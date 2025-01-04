"""Python Factory Example."""

from fastapi_factory_utilities.example.app import App


def main() -> None:
    """Main function."""
    App.main()


__all__: list[str] = ["App", "main"]
