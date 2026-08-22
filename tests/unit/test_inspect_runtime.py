"""Tests for the inspect_runtime module."""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path
from types import ModuleType
from typing import Literal

import pytest

from pebbledoc import config, inspect_runtime


@pytest.fixture
def mock_module() -> ModuleType:
    """Return the test mock module."""
    sys.path.insert(0, str(Path(__file__).parent / "resources"))
    module = importlib.import_module("mock_module")
    sys.path.pop(0)
    return module


@pytest.fixture
def mock_package() -> ModuleType:
    """Return the test mock package."""
    sys.path.insert(0, str(Path(__file__).parent / "resources"))
    package = importlib.import_module("mock_package")
    sys.path.pop(0)
    return package


# == TEST FOR MEMBER DISCOVERY =========================================


def test_discover_public_members(mock_package: ModuleType) -> None:
    """Test that the mock package is correctly handled by the function."""
    output = inspect_runtime.discover_public_members(mock_package)
    expected = {
        # The commented members are there, but excluded for not being local:
        # "sys",
        # "nodes",
        # "Path",
        # "logging",
        "MyClass",
        "my_function",
        "submodule_b",
        "BetterClassName",
        "direct_module",
        "TopLevelClass",
        "top_level_function",
    }
    assert set(output) == expected  # order irrelevant for us


# == TESTS FOR _SIGNATURE_STR ==========================================


def test_signature_str_simple_signature() -> None:
    """Test the signature parsing function for a simple signature."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: str, param_b: int) -> float:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: str, param_b: int) -> float"
    assert output == expected


def test_signature_str_empty_signature() -> None:
    """Test the signature parsing function for an empty signature."""

    # pyrefly: ignore[bad-return]
    def mock_function() -> float:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "() -> float"
    assert output == expected


def test_signature_str_self() -> None:
    """Test the signature parsing function for a signature with ``self``."""

    # pyrefly: ignore[bad-return]
    def mock_function(self, param_a: str, param_b: int) -> float:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(self, param_a: str, param_b: int) -> float"
    assert output == expected


def test_signature_str_classmethod() -> None:
    """Test the signature parsing function for a classmethode."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: str, param_b: int) -> float:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig, is_classmethod=True)
    expected = "(cls, param_a: str, param_b: int) -> float"
    assert output == expected


def test_signature_str_default_args() -> None:
    """Test the signature parsing function for a signature with defaults."""

    def mock_function(
        param_a: bool = True, param_b: int = 0
    ) -> tuple[str, str]:  # pyrefly: ignore[bad-return]
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: bool = True, param_b: int = 0) -> tuple[str, str]"
    assert output == expected


def test_signature_str_string_defaults() -> None:
    """Test the function for a signature with string type defaults."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: str = "abc") -> str:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: str = 'abc') -> str"
    assert output == expected


def test_signature_str_string_literal_defaults() -> None:
    """Test the function for a signature with string literal defaults."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: Literal["abc", "xyz"] = "abc") -> str:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: Literal['abc', 'xyz'] = 'abc') -> str"
    assert output == expected


def test_signature_str_no_param_annotations() -> None:
    """Test the function for a signature without parameter annotations."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a, param_b) -> dict[str, int]:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a, param_b) -> dict[str, int]"
    assert output == expected


def test_signature_str_no_return_annotation() -> None:
    """Test the function for a signature without return type annotation."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: str, param_b: int):
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: str, param_b: int)"
    assert output == expected


def test_signature_str_positional_only() -> None:
    """Test the function for a signature with / in it."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: str, /, param_b: int) -> bool:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: str, /, param_b: int) -> bool"
    assert output == expected


def test_signature_str_keyword_only() -> None:
    """Test the function for a signature with * in it."""

    def mock_function(
        param_a: str, *, param_b: int, param_c: float = 1.2
    ) -> bool:  # pyrefly: ignore[bad-return]
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: str, *, param_b: int, param_c: float = 1.2) -> bool"
    assert output == expected


def test_signature_str_variadic_positional() -> None:
    """Test the function for a signature with *args in it."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: str, *args: int, param_b: int) -> bool:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: str, *args: int, param_b: int) -> bool"
    assert output == expected


def test_signature_str_variadic_keyword() -> None:
    """Test the function for a signature with **kwargs in it."""

    # pyrefly: ignore[bad-return]
    def mock_function(param_a: str, param_b: int, **kwargs: str) -> bool:
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = "(param_a: str, param_b: int, **kwargs: str) -> bool"
    assert output == expected


