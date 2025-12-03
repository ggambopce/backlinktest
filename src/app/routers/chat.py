from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    status,
    WebSocket,
    WebSocketDisconnect,
    Query,
)
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.security import get_current_user  # HTTP용 인증
from app.schemas.auth import CurrentUser
from app.schemas.profile import ApiResponse

from app.models.match import MatchResult
from app.models.user import User
from app.models.enums import MatchStatus

from app.core.redis_client import get_redis
from app.schemas.chat import ChatRoomResponse, ChatAcceptRequest
from app.services.chat_service import (
    get_active_chat_room,
    update_chat_accept,
    save_chat_message,
    load_recent_messages,
)

# HTTP용 라우터 (REST)
router = APIRouter(
    prefix="/api/profile/match",
    tags=["match-chat"],
)

# =========================
# 1) 현재 활성 채팅방 조회
#    GET /api/profile/match/chat-room
# =========================

@router.get(
    "/chat-room",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def get_active_chat_room_api(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    앱 실행 시 '현재 대화 중인 방이 있는지' 체크.
    - MatchStatus.CHAT_ACTIVE
    - chat_expires_at > now
    기준으로 조회한다.
    """
    user_id = current_user.user_id

    match = get_active_chat_room(db, user_id)

    if not match:
        # 활성 채팅방 없음
        empty = ChatRoomResponse(
            hasActiveChat=False,
            chatRoomId=None,
            matchId=None,
            partnerNickname=None,
            chatExpiresAt=None,
        )
        return ApiResponse(
            code=200,
            message="채팅방 정보 조회 성공",
            result=empty,
        )

    # 상대 프로필 닉네임
    if match.user_a_id == user_id:
        partner_profile = match.user_b.profile
    else:
        partner_profile = match.user_a.profile

    partner_nickname = (
        partner_profile.nickname if partner_profile else None
    )

    data = ChatRoomResponse(
        hasActiveChat=True,
        chatRoomId=match.chat_room_id,
        matchId=match.id,
        partnerNickname=partner_nickname,
        chatExpiresAt=match.chat_expires_at,
    )

    return ApiResponse(
        code=200,
        message="채팅방 정보 조회 성공",
        result=data,
    )


# =========================
# 2) 채팅 수락 상태 변경
#    POST /api/profile/match/accept/chat
# =========================

@router.post(
    "/accept/chat",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def accept_chat_api(
    payload: ChatAcceptRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    채팅 전, 채팅 수락/거절 상태 변경.
    - 둘 다 accept=True:
        - MatchStatus.CHAT_ACTIVE
        - chat_room_id 발급
        - chat_expires_at = now + 12h
        - 두 User.is_in_chat = True
    - 한 명만 True: CHAT_PENDING
    - 둘 다 False: MATCHED (필요하면 CANCELED 등으로 확장 가능)
    """
    user_id = current_user.user_id

    match = db.get(MatchResult, payload.matchId)
    if not match:
        raise Exception("매칭 정보를 찾을 수 없습니다.")

    if user_id not in (match.user_a_id, match.user_b_id):
        raise Exception("해당 매칭에 대한 권한이 없습니다.")

    # 허용되는 상태에서만 수락 변경
    if match.status not in (
        MatchStatus.MATCHED,
        MatchStatus.CHAT_PENDING,
        MatchStatus.CHAT_ACTIVE,
    ):
        raise Exception("현재 상태에서는 채팅 수락을 변경할 수 없습니다.")

    update_chat_accept(db, match, user_id, payload.accept)

    return ApiResponse(
        code=200,
        message="채팅 수락 상태 변경 성공",
        result=None,
    )


# =========================
# 3) WebSocket 채팅
#    WS /ws/chat/{chatRoomId}
# =========================
# WebSocket은 prefix 없이 app 레벨에 붙이는 게 일반적이어서
# 아래처럼 별도 router_ws 를 두고 main.py 에서 include_router 할 때
# prefix를 주지 않는 패턴을 사용하면 된다.

ws_router = APIRouter(tags=["match-chat-ws"])


# ---- JWT 토큰에서 user_id 추출 헬퍼 (프로젝트 구조에 맞게 수정해서 써라) ----
from jose import jwt, JWTError  # auth에서 이미 쓰고 있다면 중복 제거 가능

# 실제 서비스에선 settings 에서 가져오도록 수정
JWT_SECRET = "CHANGE_ME_TO_REAL_SECRET"
JWT_ALGORITHM = "HS256"


def _decode_user_id_from_token(token: str) -> Optional[int]:
    """
    WebSocket 연결 시 query param 으로 받은 JWT에서 user_id만 추출.
    실제 JWT 페이로드 구조에 맞게 필드명 수정해서 쓰면 된다.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")  # 예: {"user_id": 123, ...}
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None
    except (TypeError, ValueError):
        return None


@ws_router.websocket("/ws/chat/{chatRoomId}")
async def websocket_chat(
    websocket: WebSocket,
    chatRoomId: str,
    token: str = Query(..., description="JWT access token"),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    - 클라이언트는 ws 연결 시:  ws://.../ws/chat/{chatRoomId}?token=JWT  형태로 접속.
    - chatRoomId 유효성, 만료 시간, 참여 권한 검증.
    - 접속 시 최근 메시지(최대 50개) history 내려주고,
      이후 들어오는 메시지는 Redis에 12시간 TTL로 저장.
    """
    await websocket.accept()

    # 1) 토큰 검증 및 user_id 추출
    user_id = _decode_user_id_from_token(token)
    if not user_id:
        await websocket.send_json(
            {"code": 401, "message": "인증 실패", "result": None}
        )
        await websocket.close(code=4401)
        return

    # 2) chatRoomId → MatchResult 확인
    match: Optional[MatchResult] = (
        db.query(MatchResult)
        .filter(MatchResult.chat_room_id == chatRoomId)
        .first()
    )

    if not match:
        await websocket.send_json(
            {"code": 400, "message": "유효하지 않은 채팅방입니다.", "result": None}
        )
        await websocket.close(code=4404)
        return

    # 참여 권한 체크
    if user_id not in (match.user_a_id, match.user_b_id):
        await websocket.send_json(
            {"code": 403, "message": "이 채팅방에 참여할 수 없습니다.", "result": None}
        )
        await websocket.close(code=4403)
        return

    # 3) 채팅 만료 체크
    now = datetime.now(timezone.utc)
    if not match.chat_expires_at or match.chat_expires_at <= now:
        await websocket.send_json(
            {"code": 400, "message": "만료된 채팅방입니다.", "result": None}
        )
        await websocket.close(code=4402)
        return

    # 4) 최근 메시지 history 로딩 (옵션)
    recent_messages = await load_recent_messages(redis, chatRoomId, limit=50)

    await websocket.send_json(
        {
            "code": 200,
            "message": "채팅 활성화 성공",
            "result": {
                "history": recent_messages,
            },
        }
    )

    # 5) 채팅 루프
    try:
        while True:
            text = await websocket.receive_text()

            # Redis 에 메시지 저장 (12시간 TTL)
            await save_chat_message(
                redis=redis,
                chat_room_id=chatRoomId,
                sender_id=user_id,
                message=text,
            )

            # 지금은 단일 연결 기준 echo 예시.
            # 추후 여러 클라이언트 브로드캐스트 구조로 확장 가능.
            await websocket.send_text(text)

    except WebSocketDisconnect:
        # 연결 끊겼을 때 정리 로직이 필요하면 여기에 추가
        pass
