"""
Tests for extension sandbox security.
"""

from pathlib import Path

import pytest

from vfwidgets_theme.errors import SecurityError
from vfwidgets_theme.extensions.sandbox import (
    ExecutionLimiter,
    ExtensionSandbox,
    RestrictedBuiltins,
    SafeObjectProxy,
    SandboxSecurityChecker,
)
from vfwidgets_theme.extensions.system import Extension


class TestRestrictedBuiltins:
    """Test restricted builtins functionality."""

    def test_create_restricted_builtins(self):
        """Test creation of restricted builtins dictionary."""
        builtins_dict = RestrictedBuiltins.create_restricted_builtins()

        # Check allowed builtins are present
        assert "len" in builtins_dict
        assert "str" in builtins_dict
        assert "list" in builtins_dict
        assert "dict" in builtins_dict

        # Check forbidden builtins are not present
        assert "open" not in builtins_dict
        assert "exec" not in builtins_dict
        assert "eval" not in builtins_dict
        assert "__import__" not in builtins_dict

        # Check safe print is present
        assert "print" in builtins_dict
        assert callable(builtins_dict["print"])

    def test_safe_print(self):
        """Test safe print function doesn't raise errors."""
        # Should not raise any exceptions
        RestrictedBuiltins._safe_print("test message")
        RestrictedBuiltins._safe_print("multiple", "arguments")
        RestrictedBuiltins._safe_print("with", "keyword", sep=", ")


class TestSandboxSecurityChecker:
    """Test security checker functionality."""

    @pytest.fixture
    def checker(self):
        """Create security checker."""
        return SandboxSecurityChecker()

    def test_check_valid_code(self, checker):
        """Test that valid code passes security check."""
        valid_code = """
def hello():
    return "Hello World"

x = [1, 2, 3]
y = len(x)
"""
        # Should not raise any exceptions
        checker.check_ast(valid_code)

    def test_forbidden_imports(self, checker):
        """Test that forbidden imports are blocked."""
        with pytest.raises(SecurityError, match="Forbidden import"):
            checker.check_ast("import os")

        with pytest.raises(SecurityError, match="Forbidden import"):
            checker.check_ast("import sys")

        with pytest.raises(SecurityError, match="Forbidden import from"):
            checker.check_ast("from subprocess import call")

    def test_forbidden_function_calls(self, checker):
        """Test that forbidden function calls are blocked."""
        with pytest.raises(SecurityError, match="Forbidden function call"):
            checker.check_ast("exec('print(hello)')")

        with pytest.raises(SecurityError, match="Forbidden function call"):
            checker.check_ast("eval('1 + 1')")

    def test_forbidden_attribute_access(self, checker):
        """Test that forbidden attribute access is blocked."""
        with pytest.raises(SecurityError, match="Forbidden attribute access"):
            checker.check_ast("obj.__class__")

        with pytest.raises(SecurityError, match="Forbidden attribute access"):
            checker.check_ast("func.__globals__")

    def test_forbidden_name_access(self, checker):
        """Test that forbidden name access is blocked."""
        with pytest.raises(SecurityError, match="Forbidden name access"):
            checker.check_ast("x = __builtins__")

    def test_syntax_error_handling(self, checker):
        """Test handling of syntax errors."""
        with pytest.raises(SecurityError, match="Syntax error"):
            checker.check_ast("invalid python syntax {")


class TestExecutionLimiter:
    """Test execution limiter functionality."""

    def test_execution_within_limits(self):
        """Test that execution within limits succeeds."""
        limiter = ExecutionLimiter(time_limit=1.0)

        with limiter.limit_execution():
            # Fast operation should succeed
            result = sum(range(100))
            assert result == 4950

    def test_time_limit_exceeded(self):
        """Test that time limit is enforced."""
        limiter = ExecutionLimiter(time_limit=0.1)

        with pytest.raises(SecurityError, match="timeout"):
            with limiter.limit_execution():
                # Slow operation should be stopped
                import time

                time.sleep(0.2)