def test_signature_str_mixed_parameter_types() -> None:
    """Test the function for a mixed signature."""

    def mock_function(
        param_a: str,
        param_b: int,
        /,
        param_c: float,
        param_d: bool = False,
        *,
        optional: str | None = None,
        **kwargs: str,
    ) -> None:  # pyrefly: ignore[bad-return]
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = (
        "(param_a: str, param_b: int, /, param_c: float, "
        "param_d: bool = False, *, optional: str | None = None, "
        "**kwargs: str) -> None"
    )
    assert output == expected


def test_signature_str_mixed_parameter_types_variadic_positionals() -> None:
    """Test the function for a mixed signature with *args instead of *."""

    def mock_function(
        param_a: str,
        param_b: int,
        /,
        param_c: float,
        param_d: bool = False,
        *args: int,
        optional: str | None = None,
        **kwargs: str,
    ) -> None:  # pyrefly: ignore[bad-return]
        pass

    sig = inspect.signature(mock_function)
    output = inspect_runtime._signature_str(sig)
    expected = (
        "(param_a: str, param_b: int, /, param_c: float, "
        "param_d: bool = False, *args: int, optional: str | None = None, "
        "**kwargs: str) -> None"
    )
    assert output == expected


# == HELPER FUNCTIONS ==================================================


def check_constant_mock_constant(node: inspect_runtime.Member) -> None:
    """Check node for representing constant "MOCK_CONSTANT"."""
    assert node.name == "MOCK_CONSTANT"
    assert node.parent == "mock_module"
    assert node.kind == "constant"
    assert node.signature == "MOCK_CONSTANT: float = 3.12"
    assert node.raw_docstring == ""
    assert node.header_level == 3


def check_constant_undocumented(node: inspect_runtime.Member) -> None:
    """Check node for representing constant "UNDOCUMENTED"."""
    assert node.name == "UNDOCUMENTED"
    assert node.parent == "mock_module"
    assert node.kind == "constant"
    assert node.signature == "UNDOCUMENTED: bool = False"
    assert node.raw_docstring == ""
    assert node.header_level == 3


def check_function_mock_function(node: inspect_runtime.Member) -> None:
    """Check node for representing function "mock_function"."""
    assert node.name == "mock_function"
    assert node.parent == "mock_module"
    assert node.kind == "routine"
    assert node.signature == (
        "mock_function(param_a: int, param_b: str, optional: int | None = None) -> str"
    )
    assert node.raw_docstring == (
        "Mock function docstring.\n\n"
        ":param param_a: Parameter A.\n"
        ":param param_b: Parameter B, which has a description that extends\n"
        "    beyond a single line.\n"
        ":param optional: An optional parameter.\n"
        ":return: A string."
    )
    assert node.header_level == 3


def check_function_function_with_custom_type(
    node: inspect_runtime.Member,
) -> None:
    """Check node for representing function "function_with_custom_type"."""
    assert node.name == "function_with_custom_type"
    assert node.parent == "mock_module"
    assert node.kind == "routine"
    assert node.signature == (
        "function_with_custom_type(param: MockClass) -> MockDataclass"
    )
    assert node.raw_docstring == (
        "Function with custom types.\n\n"
        ":param param: A MockClass parameter.\n"
        ":return: A MockDataclass."
    )
    assert node.header_level == 3


def check_method_public_method(node: inspect_runtime.Member) -> None:
    """Check node for representing method "public_method"."""
    assert node.name == "public_method"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "method"
    assert node.signature == (
        "MockClass.public_method(self, param_c: bool, "
        "optional: str | None = None) -> int"
    )
    assert node.raw_docstring == (
        "Public method docstring.\n\n"
        ":param param_c: Parameter C.\n"
        ":param optional: Optional parameter.\n"
        ":return: An integer."
    )
    assert node.header_level == 4


def check_method_class_method(node: inspect_runtime.Member) -> None:
    """Check node for representing class "class_method"."""
    assert node.name == "class_method"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "method"
    assert node.signature == (
        "@classmethod\nMockClass.class_method(cls, param: int) -> int"
    )
    assert node.raw_docstring == (
        "Class method docstring.\n\n:param param: A parameter.\n:return: An integer."
    )
    assert node.header_level == 4


