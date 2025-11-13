from fastapi import APIRouter, Depends, status
from ..schemas.profile import ApiResponse, ProfileCreate
from ..models.profile import Profile
from ..core.database import get_db
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
    profile = Profile(
        payload.dict(exclude_unset=True),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return ApiResponse(
        code=200,
        message="프로필 작성 성공",
        result=profile,
    )

@router.get(
    "/get",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
)
def get_profile(
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).all()
    return ApiResponse(
        code=200,
        message="프로필 조회 성공",
        result=profile,
    )