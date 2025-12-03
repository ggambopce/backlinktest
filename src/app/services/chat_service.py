from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from redis.asyncio import Redis
import json

from app.models.match import MatchResult
from app.models.user import User
from app.models.enums import MatchStatus


# --------------------------
# 공통: MatchResult / 채팅 상태 관련
# --------------------------

def get_active_chat_room(db: Session, user_id: int):
    now = datetime.now(timezone.utc)

    match = (
        db.query(MatchResult)
        .filter(
            (MatchResult.user_a_id == user_id)
            | (MatchResult.user_b_id == user_id),
            MatchResult.status == MatchStatus.CHAT_ACTIVE,
            MatchResult.chat_expires_at != None,  # noqa
            MatchResult.chat_expires_at > now,
        )
        .order_by(MatchResult.created_at.desc())
        .first()
    )
    return match


def update_chat_accept(db: Session, match: MatchResult, user_id: int, accept: bool):
    now = datetime.now(timezone.utc)
    is_me_a = (user_id == match.user_a_id)

    # 내 수락 상태 반영
    if is_me_a:
        match.is_chat_accepted_by_a = accept
    else:
        match.is_chat_accepted_by_b = accept

    # 둘 다 True → CHAT_ACTIVE
    if match.is_chat_accepted_by_a and match.is_chat_accepted_by_b:
        match.status = MatchStatus.CHAT_ACTIVE

        # 채팅방 생성
        if not match.chat_room_id:
            import uuid
            match.chat_room_id = f"room-{uuid.uuid4().hex[:10]}"

        # 12시간 유효
        match.chat_expires_at = now + timedelta(hours=12)

        # user.is_in_chat = True
        user_a = db.get(User, match.user_a_id)
        user_b = db.get(User, match.user_b_id)
        if user_a:
            user_a.is_in_chat = True
        if user_b:
            user_b.is_in_chat = True

    else:
        # 한 명만 True → CHAT_PENDING
        if match.is_chat_accepted_by_a or match.is_chat_accepted_by_b:
            match.status = MatchStatus.CHAT_PENDING
            match.chat_room_id = None
            match.chat_expires_at = None
        else:
            # 둘다 False → MATCHED
            match.status = MatchStatus.MATCHED
            match.chat_room_id = None
            match.chat_expires_at = None

            user_a = db.get(User, match.user_a_id)
            user_b = db.get(User, match.user_b_id)
            if user_a:
                user_a.is_in_chat = False
            if user_b:
                user_b.is_in_chat = False

    db.commit()
    db.refresh(match)
    return match


# --------------------------
# Redis 기반 채팅 메시지 임시 저장
# --------------------------

def _room_messages_key(chat_room_id: str) -> str:
    return f"chat:room:{chat_room_id}:messages"


async def save_chat_message(
    redis: Redis,
    chat_room_id: str,
    sender_id: int,
    message: str,
):
    """
    12시간 TTL을 가지는 Redis 리스트에 메시지 저장.
    """
    key = _room_messages_key(chat_room_id)

    payload = {
        "senderId": sender_id,
        "message": message,
        "createdAt": datetime.utcnow().isoformat(),
    }

    # 뒤에 append
    await redis.rpush(key, json.dumps(payload))

    # TTL 12시간
    await redis.expire(key, 60 * 60 * 12)


async def load_recent_messages(
    redis: Redis,
    chat_room_id: str,
    limit: int = 50,
):
    """
    최근 N개 메시지 로드 (옵션, 필요하면 사용)
    """
    key = _room_messages_key(chat_room_id)

    # 리스트 길이를 모른다고 가정하고, 뒤에서부터 최대 limit개
    # -limit ~ -1
    values = await redis.lrange(key, -limit, -1)

    messages = []
    for v in values:
        try:
            messages.append(json.loads(v))
        except Exception:
            # 파싱 실패하면 그냥 무시
            continue
    return messages