def check_method_static_method(node: inspect_runtime.Member) -> None:
    """Check node for representing static method "static_method"."""
    assert node.name == "static_method"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "method"
    assert node.signature == (
        "@staticmethod\nMockClass.static_method(param: int) -> int"
    )
    assert node.raw_docstring == (
        "Static method docstring.\n\n:param param: A parameter.\n:return: An integer."
    )
    assert node.header_level == 4


def check_classvar_class_var(node: inspect_runtime.Member) -> None:
    """Check node for representing class "class_var"."""
    assert node.name == "class_var"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "classvar"
    assert node.signature == "MockClass.class_var: ClassVar[str] = 'value'"
    assert node.raw_docstring == ""
    assert node.header_level == 4


def check_classvar_undocumented(node: inspect_runtime.Member) -> None:
    """Check node for representing class "undocumented"."""
    assert node.name == "undocumented"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "classvar"
    assert node.signature == "MockClass.undocumented: ClassVar[bool] = False"
    assert node.raw_docstring == ""
    assert node.header_level == 4


def check_property_property_editable(node: inspect_runtime.Member) -> None:
    """Check node for representing property "property_editable"."""
    assert node.name == "property_editable"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "property"
    assert node.signature == "@property\nMockClass.property_editable: int"
    assert node.raw_docstring == (
        "Editable property docstring.\n\n:return: An integer."
    )
    assert node.header_level == 4


def check_property_property_readonly(node: inspect_runtime.Member) -> None:
    """Check node for representing property "property_readonly"."""
    assert node.name == "property_readonly"
    assert node.parent == "mock_module.MockClass"
    assert node.kind == "property"
    assert node.signature == "@property\nMockClass.property_readonly: int"
    assert node.raw_docstring == (
        "Readonly property docstring.\n\n:return: An integer."
    )
    assert node.header_level == 4


def check_class_mock_class(node: inspect_runtime.Member) -> None:
    """Check node for representing class "MockClass"."""
    assert node.name == "MockClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "MockClass(object)"
    assert node.raw_docstring == "Mock class docstring."
    assert node.header_level == 3
    assert len(node.children) == 7

    # Check children
    check_classvar_class_var(node.children[0])
    check_classvar_undocumented(node.children[1])
    check_property_property_readonly(node.children[2])
    check_property_property_editable(node.children[3])
    check_method_public_method(node.children[4])
    check_method_class_method(node.children[5])
    check_method_static_method(node.children[6])


def check_class_mock_class_exclude(node: inspect_runtime.Member) -> None:
    """Check node with members excluded."""
    assert node.name == "MockClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "MockClass(object)"
    assert node.raw_docstring == "Mock class docstring."
    assert node.header_level == 3
    assert len(node.children) == 5  # two were excluded

    # Check children; excluded are static_method and property_readonly
    check_classvar_class_var(node.children[0])
    check_classvar_undocumented(node.children[1])
    # missing here: property_readonly, was excluded
    check_property_property_editable(node.children[2])
    check_method_public_method(node.children[3])
    check_method_class_method(node.children[4])
    # missing here: static_method, was excluded


def check_class_child_class(node: inspect_runtime.Member) -> None:
    """Check node for representing class "ChildClass"."""
    assert node.name == "ChildClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "ChildClass(MockClass)"
    assert node.raw_docstring == "Child class docstring."
    assert node.header_level == 3
    assert len(node.children) == 2

    assert node.children[0].name == "class_var"
    assert node.children[0].kind == "classvar"
    assert node.children[1].name == "new_method"
    assert node.children[1].kind == "method"


def check_class_grandchild_class(node: inspect_runtime.Member) -> None:
    """Check node for representing class "GrandChildClass"."""
    assert node.name == "GrandchildClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "GrandchildClass(ChildClass)"
    assert node.raw_docstring == "Grandchild class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


def check_class_multiple_parents(node: inspect_runtime.Member) -> None:
    """Check node for representing class "MultipleParents"."""
    assert node.name == "MultipleParents"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "MultipleParents(MockClass, AnotherParent)"
    assert node.raw_docstring == "Multiple parents class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


