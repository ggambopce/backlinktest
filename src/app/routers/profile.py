from fastapi import APIRouter, Depends, status
from ..schemas.profile import ApiResponse, ProfileCreate, ProfileResponse, MatchOfferProfileResponse
from ..models.profile import Profile
from ..core.database import get_db
from ..services.profile_service import create_profile_with_survey
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser


router = APIRouter(prefix="/api/profile")

@router.post(
    "/create",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def create_profile(
    payload: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.user_id  # JWT에서 가져온 user_id
    # service 호출
    profile = create_profile_with_survey(db, payload, user_id)

    return ApiResponse(
        code=200,
        message="프로필 작성 성공",
        result=ProfileResponse.model_validate(profile).model_dump(),
    )


@router.get(
    "/{profile_id}",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    profile = db.get(Profile, profile_id)

    if not profile:
        raise Exception("프로필을 찾을 수 없음")

    if profile.user_id != current_user.user_id:
        raise Exception("본인 프로필만 조회할 수 있음")

    return ApiResponse(
        code=200,
        message="프로필 조회 성공",
        result=ProfileResponse.model_validate(profile, from_attributes=True),
    )


@router.get(
    "/result/offer",
    response_model=ApiResponse[MatchOfferProfileResponse],
    status_code=status.HTTP_200_OK,
)
def get_match_offer(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.user_id

    # 1) 오늘자 매칭 결과 가져오기 (예시)
    match = (
        db.query(MatchResult)
        .filter(
            MatchResult.user_a_id == user_id
            | MatchResult.user_b_id == user_id,
            # 날짜 조건, 상태 조건 등 필요한 필터 추가
        )
        .first()
    )
    if not match:
        # 매칭 없을 때 result를 None으로 반환할 수도 있고, 
        # 404/400으로 처리할 수도 있음. 네 정책에 맞게.
        return ApiResponse[MatchOfferProfileResponse](
            code=200,
            message="매칭 결과가 없습니다.",
            result=None,
        )

    # 2) 상대 프로필 선택
    if match.user_a_id == user_id:
        partner_profile = match.user_b.profile
    else:
        partner_profile = match.user_a.profile

    # 3) DTO로 매핑
    dto = MatchOfferProfileResponse(
        profile_image_url=partner_profile.profile_image_url,
        introduction=partner_profile.introduction,
        job=partner_profile.job,
        birth_date=partner_profile.birth_date,
        gender=partner_profile.gender,
        location=partner_profile.location,
        temperament=partner_profile.temperament,
        enneagram=partner_profile.enneagram,
        personal_report=partner_profile.personal_report,
    )

    return ApiResponse[MatchOfferProfileResponse](
        code=200,
        message="매칭 상대 프로필 조회 성공",
        result=dto,
    )