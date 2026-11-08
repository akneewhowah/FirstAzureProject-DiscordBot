"""Pure, independently testable virtual-credit game logic (no real money)."""
import secrets

STARTING_BALANCE = 100
MAX_BET = 100
SIDES = ("heads", "tails")


def coinflip(balance: int, amount: int, choice: str, *, outcome: str | None = None) -> dict:
    """Return a coinflip result without reading or writing any cloud data.

    `outcome` is injectable for repeatable unit tests; omit it in production.
    """
    if type(balance) is not int or balance < 0:
        raise ValueError("Balance must be a nonnegative whole number.")
    if type(amount) is not int or not 1 <= amount <= MAX_BET:
        raise ValueError(f"Wager must be between 1 and {MAX_BET} credits.")
    if amount > balance:
        raise ValueError(f"Not enough credits. Current balance: {balance}.")
    if choice not in SIDES:
        raise ValueError("Choose heads or tails.")

    if outcome is None:
        outcome = SIDES[secrets.randbelow(2)]
    elif outcome not in SIDES:
        raise ValueError("Invalid test outcome.")

    won = choice == outcome
    return {
        "outcome": outcome,
        "won": won,
        "amount": amount,
        "new_balance": balance + amount if won else balance - amount,
    }
