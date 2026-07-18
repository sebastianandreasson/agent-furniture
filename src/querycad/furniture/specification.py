"""Shared interface for frozen, user-facing furniture specifications."""

from __future__ import annotations

from dataclasses import asdict, fields
from typing import Any, ClassVar, Self


class FurnitureSpec:
    """Mixin that maps JSON overrides and validates common scalar fields."""

    model_name: ClassVar[str]

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> Self:
        allowed = {field.name for field in fields(cls)}
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise ValueError(f"unknown {cls.model_name} parameter(s): {', '.join(unknown)}")
        spec = cls(**values)
        spec.validate()
        return spec

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate_basics(
        self,
        *,
        text_fields: tuple[str, ...],
        non_numeric_fields: tuple[str, ...] = (),
        allow_zero: tuple[str, ...] = (),
    ) -> dict[str, int | float]:
        """Validate common text/numeric requirements and return numeric parameters."""

        values = self.as_dict()
        invalid_text = [
            name
            for name in text_fields
            if not isinstance(values[name], str) or not values[name].strip()
        ]
        if invalid_text:
            raise ValueError(f"material names must be non-empty strings: {', '.join(invalid_text)}")

        excluded = {*text_fields, *non_numeric_fields}
        numeric = {name: value for name, value in values.items() if name not in excluded}
        not_numbers = [
            name
            for name, value in numeric.items()
            if not isinstance(value, int | float) or isinstance(value, bool)
        ]
        if not_numbers:
            raise ValueError(f"parameters must be numeric: {', '.join(not_numbers)}")

        non_positive = [
            name for name, value in numeric.items() if value <= 0 and name not in allow_zero
        ]
        if non_positive:
            raise ValueError(f"parameters must be greater than zero: {', '.join(non_positive)}")
        negative = [name for name in allow_zero if numeric[name] < 0]
        if negative:
            raise ValueError(f"parameters cannot be negative: {', '.join(negative)}")
        return numeric

    def validate(self) -> None:
        raise NotImplementedError
