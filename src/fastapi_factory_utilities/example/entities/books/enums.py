"""Provides enums for the books service."""

from enum import StrEnum, auto


class BookType(StrEnum):
    """Enumeration of book types."""

    SCIENCE_FICTION = auto()
    FANTASY = auto()
    MYSTERY = auto()
    ROMANCE = auto()
    THRILLER = auto()
    HORROR = auto()
    HISTORICAL_FICTION = auto()
    ADVENTURE = auto()
