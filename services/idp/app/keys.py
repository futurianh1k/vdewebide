from dataclasses import dataclass
import hashlib
import json
from typing import Dict, Any

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass(frozen=True)
class KeyPair:
    kid: str
    private_key: rsa.RSAPrivateKey


_KEYPAIR: KeyPair | None = None


def get_keypair() -> KeyPair:
    global _KEYPAIR
    if _KEYPAIR is not None:
        return _KEYPAIR

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    jwk_pub_json = jwt.algorithms.RSAAlgorithm.to_jwk(public_key)
    kid = "kid-" + hashlib.sha256(jwk_pub_json.encode("utf-8")).hexdigest()[:16]

    _KEYPAIR = KeyPair(kid=kid, private_key=private_key)
    return _KEYPAIR


def jwks_public() -> Dict[str, Any]:
    kp = get_keypair()
    public_key = kp.private_key.public_key()
    jwk_pub_json = jwt.algorithms.RSAAlgorithm.to_jwk(public_key)
    jwk = json.loads(jwk_pub_json)
    jwk["kid"] = kp.kid
    jwk["use"] = "sig"
    jwk["alg"] = "RS256"
    return {"keys": [jwk]}

