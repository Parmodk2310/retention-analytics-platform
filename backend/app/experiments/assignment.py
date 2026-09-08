import hashlib
import math
import re
from collections.abc import Mapping, Sequence

DEFAULT_SALT = "retention-analytics-v1"
BUCKET_COUNT = 10_000
ALLOCATION_TOLERANCE = 1e-9
VARIANT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")


def validate_assignment_contract(
    variants: Sequence[str],
    allocations: Mapping[str, float],
) -> None:
    variants = list(variants)

    if not 2 <= len(variants) <= 5:
        raise ValueError("experiments require between 2 and 5 variants")
    if len(set(variants)) != len(variants):
        raise ValueError("variant names must be unique")
    if any(not VARIANT_PATTERN.fullmatch(v) for v in variants):
        raise ValueError("invalid variant name")
    if set(variants) != set(allocations):
        raise ValueError("allocation keys must match variants")

    shares = [float(allocations[v]) for v in variants]

    if any(not math.isfinite(x) or x <= 0 or x > 1 for x in shares):
        raise ValueError("traffic allocation values must be between 0 and 1")
    if not math.isclose(
        math.fsum(shares),
        1.0,
        rel_tol=0.0,
        abs_tol=ALLOCATION_TOLERANCE,
    ):
        raise ValueError("traffic allocation must sum to 1")


def bucket_for(
    user_id: str,
    experiment_id: str,
    salt: str = DEFAULT_SALT,
) -> int:
    value = f"{salt}:{experiment_id}:{user_id}".encode()
    digest = hashlib.sha256(value).digest()
    return int.from_bytes(digest[:8], "big") % BUCKET_COUNT


def assign_variant(
    user_id: str,
    experiment_id: str,
    allocations: Mapping[str, float],
    *,
    variants: Sequence[str] | None = None,
    salt: str = DEFAULT_SALT,
) -> str:
    order = list(variants) if variants is not None else sorted(allocations)
    validate_assignment_contract(order, allocations)

    bucket = bucket_for(user_id, experiment_id, salt)
    cumulative = 0.0

    for index, variant in enumerate(order):
        if index == len(order) - 1:
            return variant

        cumulative += float(allocations[variant])
        if bucket < round(cumulative * BUCKET_COUNT):
            return variant

    raise RuntimeError("unable to resolve experiment variant")