class TestExtensionSandbox:
    """Test extension sandbox functionality."""

    @pytest.fixture
    def sandbox(self):
        """Create extension sandbox."""
        return ExtensionSandbox()

    @pytest.fixture
    def sample_extension(self):
        """Create sample extension for testing."""
        return Extension(
            name="test_extension",
            version="1.0.0",
            description="Test extension",
            author="Test Author",
            path=Path("/fake/path"),
            hooks={},
        )

    def test_sandbox_initialization(self, sandbox):
        """Test sandbox initialization."""
        assert sandbox.security_checker is not None
        assert sandbox.execution_limiter is not None
        assert sandbox.restricted_builtins is not None
        assert isinstance(sandbox._extension_namespaces, dict)

    def test_initialize_extension(self, sandbox, sample_extension):
        """Test extension initialization in sandbox."""
        sandbox.initialize_extension(sample_extension)

        assert sample_extension.id in sandbox._extension_namespaces
        namespace = sandbox._extension_namespaces[sample_extension.id]

        assert "__builtins__" in namespace
        assert "__name__" in namespace
        assert "__extension__" in namespace
        assert namespace["__extension__"] is sample_extension

    def test_cleanup_extension(self, sandbox, sample_extension):
        """Test extension cleanup."""
        sandbox.initialize_extension(sample_extension)
        assert sample_extension.id in sandbox._extension_namespaces

        sandbox.cleanup_extension(sample_extension)
        assert sample_extension.id not in sandbox._extension_namespaces

    def test_execute_safely_simple_function(self, sandbox, sample_extension):
        """Test safe execution of simple function."""
        sandbox.initialize_extension(sample_extension)

        def test_func():
            return 42

        result = sandbox.execute_safely(sample_extension, test_func)
        assert result == 42

    def test_execute_safely_with_arguments(self, sandbox, sample_extension):
        """Test safe execution with arguments."""
        sandbox.initialize_extension(sample_extension)

        def test_func(a, b, c=10):
            return a + b + c

        result = sandbox.execute_safely(sample_extension, test_func, 1, 2, c=3)
        assert result == 6

    def test_validate_code_valid(self, sandbox):
        """Test code validation with valid code."""
        valid_code = "def hello(): return 'world'"
        # Should not raise
        sandbox.validate_code(valid_code)

    def test_validate_code_invalid(self, sandbox):
        """Test code validation with invalid code."""
        invalid_code = "import os; os.system('rm -rf /')"
        with pytest.raises(SecurityError):
            sandbox.validate_code(invalid_code)

    def test_create_safe_namespace(self, sandbox):
        """Test safe namespace creation."""
        namespace = sandbox.create_safe_namespace("test_ext")

        assert "__builtins__" in namespace
        assert "__name__" in namespace
        assert namespace["__name__"] == "extension_test_ext"

    def test_is_safe_attribute(self, sandbox):
        """Test attribute safety checking."""

        class TestObj:
            safe_attr = "safe"
            __unsafe_attr__ = "unsafe"

        obj = TestObj()

        assert sandbox.is_safe_attribute(obj, "safe_attr")
        assert not sandbox.is_safe_attribute(obj, "__unsafe_attr__")
        assert not sandbox.is_safe_attribute(obj, "__class__")

    def test_wrap_object_basic_types(self, sandbox):
        """Test object wrapping for basic types."""
        # Basic types should pass through unchanged
        assert sandbox.wrap_object("string") == "string"
        assert sandbox.wrap_object(42) == 42
        assert sandbox.wrap_object([1, 2, 3]) == [1, 2, 3]
        assert sandbox.wrap_object({"key": "value"}) == {"key": "value"}

    def test_wrap_object_complex_type(self, sandbox):
        """Test object wrapping for complex types."""

        class TestClass:
            def __init__(self):
                self.value = 42

        obj = TestClass()
        wrapped = sandbox.wrap_object(obj)

        assert isinstance(wrapped, SafeObjectProxy)

    def test_shutdown(self, sandbox, sample_extension):
        """Test sandbox shutdown."""
        sandbox.initialize_extension(sample_extension)
        assert len(sandbox._extension_namespaces) > 0

        sandbox.shutdown()
        assert len(sandbox._extension_namespaces) == 0


class TestSafeObjectProxy:
    """Test safe object proxy functionality."""

    @pytest.fixture
    def sandbox(self):
        """Create sandbox for proxy testing."""
        return ExtensionSandbox()

    @pytest.fixture
    def test_object(self):
        """Create test object."""

        class TestClass:
            def __init__(self):
                self.safe_value = 42
                self.__private_value = "private"

            def safe_method(self):
                return "safe"

            def __private_method(self):
                return "private"

        return TestClass()

    def test_safe_attribute_access(self, sandbox, test_object):
        """Test safe attribute access through proxy."""
        proxy = SafeObjectProxy(test_object, sandbox)

        # Safe access should work
        assert proxy.safe_value == 42

    def test_forbidden_attribute_access(self, sandbox, test_object):
        """Test that forbidden attributes are blocked."""
        proxy = SafeObjectProxy(test_object, sandbox)

        # Should block access to private attributes
        with pytest.raises(SecurityError):
            _ = proxy.__class__

    def test_safe_method_call(self, sandbox, test_object):
        """Test safe method calls through proxy."""
        proxy = SafeObjectProxy(test_object, sandbox)

        result = proxy.safe_method()
        assert result == "safe"

    def test_callable_proxy(self, sandbox):
        """Test proxy for callable objects."""

        def test_func(x):
            return x * 2

        proxy = SafeObjectProxy(test_func, sandbox)
        result = proxy(21)
        assert result == 42

    def test_non_callable_proxy(self, sandbox):
        """Test proxy for non-callable objects."""
        proxy = SafeObjectProxy("not callable", sandbox)

        with pytest.raises(TypeError, match="not callable"):
            proxy()

    def test_proxy_repr(self, sandbox, test_object):
        """Test proxy representation."""
        proxy = SafeObjectProxy(test_object, sandbox)
        repr_str = repr(proxy)

        assert "SafeProxy" in repr_str
