# app/services/match_service.py
from typing import TypedDict, List, Tuple, Set
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.profile import Profile
from app.models.match import MatchResult
from app.models.enums import MatchStatus

from app.services.report_service import build_compatibility_report_from_profiles


class MatchScoreDetail(TypedDict):
    total: int
    q1: int
    q2: int
    q3: int
    q4: int


def _score_q1(n1: int, n2: int) -> int:
    """
    q1 (헬렌 기질) 점수 계산
    25점: 1-1, 2-2, 3-4, 4-3
    20점: 그 외
    """
    pair = (n1, n2)
    if pair in {(1, 1), (2, 2), (3, 4), (4, 3)}:
        return 25
    return 20


def _score_q2(n1: int, n2: int) -> int:
    """
    q2 (성숙도) 점수 계산
    25점: n1 - n2 = 0
    20점: |n1 - n2| = 1
    15점: |n1 - n2| = 2
    (입력 범위: 1~3 가정)
    """
    diff = abs(n1 - n2)
    if diff == 0:
        return 25
    elif diff == 1:
        return 20
    elif diff == 2:
        return 15
    # 이론상 diff는 0~2 범위라 여기까지 안 온다.
    return 0


def _score_q3(n1: int, n2: int) -> int:
    """
    q3 (본능) 점수 계산
    25점: n1 - n2 = 0
    20점: 그 외
    """
    if n1 == n2:
        return 25
    return 20


def _score_q4(n1: int, n2: int) -> int:
    """
    q4 (핵심유형) 점수 계산
    25점: n1 + n2 = 10
    20점: 그 외
    """
    if n1 + n2 == 10:
        return 25
    return 20


def compute_match_score_from_codes(
    *,
    q1_a: int,
    q2_a: int,
    q3_a: int,
    q4_a: int,
    q1_b: int,
    q2_b: int,
    q3_b: int,
    q4_b: int,
) -> MatchScoreDetail:
    """
    헬렌 기질/에니어그램 코드 숫자만으로 점수 계산.
    """
    s1 = _score_q1(q1_a, q1_b)
    s2 = _score_q2(q2_a, q2_b)
    s3 = _score_q3(q3_a, q3_b)
    s4 = _score_q4(q4_a, q4_b)

    total = s1 + s2 + s3 + s4

    return MatchScoreDetail(
        total=total,
        q1=s1,
        q2=s2,
        q3=s3,
        q4=s4,
    )

def compute_match_score_from_profiles(
    profile_a: Profile,
    profile_b: Profile,
) -> MatchScoreDetail:
    """
    Profile 엔티티에 이미 저장된 코드값(helen_code, enneagram_*) 기반으로 계산.
    """
    return compute_match_score_from_codes(
        q1_a=profile_a.helen_code,
        q2_a=profile_a.enneagram_maturity,
        q3_a=profile_a.enneagram_instinct,
        q4_a=profile_a.enneagram_core_type,
        q1_b=profile_b.helen_code,
        q2_b=profile_b.enneagram_maturity,
        q3_b=profile_b.enneagram_instinct,
        q4_b=profile_b.enneagram_core_type,
    )

def create_match_result(
    db: Session,
    profile_a: Profile,
    profile_b: Profile,
) -> MatchResult:
    scores = compute_match_score_from_profiles(profile_a, profile_b)
    report = build_compatibility_report_from_profiles(profile_a, profile_b)

    match = MatchResult(
        user_a_id=profile_a.user_id,
        user_b_id=profile_b.user_id,
        compatibility_score=scores["total"],
        compatibility_report=report,
        status=MatchStatus.MATCHED,
    )

    db.add(match)
    db.commit()
    db.refresh(match)
    return match

def _pair_key(a_id: int, b_id: int) -> tuple[int, int]:
    """
    (a,b) / (b,a)를 동일한 조합으로 보기 위한 정규화 키
    """
    return (min(a_id, b_id), max(a_id, b_id))


def create_daily_match_results_by_best_score(db: Session) -> list[MatchResult]:
    """
    매일 0시에 스케줄러가 호출할 매칭 생성 함수.

    - 대상:
      - 채팅중이 아닌 유저
    - 과거에 한 번이라도 매칭된 (A,B) 조합은 제외
    - 점수 내림차순으로 정렬
    - 한 사람이 하루에 한 번만 매칭되도록 greedy하게 짝을 짓고
    - status = MATCHED 인 MatchResult를 생성

    리턴: 생성된 MatchResult 리스트
    """
    # 매칭 가능한 유저 + 프로필 조회
    eligible_users: list[User] = (
        db.query(User)
        .join(Profile, Profile.user_id == User.id)
        .filter(
            User.is_in_chat.is_(False),
        )
        .all()
    )

    if len(eligible_users) < 2:
        return []

    profiles_by_user_id: dict[int, Profile] = {
        u.id: u.profile for u in eligible_users
    }

    user_ids = list(profiles_by_user_id.keys())

    # 2) 과거 매칭 조합 수집 (한 번 매칭된 사람끼리는 다시 매칭되면 안 됨)
    existing_pairs: Set[tuple[int, int]] = set()

    past_matches = db.query(MatchResult.user_a_id, MatchResult.user_b_id).all()
    for a_id, b_id in past_matches:
        existing_pairs.add(_pair_key(a_id, b_id))

    # 3) 모든 가능한 (A,B) 쌍에 대해 점수 계산 (과거 조합 제외)
    candidate_pairs: list[tuple[int, Profile, Profile]] = []

    n = len(user_ids)
    for i in range(n):
        for j in range(i + 1, n):
            ua = user_ids[i]
            ub = user_ids[j]

            if _pair_key(ua, ub) in existing_pairs:
                continue

            p_a = profiles_by_user_id.get(ua)
            p_b = profiles_by_user_id.get(ub)
            if not p_a or not p_b:
                continue

            scores = compute_match_score_from_profiles(p_a, p_b)
            total_score = scores["total"]

            candidate_pairs.append((total_score, p_a, p_b))

    if not candidate_pairs:
        return []

    # 4) 점수 내림차순 정렬
    candidate_pairs.sort(key=lambda x: x[0], reverse=True)

    # 5) greedy 매칭: 한 번 매칭된 user_id는 더 이상 사용하지 않음
    matched_user_ids: set[int] = set()
    created_matches: list[MatchResult] = []
    now = datetime.utcnow()

    for total_score, p_a, p_b in candidate_pairs:
        if p_a.user_id in matched_user_ids or p_b.user_id in matched_user_ids:
            continue

        # 아직 매칭 안 된 두 명이면 MatchResult 생성
        match = MatchResult(
            user_a_id=p_a.user_id,
            user_b_id=p_b.user_id,
            compatibility_score=total_score,
            status=MatchStatus.MATCHED,
            created_at=now,
            # 채팅/공개 관련 필드는 아직 False/None
        )
        db.add(match)
        created_matches.append(match)

        matched_user_ids.add(p_a.user_id)
        matched_user_ids.add(p_b.user_id)

    db.commit()

    for m in created_matches:
        db.refresh(m)

    return created_matches