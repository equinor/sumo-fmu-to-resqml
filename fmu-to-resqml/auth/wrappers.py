"""
All auth wrapper functions
"""

from os import environ
from time import time

import jwt
import requests
from auth.exchange import get_bearer_token
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from flask import request

TENANT = environ.get("AZURE_TENANT_ID")
AUDIENCE = environ.get("AZURE_CLIENT_ID")
ISSUER = f"{environ.get('AZURE_AUTHORITY_HOST')}{environ.get('AZURE_TENANT_ID')}/v2.0"
ALGORITHMS = None
JWKCLIENT = None


def get_jwkclient():
    """
    Get a jwk client from jwt
    """
    global JWKCLIENT
    global ALGORITHMS
    if JWKCLIENT is None:
        well_known_uri = ISSUER + "/.well-known/openid-configuration"
        config = requests.get(well_known_uri).json()
        ALGORITHMS = config["id_token_signing_alg_values_supported"]
        jwks_uri = config["jwks_uri"]
        JWKCLIENT = jwt.PyJWKClient(jwks_uri)

    return JWKCLIENT


def get_key(token):
    """
    Get a key from the jwk client
    """
    key = get_jwkclient().get_signing_key_from_jwt(token)
    pem = (
        key.key.public_numbers()
        .public_key(default_backend())
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

    return pem


def verify_token(func: any) -> any:
    """
    Wrapper that verifies that a auth token exists and is valid
    """

    def wrapper(*args, **kwargs):
        token = get_bearer_token(request)
        try:
            key = get_key(token)
            payload = jwt.decode(
                token,
                algorithms=ALGORITHMS,
                key=key,
                audience=AUDIENCE,
                issuer=ISSUER,
            )
        except Exception as e:
            raise Exception(f"Failed to decode token: {e}", 401)

        scope = payload["scp"]
        expires = payload["exp"]

        if scope != "RESQML.Read":
            raise Exception("Token is not valid: Invalid scope", 401)

        # Verify that token expires in (at least) over 2 minutes
        if expires < time() - 120:
            raise Exception("Token is not valid: Expired token", 401)

        return func(*args, **kwargs)

    return wrapper
