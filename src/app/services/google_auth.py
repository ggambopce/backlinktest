# src/app/services/google_auth.py
import os
from fastapi import HTTPException
import httpx  # pip install httpx 필요

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")  # 있으면 aud 체크에 사용


async def verify_google_id_token(id_token: str) -> dict:
    """
    Google OAuth Playground 등에서 받은 id_token을
    구글 tokeninfo 엔드포인트로 검증하는 간단한 함수.
    """
    if not id_token:
        raise HTTPException(status_code=400, detail="idToken이 비어 있습니다.")

    # 구글 검증 엔드포인트 호출
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=5.0,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="유효하지 않은 Google ID Token")

    data = resp.json()

    # aud(클라이언트 ID) 검증 (환경변수 설정했을 때만)
    if GOOGLE_CLIENT_ID and data.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="잘못된 클라이언트 ID(aud)")

    # 여기서 email_verified 같은 것도 체크할 수 있음
    return data
