from langchain_core.tools import tool

@tool()
def add(a: float, b: float):
    """Compute the addition of the given a and b.

    Args:
        a: Number a.
        b: Number b.
    """
    return a + b
@tool()
def minus(a: float, b: float):
    """Compute the minus of the given a and b.

    Args:
        a: Number a.
        b: Number b.
    """
    return a - b
@tool()
def divide(a: float, b: float):
    """Compute the a divided by b.

    Args:
        a: Number a.
        b: Number b.
    """
    return a / b
@tool()
def multiply(a: float, b: float):
    """Compute the multiplication of the given a and b.

    Args:
        a: Number a.
        b: Number b.
    """
    return a * b