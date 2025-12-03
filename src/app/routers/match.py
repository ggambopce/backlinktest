from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser

from app.schemas.profile import ApiResponse
from app.models.match import MatchResult
from app.models.profile import Profile
from app.models.enums import MatchStatus

router = APIRouter(prefix="/api/profile/match")

# ---------- 공통 유틸 ----------

def _get_latest_match_for_user(db: Session, user_id: int) -> MatchResult | None:
    """
    해당 유저가 포함된 가장 최근 MatchResult 한 건 조회
    """
    return (
        db.query(MatchResult)
        .filter(
            (MatchResult.user_a_id == user_id)
            | (MatchResult.user_b_id == user_id)
        )
        .order_by(MatchResult.created_at.desc())
        .first()
    )


def _resolve_partner_profile(match: MatchResult, me_user_id: int) -> tuple[Profile, bool]:
    """
    match 안에서 내가 A인지 B인지 판별하고,
    - partner_profile
    - is_me_a (bool)
    반환
    """
    if match.user_a_id == me_user_id:
        return match.user_b.profile, True
    else:
        return match.user_a.profile, False


# ---------- 1) 매칭결과 상대 프로필 조회 ----------

@router.get(
    "/result/offer",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def get_match_offer(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    매칭 스케줄 이후 앱 실행 시, 상대 프로필(오퍼) 단건 조회
    """
    user_id = current_user.user_id

    # 현재 유저 기준 가장 최근 매칭 1건
    match = _get_latest_match_for_user(db, user_id)
    if not match:
        # 전역 예외 핸들러에서 ApiResponse로 감쌀 것으로 가정
        raise Exception("현재 매칭 상대가 없습니다.")

    # 취소된 매칭이면 오퍼로 사용하지 않음
    if match.status == MatchStatus.CANCELED:
        raise Exception("현재 유효한 매칭 오퍼가 없습니다.")

    partner_profile, _ = _resolve_partner_profile(match, user_id)

    result = {
        "profile_image_url": partner_profile.profile_image_url,
        "introduction": partner_profile.introduction,
        "job": partner_profile.job,
        "birth_date": partner_profile.birth_date,
        "gender": partner_profile.gender,
        "location": partner_profile.location,
        "temperament": partner_profile.temperament,
        "enneagram": partner_profile.enneagram,
        "personal_report": partner_profile.personal_report,
    }

    return ApiResponse(
        code=200,
        message="매칭 상대 프로필 조회 성공",
        result=result,
    )


# ---------- 2) 매칭결과 전체 상태 조회 ----------

@router.get(
    "/result",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def get_match_result(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    매칭 ~ 채팅 ~ 연락처 공개까지 전체 상태 조회
    """
    user_id = current_user.user_id

    match = _get_latest_match_for_user(db, user_id)
    if not match:
        raise Exception("매칭 상태를 찾을 수 없습니다.")

    partner_profile, is_me_a = _resolve_partner_profile(match, user_id)

    # 내 쪽/상대 쪽 플래그 분리
    if is_me_a:
        is_chat_accepted_by_me = match.is_chat_accepted_by_a
        is_chat_accepted_by_partner = match.is_chat_accepted_by_b
        is_contact_accepted_by_me = match.is_contact_shared_by_a
        is_contact_accepted_by_partner = match.is_contact_shared_by_b
    else:
        is_chat_accepted_by_me = match.is_chat_accepted_by_b
        is_chat_accepted_by_partner = match.is_chat_accepted_by_a
        is_contact_accepted_by_me = match.is_contact_shared_by_b
        is_contact_accepted_by_partner = match.is_contact_shared_by_a

    result = {
        "matchId": match.id,
        "status": match.status.value,
        "compatibilityScore": match.compatibility_score,
        "compatibilityReport": match.compatibility_report,
        "userA": {
            "userId": match.user_a_id,
            # 프로필에 nickname 필드가 있다고 가정
            "nickname": match.user_a.profile.nickname if match.user_a.profile else None,
        },
        "userB": {
            "userId": match.user_b_id,
            "nickname": match.user_b.profile.nickname if match.user_b.profile else None,
        },
        "isChatAcceptedByMe": is_chat_accepted_by_me,
        "isChatAcceptedByPartner": is_chat_accepted_by_partner,
        "isContactAcceptedByMe": is_contact_accepted_by_me,
        "isContactAcceptedByPartner": is_contact_accepted_by_partner,
        "chatRoomId": match.chat_room_id,
        "chatExpiresAt": match.chat_expires_at,
    }

    return ApiResponse(
        code=200,
        message="매칭 상태 조회 성공",
        result=result,
    )


# ---------- 3) 최종정보 공개 동의 ----------

class ContactAcceptRequest(BaseModel):
    matchId: int
    accept: bool


@router.post(
    "/accept/contact",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def accept_contact_share(
    payload: ContactAcceptRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    최종정보 공개(연락처 공개) 동의/철회
    """
    user_id = current_user.user_id

    match = db.get(MatchResult, payload.matchId)
    if not match:
        raise Exception("매칭 정보를 찾을 수 없습니다.")

    if user_id not in (match.user_a_id, match.user_b_id):
        raise Exception("해당 매칭에 대한 권한이 없습니다.")

    is_me_a = (user_id == match.user_a_id)

    if is_me_a:
        match.is_contact_shared_by_a = payload.accept
    else:
        match.is_contact_shared_by_b = payload.accept

    db.commit()
    db.refresh(match)

    return ApiResponse(
        code=200,
        message="최종 정보 공개 동의 성공",
        result=None,
    )


# ---------- 4) 최종정보 공개 조회 ----------

@router.get(
    "/final",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def get_final_contact_info(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    최종 정보(연락처) 조회
    - 양쪽 모두 is_contact_shared_by_* 가 True 일 때만 조회 가능
    """
    user_id = current_user.user_id

    match = _get_latest_match_for_user(db, user_id)
    if not match:
        raise Exception("매칭 정보를 찾을 수 없습니다.")

    # 양쪽 모두 동의해야만 최종 정보 조회 허용
    if not (match.is_contact_shared_by_a and match.is_contact_shared_by_b):
        raise Exception("아직 양쪽 모두 최종 정보 공개에 동의하지 않았습니다.")

    partner_profile, _ = _resolve_partner_profile(match, user_id)

    result = {
        "sns_url": partner_profile.sns_url,
        "phone_number": partner_profile.phone_number,
    }

    return ApiResponse(
        code=200,
        message="최종 정보 조회 성공",
        result=result,
    )