def check_class_mock_dataclass(node: inspect_runtime.Member) -> None:
    """Check node for representing dataclass "MockDataclass"."""
    assert node.name == "MockDataclass"
    assert node.parent == "mock_module"
    assert node.kind == "dataclass"
    assert node.signature == "@dataclass\nMockDataclass(object)"
    assert node.raw_docstring == "Mock dataclass docstring."
    assert node.header_level == 3
    assert len(node.children) == 3

    # Check children
    assert node.children[0].name == "class_var"
    assert node.children[0].parent == "mock_module.MockDataclass"
    assert node.children[0].kind == "classvar"
    assert (
        node.children[0].signature
        == "MockDataclass.class_var: ClassVar[int] = 0"
    )
    assert node.children[0].raw_docstring == ""
    assert node.children[0].header_level == 4

    assert node.children[1].name == "undocumented"
    assert node.children[1].parent == "mock_module.MockDataclass"
    assert node.children[1].kind == "classvar"
    assert (
        node.children[1].signature
        == "MockDataclass.undocumented: ClassVar[bool] = False"
    )
    assert node.children[1].raw_docstring == ""
    assert node.children[1].header_level == 4

    assert node.children[2].name == "public_method"
    assert node.children[2].parent == "mock_module.MockDataclass"
    assert node.children[2].kind == "method"
    assert node.children[2].signature == (
        "MockDataclass.public_method(self, param_c: bool, "
        "optional: str | None = None) -> int"
    )
    assert node.children[2].raw_docstring == (
        "Public method docstring.\n\n"
        ":param param_c: Parameter C.\n"
        ":param optional: An optional parameter.\n"
        ":return: An integer."
    )
    assert node.children[2].header_level == 4


def check_method_abstract_method(node: inspect_runtime.Member) -> None:
    """Check node for representing abstract method "abstract_method"."""
    assert node.name == "abstract_method"
    assert node.parent == "mock_module.MockAbstractClass"
    assert node.kind == "method"
    assert node.signature == (
        "@abstractmethod\n"
        "MockAbstractClass.abstract_method(self) -> tuple[str, int]"
    )
    assert node.raw_docstring == (
        "Abstract method docstring.\n\n"
        ":return: A tuple of a string and an integer."
    )
    assert node.header_level == 4


def check_class_abstract_base_class(node: inspect_runtime.Member) -> None:
    """Check node for representing abstract base class "MockAbstractClass"."""
    assert node.name == "MockAbstractClass"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "MockAbstractClass(ABC)"
    assert node.raw_docstring == "Mock abstract class docstring."
    assert node.header_level == 3
    assert len(node.children) == 1
    check_method_abstract_method(node.children[0])


# == MEMBER FUNCTION TESTS =============================================


def test_member_constant_with_docstring(mock_module: ModuleType) -> None:
    """Test the function for a member with a constant value."""
    output = inspect_runtime._member_constant(
        "MOCK_CONSTANT", mock_module.MOCK_CONSTANT, "mock_module"
    )
    check_constant_mock_constant(output)


def test_member_constant_no_docstring(mock_module: ModuleType) -> None:
    """Test the function for a member with a constant value."""
    output = inspect_runtime._member_constant(
        "UNDOCUMENTED", mock_module.UNDOCUMENTED, "mock_module"
    )
    check_constant_undocumented(output)


def test_member_constant_string_types() -> None:
    """Test that members of type string appear in quotes in their signature."""
    output = inspect_runtime._member_constant(
        "STRING_CONSTANT", "abc", "mock_module"
    )
    assert output.name == "STRING_CONSTANT"
    assert output.parent == "mock_module"
    assert output.kind == "constant"
    assert output.signature == "STRING_CONSTANT: str = 'abc'"
    assert output.raw_docstring == ""
    assert output.header_level == 3


@pytest.mark.xfail(
    reason="Literal types not yet supported for constants, see #30"
)
def test_member_constant_string_literal_types() -> None:
    """Test that members of type string literal have correct signature."""
    my_const: Literal["abc", "xyz"] = "abc"
    output = inspect_runtime._member_constant(
        "STRING_CONSTANT", my_const, "mock_module"
    )
    assert output.name == "STRING_CONSTANT"
    assert output.parent == "mock_module"
    assert output.kind == "constant"
    assert output.signature == "STRING_CONSTANT: Literal['abc', 'xyz'] = 'abc'"
    assert output.raw_docstring == ""
    assert output.header_level == 3


def test_member_function(mock_module: ModuleType) -> None:
    """Test the function for a member function."""
    output = inspect_runtime._member_function(
        "mock_function", mock_module.mock_function, "mock_module"
    )
    check_function_mock_function(output)


def test_member_function_custom_types(mock_module: ModuleType) -> None:
    """Test the function for a member function with non-builtin types."""
    output = inspect_runtime._member_function(
        "function_with_custom_type",
        mock_module.function_with_custom_type,
        "mock_module",
    )
    check_function_function_with_custom_type(output)


