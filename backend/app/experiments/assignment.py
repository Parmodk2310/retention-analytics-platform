import hashlib

DEFAULT_SALT = "retention-analytics-v1"


def bucket_for(user_id: str, experiment_id: str, salt: str = DEFAULT_SALT) -> int:
    digest = hashlib.sha256(f"{salt}:{experiment_id}:{user_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 10_000


def assign_variant(user_id: str, experiment_id: str, allocations: dict[str, float]) -> str:
    bucket = bucket_for(user_id, experiment_id)
    cursor = 0
    for variant, share in allocations.items():
        cursor += round(share * 10_000)
        if bucket < cursor:
            return variant
    return next(reversed(allocations))
