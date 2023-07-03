# Deprecation warning decorator
from warnings import warn

def deprecated(func) -> None:
    warn(f"Function {func.__name__} is deprecated.")
    return func