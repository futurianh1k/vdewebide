from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
import time

import jwt

from .keys import get_keypair, jwks_public


app = FastAPI(title="Mock IdP (SSO/JWT)", version="0.1.0")


class TokenRequest(BaseModel):
    sub: str = Field(default="dev-user", min_length=1, max_length=80)
    tid: str = Field(default="dev-tenant", min_length=1, max_length=80)
    pid: str = Field(default="dev-project", min_length=1, max_length=80)
    wid: str = Field(default="dev-workspace", min_length=1, max_length=80)
    role: str = Field(default="developer", min_length=1, max_length=40)
    aud: str = Field(default="vde-gateway", min_length=1, max_length=120)
    iss: str = Field(default="vde-idp", min_length=1, max_length=200)
    expires_in: int = Field(default=3600, ge=60, le=86400)
    extra: Optional[dict] = None


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/.well-known/jwks.json")
def well_known_jwks():
    return jwks_public()


@app.post("/token")
def issue_token(req: TokenRequest):
    """
    Mock access token 발급 엔드포인트.
    - 운영 환경의 실제 SSO/OIDC와 동일한 계약을 목표로 하지 않고,
      Gateway의 JWKS 기반 JWT 검증을 독립형으로 테스트하기 위한 목적이다.
    """
    kp = get_keypair()
    now = int(time.time())

    claims = {
        "sub": req.sub,
        "tid": req.tid,
        "pid": req.pid,
        "wid": req.wid,
        "role": req.role,
        "iss": req.iss,
        "aud": req.aud,
        "iat": now,
        "exp": now + int(req.expires_in),
    }
    if req.extra:
        # mock용: 추가 claim 주입
        claims.update(req.extra)

    token = jwt.encode(
        claims,
        kp.private_key,
        algorithm="RS256",
        headers={"kid": kp.kid, "typ": "JWT"},
    )
    return {"access_token": token, "token_type": "Bearer", "expires_in": int(req.expires_in)}

