from fastapi import APIRouter, Depends, status
from ..schemas.profile import ApiResponse, ProfileCreate, ProfileResponse
from ..models.profile import Profile
from ..core.database import get_db
from ..services.profile_service import create_profile_with_survey
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/profile")

@router.post(
    "/create",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def create_profile(
    payload: ProfileCreate,
    db: Session = Depends(get_db)
):
    # 여기서 service 호출!
    profile = create_profile_with_survey(db, payload)

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
    db: Session = Depends(get_db)
):
    profile = db.get(Profile, profile_id)

    return ApiResponse(
        code=200,
        message="프로필 조회 성공",
        result=ProfileResponse.model_validate(profile, from_attributes=True),
    )