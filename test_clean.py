"""Clean test file that passes ruff checks."""


def add_numbers(x: int, y: int) -> int:
    """Add two numbers together."""
    return x + y


def main() -> None:
    """Main function."""
    result = add_numbers(5, 10)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
