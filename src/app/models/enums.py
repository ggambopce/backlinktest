# src/app/models/enums.py
from enum import IntEnum


class HelenFisherType(IntEnum):
    """
    헬렌 피셔 기질 코드 (질문지 1번)
    1: Explorer (탐험가)
    2: Builder (건축가)
    3: Negotiator (협상가)
    4: Director (감독자)
    """
    EXPLORER = 1     # 탐험가형
    BUILDER = 2      # 건축가형
    NEGOTIATOR = 3   # 협상가형
    DIRECTOR = 4     # 감독자형


HELEN_LABEL_KO = {
    HelenFisherType.EXPLORER: "Explorer 탐험가",
    HelenFisherType.BUILDER: "Builder 건축가",
    HelenFisherType.NEGOTIATOR: "Negotiator 협상가",
    HelenFisherType.DIRECTOR: "Director 감독자",
}


class EnneagramCoreType(IntEnum):
    """
    에니어그램 핵심 유형 (질문지 4번)
    1~9: 1번~9번
    """
    ONE = 1   # 1번 (완벽주의자)
    TWO = 2   # 2번 (조력가)
    THREE = 3 # 3번 (성취자)
    FOUR = 4  # 4번 (낭만가)
    FIVE = 5  # 5번 (탐구자)
    SIX = 6   # 6번 (충성가)
    SEVEN = 7 # 7번 (낙천가)
    EIGHT = 8 # 8번 (보호자)
    NINE = 9  # 9번 (중재자)


ENNEAGRAM_LABEL_KO = {
    EnneagramCoreType.ONE:   "1번 완벽주의자",
    EnneagramCoreType.TWO:   "2번 조력가",
    EnneagramCoreType.THREE: "3번 성취자",
    EnneagramCoreType.FOUR:  "4번 낭만가",
    EnneagramCoreType.FIVE:  "5번 탐구자",
    EnneagramCoreType.SIX:   "6번 충성가",
    EnneagramCoreType.SEVEN: "7번 낙천가",
    EnneagramCoreType.EIGHT: "8번 보호자",
    EnneagramCoreType.NINE:  "9번 중재자",
}