def test_member_method_basic(mock_module: ModuleType) -> None:
    """Test the function for a method."""
    output = inspect_runtime._member_method(
        "public_method",
        mock_module.MockClass.public_method,
        "mock_module.MockClass",
        None,
    )
    check_method_public_method(output)


def test_member_method_decorated(mock_module: ModuleType) -> None:
    """Test the function for a decorated method."""
    output = inspect_runtime._member_method(
        "public_method",
        mock_module.MockClass.public_method,
        "mock_module.MockClass",
        "decorator",
    )
    assert output.name == "public_method"
    assert output.parent == "mock_module.MockClass"
    assert output.kind == "method"
    assert output.signature == (
        "@decorator\nMockClass.public_method(self, param_c: bool, "
        "optional: str | None = None) -> int"
    )
    assert output.raw_docstring == (
        "Public method docstring.\n\n"
        ":param param_c: Parameter C.\n"
        ":param optional: Optional parameter.\n"
        ":return: An integer."
    )
    assert output.header_level == 4


def test_member_method_classmethod(mock_module: ModuleType) -> None:
    """Test the function for a class method."""
    output = inspect_runtime._member_method(
        "class_method",
        mock_module.MockClass.class_method,
        "mock_module.MockClass",
        "classmethod",
    )
    check_method_class_method(output)


def test_member_method_staticmethod(mock_module: ModuleType) -> None:
    """Test the function for a static method."""
    output = inspect_runtime._member_method(
        "static_method",
        mock_module.MockClass.static_method,
        "mock_module.MockClass",
        "staticmethod",
    )
    check_method_static_method(output)


def test_member_method_abstractmethod(mock_module: ModuleType) -> None:
    """Test the function for a abstract method."""
    output = inspect_runtime._member_method(
        "abstract_method",
        mock_module.MockAbstractClass.abstract_method,
        "mock_module.MockAbstractClass",
        "abstractmethod",
    )
    check_method_abstract_method(output)


def test_member_classvar(mock_module: ModuleType) -> None:
    """Test the function for a classvar."""
    output = inspect_runtime._member_classvar(
        "class_var", mock_module.MockClass.class_var, "mock_module.MockClass"
    )
    check_classvar_class_var(output)


def test_member_classvar_no_docs(mock_module: ModuleType) -> None:
    """Test the function for a classvar without docstring."""
    output = inspect_runtime._member_classvar(
        "undocumented",
        mock_module.MockClass.undocumented,
        "mock_module.MockClass",
    )
    check_classvar_undocumented(output)


def test_member_property(mock_module: ModuleType) -> None:
    """Test the function for a property."""
    output = inspect_runtime._member_property(
        "property_editable",
        mock_module.MockClass.property_editable,
        "mock_module.MockClass",
    )
    check_property_property_editable(output)


def test_member_class_normal(mock_module: ModuleType) -> None:
    """Test the function for a class."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_class(
        "MockClass", mock_module.MockClass, "mock_module", test_config
    )
    check_class_mock_class(output)


def test_member_class_exclude(mock_module: ModuleType) -> None:
    """Test the function for a class with members excluded."""
    exclude = ["property_readonly", "static_method"]
    test_config = config.PebbledocConfig(exclude=exclude)
    output = inspect_runtime._member_class(
        "MockClass", mock_module.MockClass, "mock_module", test_config
    )
    check_class_mock_class_exclude(output)


def test_member_class_inheritance(mock_module: ModuleType) -> None:
    """Test the function for a class with a parent class."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_class(
        "ChildClass", mock_module.ChildClass, "mock_module", test_config
    )
    check_class_child_class(output)


def test_member_class_inheritance_chain(mock_module: ModuleType) -> None:
    """Test the function for a class further down an inheritance chain."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_class(
        "GrandchildClass",
        mock_module.GrandchildClass,
        "mock_module",
        test_config,
    )
    check_class_grandchild_class(output)


def test_member_class_multiple_inheritance(mock_module: ModuleType) -> None:
    """Test the function for a class with multiple parents."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_class(
        "MultipleParents",
        mock_module.MultipleParents,
        "mock_module",
        test_config,
    )
    check_class_multiple_parents(output)


