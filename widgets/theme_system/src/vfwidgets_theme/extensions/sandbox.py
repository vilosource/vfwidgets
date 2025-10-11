"""Extension sandbox for secure execution.

Provides a secure environment for running extension code with restricted
access to system resources and APIs.
"""

import ast
import builtins
import resource
import threading
import time
import types
from contextlib import contextmanager
from typing import Any, Callable

from ..errors import ExtensionError, SecurityError
from ..logging import get_logger

logger = get_logger(__name__)


class RestrictedBuiltins:
    """Restricted set of builtin functions for extensions."""

    ALLOWED_BUILTINS = {
        # Type functions
        "abs",
        "all",
        "any",
        "bool",
        "bytearray",
        "bytes",
        "chr",
        "dict",
        "enumerate",
        "filter",
        "float",
        "frozenset",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "next",
        "object",
        "ord",
        "range",
        "reversed",
        "round",
        "set",
        "slice",
        "sorted",
        "str",
        "sum",
        "tuple",
        "type",
        "zip",
        # Safe functions
        "divmod",
        "pow",
        "repr",
        "format",
        "hash",
        "hex",
        "oct",
        "bin",
        "ascii",
        "callable",
        "classmethod",
        "staticmethod",
        "property",
        # Exceptions
        "Exception",
        "ValueError",
        "TypeError",
        "KeyError",
        "IndexError",
        "AttributeError",
        "RuntimeError",
        "NotImplementedError",
    }

    FORBIDDEN_BUILTINS = {
        # File operations
        "open",
        "file",
        # System functions
        "exec",
        "eval",
        "compile",
        "__import__",
        "globals",
        "locals",
        "vars",
        "dir",
        "getattr",
        "setattr",
        "delattr",
        "hasattr",
        # Memory operations
        "memoryview",
        "bytearray",
        # Debugging
        "breakpoint",
        "input",
        "print",  # print can be allowed selectively
    }

    @classmethod
    def create_restricted_builtins(cls) -> dict[str, Any]:
        """Create restricted builtins dictionary."""
        restricted = {}

        for name in cls.ALLOWED_BUILTINS:
            if hasattr(builtins, name):
                restricted[name] = getattr(builtins, name)

        # Add safe print function
        restricted["print"] = cls._safe_print

        return restricted

    @staticmethod
    def _safe_print(*args, **kwargs):
        """Safe print function that logs instead of printing to stdout."""
        # Convert arguments to strings safely
        safe_args = []
        for arg in args:
            try:
                safe_args.append(str(arg))
            except Exception:
                safe_args.append("<unprintable>")

        message = " ".join(safe_args)
        logger.info(f"Extension print: {message}")


class SandboxSecurityChecker:
    """Security checker for extension code."""

    FORBIDDEN_NAMES = {
        # System modules
        "os",
        "sys",
        "subprocess",
        "threading",
        "multiprocessing",
        # File system
        "open",
        "file",
        "io",
        "pathlib",
        # Network
        "socket",
        "urllib",
        "requests",
        "http",
        # Dangerous builtins
        "exec",
        "eval",
        "__import__",
        "compile",
        # Internal Python
        "__builtins__",
        "__globals__",
        "__locals__",
    }

    FORBIDDEN_ATTRIBUTES = {
        "__class__",
        "__bases__",
        "__mro__",
        "__subclasses__",
        "__globals__",
        "__code__",
        "__closure__",
        "__defaults__",
        "func_globals",
        "func_code",
        "gi_frame",
        "gi_code",
    }

    def check_ast(self, code: str) -> None:
        """Check AST for security violations.

        Args:
            code: Source code to check

        Raises:
            SecurityError: If code violates security policy

        """
        try:
            tree = ast.parse(code)
            self._check_node(tree)
        except SyntaxError as e:
            raise SecurityError(f"Syntax error in extension code: {e}")

    def _check_node(self, node: ast.AST) -> None:
        """Recursively check AST node for security violations."""
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.FORBIDDEN_NAMES:
                    raise SecurityError(f"Forbidden import: {alias.name}")

        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module in self.FORBIDDEN_NAMES:
                raise SecurityError(f"Forbidden import from: {node.module}")

        # Check attribute access
        elif isinstance(node, ast.Attribute):
            if node.attr in self.FORBIDDEN_ATTRIBUTES:
                raise SecurityError(f"Forbidden attribute access: {node.attr}")

        # Check function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.FORBIDDEN_NAMES:
                    raise SecurityError(f"Forbidden function call: {node.func.id}")

        # Check name access
        elif isinstance(node, ast.Name):
            if node.id in self.FORBIDDEN_NAMES:
                raise SecurityError(f"Forbidden name access: {node.id}")

        # Recursively check child nodes
        for child in ast.iter_child_nodes(node):
            self._check_node(child)


