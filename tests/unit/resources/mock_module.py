"""Mock module docstring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Final

MOCK_CONSTANT: Final[float] = 3.12
"""Mock constant docstring."""

UNDOCUMENTED: Final[bool] = False


# pyrefly: ignore[bad-return]
def mock_function(param_a: int, param_b: str, optional: int | None = None) -> str:
    """
    Mock function docstring.

    :param param_a: Parameter A.
    :param param_b: Parameter B, which has a description that extends
        beyond a single line.
    :param optional: An optional parameter.
    :return: A string.
    """
    pass


class MockClass:
    """Mock class docstring."""

    class_var: ClassVar[int] = 0
    """Class variable docstring."""

    undocumented: ClassVar[bool] = UNDOCUMENTED

    @property
    def property_readonly(self) -> int:
        """
        Readonly property docstring.

        :return: An integer.
        """
        return 1

    @property
    def property_editable(self) -> int:
        """
        Editable property docstring.

        :return: An integer.
        """
        return self._private_attr

    @property_editable.setter
    def property_editable(self, value: int) -> None:
        """
        Setter for editable property docstring.

        :param value: New value.
        :return: None.
        """
        self._private_attr = value

    def __init__(
        self, param_a: int, param_b: str, optional: float | None = None
    ) -> None:
        """
        :param param_a: Parameter A.
        :param param_b: Parameter B.
        :param optional: Optional parameter.
        """
        self.param_a = param_a
        self.param_b = param_b
        self.optional = optional if optional else MOCK_CONSTANT
        self._private_attr = 0

    # pyrefly: ignore[bad-return]
    def public_method(self, param_c: bool, optional: str | None = None) -> int:
        """
        Public method docstring.

        :param param_c: Parameter C.
        :param optional: Optional parameter.
        :return: An integer.
        """
        pass

    # pyrefly: ignore[bad-return]
    def _private_method(self, param_d: bool, optional: str | None = None) -> bytes:
        """
        Private method docstring.

        :param param_d: Parameter D.
        :param optional: Optional parameter.
        :return: Bytes.
        """
        pass

    @classmethod
    def class_method(cls, param: int) -> int:  # pyrefly: ignore[bad-return]
        """
        Class method docstring.

        :param param: A parameter.
        :return: An integer.
        """
        pass

    @staticmethod
    def static_method(param: int) -> int:  # pyrefly: ignore[bad-return]
        """
        Static method docstring.

        :param param: A parameter.
        :return: An integer.
        """
        pass


class ChildClass(MockClass):
    """Child class docstring."""

    class_var: ClassVar[int] = 12  # overwritten, no doc

    # pyrefly: ignore[bad-return]
    def new_method(self, param_a: float, param_b: str) -> int:
        """
        New method docstring.

        :param param_a: Parameter A.
        :param param_b: Parameter B.
        :return: An integer.
        """
        pass


class GrandchildClass(ChildClass):
    """Grandchild class docstring."""


class AnotherParent:
    """Another parent class docstring."""

    pass


class MultipleParents(MockClass, AnotherParent):
    """Multiple parents class docstring."""

    pass


@dataclass
class MockDataclass:
    """Mock dataclass docstring."""

    class_var: ClassVar[int] = 0
    """Class variable docstring."""
    undocumented: ClassVar[bool] = UNDOCUMENTED

    param_a: float
    param_b: str
    optional: bool | None = None

    def __post_init__(self) -> None:
        """
        Post initialization docstring.

        :return: None.
        """
        if self.optional is None:
            self.optional = UNDOCUMENTED

    # pyrefly: ignore[bad-return]
    def public_method(self, param_c: bool, optional: str | None = None) -> int:
        """
        Public method docstring.

        :param param_c: Parameter C.
        :param optional: An optional parameter.
        :return: An integer.
        """
        pass


# pyrefly: ignore[bad-return]
def function_with_custom_type(param: MockClass) -> MockDataclass:
    """
    Function with custom types.

    :param param: A MockClass parameter.
    :return: A MockDataclass.
    """
    pass
