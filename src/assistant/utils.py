import secrets


def generate_random_hex(length: int = 32) -> str:
    """Generate a random hex string of the given length."""
    if length <= 0:
        raise ValueError("length must be positive")
    # token_hex returns 2 chars per byte; slice to requested length.
    return secrets.token_hex((length + 1) // 2)[:length]