def test_member_class_dataclass(mock_module: ModuleType) -> None:
    """Test the function for a dataclass."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_class(
        "MockDataclass", mock_module.MockDataclass, "mock_module", test_config
    )
    check_class_mock_dataclass(output)


def test_member_class_abstract_base_class(mock_module: ModuleType) -> None:
    """Test the function for a abstract base class."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_class(
        "MockAbstractClass",
        mock_module.MockAbstractClass,
        "mock_module",
        test_config,
    )
    check_class_abstract_base_class(output)


def test_member_module(mock_module: ModuleType) -> None:
    """Test the function for a module."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_module(
        "mock_module", mock_module, test_config, "mock_module", ""
    )
    assert output.name == "mock_module"
    assert output.parent == ""
    assert output.kind == "module"
    assert output.signature == ""
    assert output.raw_docstring == "Mock module docstring."
    assert output.header_level == 2
    assert len(output.children) == 11

    # check children
    check_constant_mock_constant(output.children[0])
    check_constant_undocumented(output.children[1])
    check_function_mock_function(output.children[2])
    check_class_mock_class(output.children[3])
    check_class_child_class(output.children[4])
    check_class_grandchild_class(output.children[5])
    # missing here: the class "AnotherParent", verified below
    check_class_multiple_parents(output.children[7])
    check_class_mock_dataclass(output.children[8])
    check_function_function_with_custom_type(output.children[9])
    check_class_abstract_base_class(output.children[10])

    # check AnotherParent class
    node = output.children[6]
    assert node.name == "AnotherParent"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "AnotherParent(object)"
    assert node.raw_docstring == "Another parent class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


def test_member_module_parent(mock_module: ModuleType) -> None:
    """Test the function for a module with a parent."""
    test_config = config.PebbledocConfig()
    output = inspect_runtime._member_module(
        "mock_module", mock_module, test_config, "mock_module", "parent"
    )
    assert output.name == "mock_module"
    assert output.parent == "parent"
    assert output.kind == "module"
    assert output.signature == ""
    assert output.raw_docstring == "Mock module docstring."
    assert output.header_level == 2
    assert len(output.children) == 11
    for child in output.children:
        assert child.parent == "parent.mock_module"


def test_member_module_no_constants(mock_module: ModuleType) -> None:
    """Test the function for a module."""
    test_config = config.PebbledocConfig(document_constants=False)
    output = inspect_runtime._member_module(
        "mock_module", mock_module, test_config, "mock_module", ""
    )
    assert output.name == "mock_module"
    assert output.parent == ""
    assert output.kind == "module"
    assert output.signature == ""
    assert output.raw_docstring == "Mock module docstring."
    assert output.header_level == 2
    assert len(output.children) == 9

    # check children
    check_function_mock_function(output.children[0])
    check_class_mock_class(output.children[1])
    check_class_child_class(output.children[2])
    check_class_grandchild_class(output.children[3])
    # missing here: the class "AnotherParent", verified below
    check_class_multiple_parents(output.children[5])
    check_class_mock_dataclass(output.children[6])
    check_function_function_with_custom_type(output.children[7])
    check_class_abstract_base_class(output.children[8])

    # check AnotherParent class
    node = output.children[4]
    assert node.name == "AnotherParent"
    assert node.parent == "mock_module"
    assert node.kind == "class"
    assert node.signature == "AnotherParent(object)"
    assert node.raw_docstring == "Another parent class docstring."
    assert node.header_level == 3
    assert len(node.children) == 0


def test_member_module_exclude(mock_module: ModuleType) -> None:
    """Test the function when members are excluded by the user."""
    exclude = [
        "mock_function",
        "property_readonly",
        "static_method",
        "AnotherParent",
    ]
    test_config = config.PebbledocConfig(exclude=exclude)
    output = inspect_runtime._member_module(
        "mock_module", mock_module, test_config, "mock_module", ""
    )
    assert output.name == "mock_module"
    assert output.parent == ""
    assert output.kind == "module"
    assert output.signature == ""
    assert output.raw_docstring == "Mock module docstring."
    assert output.header_level == 2
    assert len(output.children) == 9  # 2 were removed at this level

    # check children
    check_constant_mock_constant(output.children[0])
    check_constant_undocumented(output.children[1])
    # missing here: mock_function, was excluded
    check_class_mock_class_exclude(output.children[2])
    check_class_child_class(output.children[3])
    check_class_grandchild_class(output.children[4])
    # missing here: the class "AnotherParent", was excluded
    check_class_multiple_parents(output.children[5])
    check_class_mock_dataclass(output.children[6])
    check_function_function_with_custom_type(output.children[7])
    check_class_abstract_base_class(output.children[8])
