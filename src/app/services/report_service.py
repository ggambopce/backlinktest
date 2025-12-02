from app.models.enums import (
    HelenFisherType,
    HELEN_LABEL_KO,
    EnneagramCoreType,
    ENNEAGRAM_LABEL_KO,
)

# 1) 헬렌 피셔 4기질 설명 문구
HELEN_DESCRIPTION = {
    1: "모험과 새로움을 사랑하는 열정가, 세상 어디든 발걸음을 옮길 준비가 된 사람.",
    2: "믿음직하고 따뜻한 마음씨, 함께 있으면 늘 든든한 안정형 파트너.",
    3: "직관과 논리로 세상을 읽는 사람, 강인함 속에 숨은 섬세함까지 갖춘 매력.",
    4: "타인의 마음을 자연스럽게 읽고 감싸주는 따뜻한 감성가.",
}

# 2) 에니어그램 핵심 유형 설명 문구
ENNEAGRAM_DESCRIPTION = {
    1: "원칙과 정의를 중시하며 작은 일도 꼼꼼히 챙기는 완벽주의적 성향.",
    2: "사랑을 나누고 돌보길 좋아하는 다정한 마음씨의 도우미 성향.",
    3: "늘 도전하고 성취하며 스스로 빛을 만들어내는 목표 지향형 성취자.",
    4: "남들과는 다른 색깔과 감성으로 특별함을 표현하는 개성추구자.",
    5: "생각이 깊고 지적 탐구를 즐기는 내면 세계가 풍부한 탐구자.",
    6: "충성심 강하고 믿음직한 동반자형 충성가.",
    7: "즐거움과 모험을 찾아다니며 웃음을 퍼뜨리는 낙천적 열정가.",
    8: "단단한 카리스마와 강한 의지로 자신과 주변을 지키는 리더형 보스.",
    9: "평화와 조화를 중시하며 모두를 편안하게 만드는 중재자.",
}


def build_profile_labels(helen_code: int, enneagram_core_type: int) -> tuple[str, str]:
    """
    숫자 코드(q1, q4)를 받아서
    - temperament: 헬렌 4기질 한국어 라벨
    - enneagram: 에니어그램 핵심 유형 한국어 라벨
    을 반환.
    """
    helen_enum = HelenFisherType(helen_code)
    enneagram_enum = EnneagramCoreType(enneagram_core_type)

    temperament_text = HELEN_LABEL_KO[helen_enum]
    enneagram_text = ENNEAGRAM_LABEL_KO[enneagram_enum]

    return temperament_text, enneagram_text


def build_personal_report(helen_code: int, enneagram_core_type: int) -> str:
    """
    1단락: 헬렌 피셔 기질 설명
    2단락: 에니어그램 핵심 유형 설명
    형식으로 personal_report 텍스트를 생성.
    """
    helen_text = HELEN_DESCRIPTION.get(helen_code, "")
    enneagram_text = ENNEAGRAM_DESCRIPTION.get(enneagram_core_type, "")

    return f"{helen_text}\n\n{enneagram_text}"
