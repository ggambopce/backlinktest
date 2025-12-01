from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from jose import jwt, JWTError

from app.core.config import jwt_settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _create_token(
    claims: Dict[str, Any],
    secret_key: str,
    expires_delta: timedelta,
) -> str:
    to_encode = claims.copy()
    expire = _now_utc() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        secret_key,
        algorithm=jwt_settings.algorithm,
    )


def _decode_token(token: str, secret_key: str) -> Dict[str, Any]:
    return jwt.decode(
        token,
        secret_key,
        algorithms=[jwt_settings.algorithm],
    )

def create_access_token(claims: Dict[str, Any]) -> str:
    """
    AccessToken 생성용 헬퍼
    """
    return _create_token(
        claims=claims,
        secret_key=jwt_settings.access_secret_key,
        expires_delta=jwt_settings.access_expires_delta,
    )


def create_refresh_token(claims: Dict[str, Any]) -> str:
    """
    RefreshToken 생성용 헬퍼
    """
    return _create_token(
        claims=claims,
        secret_key=jwt_settings.refresh_secret_key,
        expires_delta=jwt_settings.refresh_expires_delta,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    AccessToken 전용 디코딩. 유효하지 않으면 JWTError 발생.
    """
    return _decode_token(
        token=token,
        secret_key=jwt_settings.access_secret_key,
    )


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    RefreshToken 전용 디코딩. 유효하지 않으면 JWTError 발생.
    """
    return _decode_token(
        token=token,
        secret_key=jwt_settings.refresh_secret_key,
    )


class InvalidTokenError(Exception):
    """JWT가 유효하지 않을 때 던지는 커스텀 예외"""
    pass


def try_decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return decode_access_token(token)
    except JWTError as e:
        raise InvalidTokenError(str(e))