class ExecutionLimiter:
    """Limits execution time and resource usage."""

    def __init__(self, time_limit: float = 5.0, memory_limit: int = 50 * 1024 * 1024):
        """Initialize execution limiter.

        Args:
            time_limit: Maximum execution time in seconds
            memory_limit: Maximum memory usage in bytes

        """
        self.time_limit = time_limit
        self.memory_limit = memory_limit

    @contextmanager
    def limit_execution(self):
        """Context manager for limited execution."""
        start_time = time.time()
        original_limit = None

        try:
            # Set memory limit (Unix only)
            try:
                original_limit = resource.getrlimit(resource.RLIMIT_AS)
                resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
            except (ImportError, OSError):
                # resource module not available or permission denied
                pass

            yield

            # Check time limit
            elapsed = time.time() - start_time
            if elapsed > self.time_limit:
                raise SecurityError(
                    f"Extension execution timeout ({elapsed:.2f}s > {self.time_limit}s)"
                )

        finally:
            # Restore original memory limit
            if original_limit:
                try:
                    resource.setrlimit(resource.RLIMIT_AS, original_limit)
                except (ImportError, OSError):
                    pass


class ExtensionSandbox:
    """Secure sandbox environment for extension execution.

    Provides isolated execution with restricted access to system resources.
    """

    def __init__(self):
        """Initialize extension sandbox."""
        self.security_checker = SandboxSecurityChecker()
        self.execution_limiter = ExecutionLimiter()
        self.restricted_builtins = RestrictedBuiltins.create_restricted_builtins()

        # Extension-specific namespaces
        self._extension_namespaces: dict[str, dict[str, Any]] = {}

        # Thread-local storage for current extension
        self._local = threading.local()

        logger.info("Extension sandbox initialized")

    def initialize_extension(self, extension) -> None:
        """Initialize sandbox environment for an extension.

        Args:
            extension: Extension to initialize

        """
        logger.debug(f"Initializing sandbox for extension: {extension.name}")

        # Create isolated namespace for extension
        namespace = {
            "__builtins__": self.restricted_builtins,
            "__name__": f"extension_{extension.name}",
            "__extension__": extension,
        }

        # Add extension API
        from .api import ExtensionAPI

        namespace["api"] = ExtensionAPI()

        self._extension_namespaces[extension.id] = namespace

    def cleanup_extension(self, extension) -> None:
        """Cleanup sandbox for an extension.

        Args:
            extension: Extension to cleanup

        """
        logger.debug(f"Cleaning up sandbox for extension: {extension.name}")

        if extension.id in self._extension_namespaces:
            del self._extension_namespaces[extension.id]

    def execute_safely(self, extension, func: Callable, *args, **kwargs) -> Any:
        """Execute function in sandbox environment.

        Args:
            extension: Extension context
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            SecurityError: If execution violates security policy
            ExtensionError: If execution fails

        """
        # Set current extension in thread-local storage
        self._local.current_extension = extension

        try:
            with self.execution_limiter.limit_execution():
                # Execute in isolated namespace
                namespace = self._extension_namespaces.get(extension.id, {})

                # Add function to namespace temporarily
                func.__globals__ if hasattr(func, "__globals__") else {}

                # Create safe execution environment
                safe_globals = {**namespace}

                # Execute function
                if hasattr(func, "__code__"):
                    # For regular functions, create new function with safe globals
                    safe_func = types.FunctionType(
                        func.__code__,
                        safe_globals,
                        func.__name__,
                        func.__defaults__,
                        func.__closure__,
                    )
                    return safe_func(*args, **kwargs)
                else:
                    # For other callables, call directly
                    return func(*args, **kwargs)

        except SecurityError:
            logger.error(f"Security violation in extension {extension.name}")
            raise
        except Exception as e:
            logger.error(f"Error executing extension {extension.name}: {e}")
            raise ExtensionError(f"Extension execution failed: {e}")
        finally:
            # Clean up thread-local storage
            if hasattr(self._local, "current_extension"):
                delattr(self._local, "current_extension")

    def validate_code(self, code: str) -> None:
        """Validate extension code for security.

        Args:
            code: Source code to validate

        Raises:
            SecurityError: If code violates security policy

        """
        self.security_checker.check_ast(code)

    def create_safe_namespace(self, extension_name: str) -> dict[str, Any]:
        """Create safe namespace for extension.

        Args:
            extension_name: Name of extension

        Returns:
            Safe namespace dictionary

        """
        return {
            "__builtins__": self.restricted_builtins,
            "__name__": f"extension_{extension_name}",
            "api": None,  # Will be set when extension loads
        }

    def get_current_extension(self):
        """Get currently executing extension from thread-local storage."""
        return getattr(self._local, "current_extension", None)

    def is_safe_attribute(self, obj: Any, attr_name: str) -> bool:
        """Check if attribute access is safe.

        Args:
            obj: Object to check
            attr_name: Attribute name

        Returns:
            True if access is safe

        """
        if attr_name in self.security_checker.FORBIDDEN_ATTRIBUTES:
            return False

        # Check object type
        if isinstance(obj, type):
            # Don't allow access to class internals
            if attr_name.startswith("__") and attr_name.endswith("__"):
                return False

        return True

    def wrap_object(self, obj: Any):
        """Wrap object to provide safe access.

        Args:
            obj: Object to wrap

        Returns:
            Wrapped object with restricted access

        """
        if isinstance(obj, (str, int, float, bool, list, dict, tuple, set)):
            # Basic types are safe
            return obj

        # For complex objects, create a proxy
        return SafeObjectProxy(obj, self)

    def shutdown(self) -> None:
        """Shutdown sandbox and cleanup resources."""
        logger.info("Shutting down extension sandbox")

        # Clear all extension namespaces
        self._extension_namespaces.clear()


class SafeObjectProxy:
    """Proxy object that restricts attribute access."""

    def __init__(self, wrapped_object: Any, sandbox: ExtensionSandbox):
        object.__setattr__(self, "_wrapped_object", wrapped_object)
        object.__setattr__(self, "_sandbox", sandbox)

    def __getattr__(self, name: str) -> Any:
        sandbox = object.__getattribute__(self, "_sandbox")
        wrapped = object.__getattribute__(self, "_wrapped_object")

        if not sandbox.is_safe_attribute(wrapped, name):
            raise SecurityError(f"Access to attribute '{name}' is forbidden")

        attr = getattr(wrapped, name)
        return sandbox.wrap_object(attr)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            return object.__setattr__(self, name, value)

        sandbox = object.__getattribute__(self, "_sandbox")
        wrapped = object.__getattribute__(self, "_wrapped_object")

        if not sandbox.is_safe_attribute(wrapped, name):
            raise SecurityError(f"Setting attribute '{name}' is forbidden")

        setattr(wrapped, name, value)

    def __delattr__(self, name: str) -> None:
        sandbox = object.__getattribute__(self, "_sandbox")
        wrapped = object.__getattribute__(self, "_wrapped_object")

        if not sandbox.is_safe_attribute(wrapped, name):
            raise SecurityError(f"Deleting attribute '{name}' is forbidden")

        delattr(wrapped, name)

    def __call__(self, *args, **kwargs) -> Any:
        wrapped = object.__getattribute__(self, "_wrapped_object")
        sandbox = object.__getattribute__(self, "_sandbox")

        if not callable(wrapped):
            raise TypeError("Object is not callable")

        result = wrapped(*args, **kwargs)
        return sandbox.wrap_object(result)

    def __repr__(self) -> str:
        wrapped = object.__getattribute__(self, "_wrapped_object")
        return f"SafeProxy({repr(wrapped)})"
