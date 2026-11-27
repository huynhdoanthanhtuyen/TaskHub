import hashlib
import json
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from app.core.constants import CACHE_KEY_PREFIX


class CacheKey:
    @staticmethod
    def _hash_params(params: dict[str, Any]) -> str:
        normalized_params = jsonable_encoder(params)

        serialized = json.dumps(
            normalized_params,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return hashlib.sha256(
            serialized.encode("utf-8"),
        ).hexdigest()

    @classmethod
    def build(
        cls,
        resource: str,
        scope: str | UUID,
        operation: str,
        **params: Any,
    ) -> str:
        params_hash = cls._hash_params(params)

        return f"{CACHE_KEY_PREFIX}:{resource}:{scope}:{operation}:{params_hash}"

    @staticmethod
    def pattern(
        resource: str,
        scope: str | UUID = "*",
        operation: str = "*",
    ) -> str:
        return f"{CACHE_KEY_PREFIX}:{resource}:{scope}:{operation}:*"
