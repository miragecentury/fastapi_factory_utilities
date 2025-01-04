"""Provides unit tests for the `example.services.books.types` module."""

from typing import cast

import pytest
from pydantic import BaseModel

from fastapi_factory_utilities.example.entities.books.types import BookName


class TestsBookName:
    """Provides unit tests for the BookName class type."""

    def test_validate(self) -> None:
        """Should validate the book name."""
        assert BookName.validate("A Book Name") == "A Book Name"

    @pytest.mark.parametrize(
        "size",
        [
            pytest.param(
                BookName.MIN_LENGTH - 1,
                id="raise_value_error_size_min",
            ),
            pytest.param(
                BookName.MAX_LENGTH + 1,
                id="raise_value_error_size_max",
            ),
        ],
    )
    def test_validate_raises_value_error(self, size: int) -> None:
        """Should raise a ValueError for an invalid book name."""
        try:
            BookName.validate("A" * size)
            assert False
        except ValueError as error:
            assert str(error) == f"Expected a string with length between 1 and 100, got {size}"

    def test_new(self) -> None:
        """Should create a new instance of BookName."""
        assert BookName("A Book Name") == "A Book Name"

    def test_usage_in_pydantic_model(self) -> None:
        """Should be used in a Pydantic model."""

        class Book(BaseModel):
            name: BookName

        book = Book(name=cast(BookName, "A Book Name"))
        assert book.name == "A Book Name"

    @pytest.mark.parametrize(
        "size",
        [
            pytest.param(
                BookName.MIN_LENGTH - 1,
                id="raise_value_error_size_min",
            ),
            pytest.param(
                BookName.MAX_LENGTH + 1,
                id="raise_value_error_size_max",
            ),
        ],
    )
    def test_usage_in_pydantic_model_raises(self, size: int) -> None:
        """Should raise a ValueError for an invalid book name in a Pydantic model."""

        class Book(BaseModel):
            name: BookName

        try:
            Book(name=cast(BookName, "A" * size))
            assert False
        except ValueError as error:
            assert str(error).startswith("1 validation error for Book")
            assert error.error_count() == 1  # type: ignore
