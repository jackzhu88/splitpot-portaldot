"""Pure split math for SplitPot (no chain access), so it can be unit-tested."""
from decimal import Decimal, InvalidOperation


def parse_shares(text):
    """Parse '50,30,20' into [50, 30, 20]; shares must be positive ints summing to 100."""
    try:
        shares = [int(x) for x in str(text).split(",") if x.strip()]
    except ValueError:
        raise ValueError(f"shares must be integers, got {text!r}")
    if len(shares) < 2:
        raise ValueError("need at least 2 payees")
    if any(s <= 0 for s in shares):
        raise ValueError("every share must be > 0")
    if sum(shares) != 100:
        raise ValueError(f"shares must sum to 100, got {sum(shares)}")
    return shares


def to_planck(total, decimals):
    """Convert a decimal token amount string to integer planck without float error."""
    try:
        d = Decimal(str(total))
    except InvalidOperation:
        raise ValueError(f"amount must be a number, got {total!r}")
    if d <= 0:
        raise ValueError("amount must be > 0")
    p = d * (Decimal(10) ** decimals)
    if p != p.to_integral_value():
        raise ValueError(f"amount has more than {decimals} decimals")
    return int(p)


def split_amounts(total_planck, shares):
    """Split by percentage; rounding dust goes to the last payee so the sum is exact."""
    amounts = [total_planck * s // 100 for s in shares]
    amounts[-1] += total_planck - sum(amounts)
    return amounts
