"""Python Factory Example."""

from fastapi_factory_utilities.example.app import AppBuilder


def main() -> None:
    """Main function."""
    AppBuilder().build_and_serve()


__all__: list[str] = ["main"]
