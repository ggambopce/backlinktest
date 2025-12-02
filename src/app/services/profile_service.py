from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.schemas.profile import ProfileCreate
from app.models.enums import (
    HelenFisherType,
    HELEN_LABEL_KO,
    EnneagramCoreType,
    ENNEAGRAM_LABEL_KO,
)
from app.services.report_service import (
    build_profile_labels,
    build_personal_report,
)

def create_profile_with_survey(db: Session, payload: ProfileCreate) -> Profile:
    # 설문 값 추출
    q1 = payload.q1  # 헬렌 코드 (1~4)
    q2 = payload.q2  # 성숙도 (1~3)
    q3 = payload.q3  # 본능 (1~3)
    q4 = payload.q4  # 에니어그램 핵심 유형 (1~9)

    # 1) 기질/에니어그램 라벨 생성 (temperament, enneagram 컬럼용)
    temperament_text, enneagram_text = build_profile_labels(
        helen_code=q1,
        enneagram_core_type=q4,
    )

    # 2) personal_report 생성 (1단락: 헬렌, 2단락: 에니어그램)
    personal_report = build_personal_report(
        helen_code=q1,
        enneagram_core_type=q4,
    )

    # 3) Profile 엔티티 생성
    profile = Profile(
        user_id=payload.user_id,
        profile_image_url=payload.profile_image_url,
        introduction=payload.introduction,
        job=payload.job,
        birth_date=payload.birth_date,
        gender=payload.gender,
        location=payload.location,
        sns_url=payload.sns_url,
        phone_number=payload.phone_number,

        temperament=temperament_text,
        enneagram=enneagram_text,
        personal_report=personal_report,

        helen_code=q1,
        enneagram_maturity=q2,
        enneagram_instinct=q3,
        enneagram_core_type=q4,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile
