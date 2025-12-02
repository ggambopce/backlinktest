from fastapi import APIRouter, Depends, status
from ..schemas.profile import ApiResponse, ProfileCreate, ProfileResponse
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