import hashlib


def assign_variant(user_id: str, experiment_id: str, variants: list[str]) -> str:
    """
    Deterministic hash-based assignment ensures:
    1. Same user always gets same variant
    2. Even distribution across variants
    3. No DB lookup needed at assignment time
    """
    hash_input = f"{experiment_id}:{user_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    bucket = hash_value % 100
    split_points = [100 // len(variants) * (i + 1) for i in range(len(variants) - 1)]

    for i, point in enumerate(split_points):
        if bucket < point:
            return variants[i]
    return variants[-1]
