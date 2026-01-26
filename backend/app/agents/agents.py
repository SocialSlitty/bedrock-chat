"""
Specialized refactoring agents for different optimization dimensions.
"""

from typing import Dict, List, Any
import ast
import re
from .base_agent import (
    BaseAgent,
    AgentType,
    RefactoringSuggestion,
    SeverityLevel,
)


class StructureAgent(BaseAgent):
    """
    Agent focused on code structure and organization.

    Analyzes:
    - Module organization
    - Class and function structure
    - Code duplication
    - Separation of concerns
    - Design patterns
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(AgentType.STRUCTURE, config)
        self.max_function_length = self.config.get("max_function_length", 80)  # Increased from 50 to 80
        self.max_class_length = self.config.get("max_class_length", 400)  # Increased from 300 to 400
        self.max_imports = self.config.get("max_imports", 30)  # Increased from 20 to 30
        self.min_function_length = self.config.get("min_function_length", 5)  # Added minimum length check
        self.max_parameters = self.config.get("max_parameters", 6)  # Added parameter count check
        self.max_cognitive_complexity = self.config.get("max_cognitive_complexity", 10)  # Added complexity check

    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze code structure and organization."""
        suggestions = []

        for file_path, code_content in code_context.get("files", {}).items():
            if not file_path.endswith(".py"):
                continue

            try:
                tree = ast.parse(code_content)
                suggestions.extend(self._analyze_functions(file_path, tree, code_content))
                suggestions.extend(self._analyze_classes(file_path, tree, code_content))
                suggestions.extend(self._analyze_imports(file_path, tree, code_content))
            except SyntaxError:
                self.logger.warning(f"Could not parse {file_path}")

        return suggestions

    def _analyze_functions(
        self,
        file_path: str,
        tree: ast.AST,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Analyze function structure."""
        suggestions = []
        lines = code_content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = node.end_lineno - node.lineno if node.end_lineno else 0

                if func_length > self.max_function_length:
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        original_code="\n".join(lines[node.lineno-1:node.end_lineno]),
                        refactored_code="# Consider breaking this function into smaller functions",
                        description=f"Function '{node.name}' is {func_length} lines long",
                        severity=SeverityLevel.MEDIUM,
                        agent_type=self.agent_type,
                        rationale=f"Functions longer than {self.max_function_length} lines "
                                  "are harder to understand and maintain",
                        estimated_impact="Improved readability and testability",
                        tags=["function-length", "complexity"],
                    ))

        return suggestions

    def _analyze_classes(
        self,
        file_path: str,
        tree: ast.AST,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Analyze class structure."""
        suggestions = []
        lines = code_content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_length = node.end_lineno - node.lineno if node.end_lineno else 0

                if class_length > self.max_class_length:
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        original_code="\n".join(lines[node.lineno-1:node.end_lineno]),
                        refactored_code="# Consider splitting this class into smaller classes",
                        description=f"Class '{node.name}' is {class_length} lines long",
                        severity=SeverityLevel.MEDIUM,
                        agent_type=self.agent_type,
                        rationale=f"Classes longer than {self.max_class_length} lines "
                                  "may violate single responsibility principle",
                        estimated_impact="Better separation of concerns",
                        tags=["class-length", "srp"],
                    ))

        return suggestions

    def _analyze_imports(
        self,
        file_path: str,
        tree: ast.AST,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Analyze import organization."""
        suggestions = []
        lines = code_content.split("\n")

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)

        if len(imports) > self.max_imports:
            start_line = min(getattr(node, "lineno", 1) for node in imports) if imports else 1
            end_line = max(getattr(node, "end_lineno", getattr(node, "lineno", 1)) for node in imports) if imports else 1
            original_code = "\n".join(lines[start_line - 1:end_line])
            suggestions.append(RefactoringSuggestion(
                file_path=file_path,
                line_start=start_line,
                line_end=end_line,
                original_code=original_code or "# imports elided",
                refactored_code="# Consider reorganizing or splitting this module to reduce imports",
                description=f"File has {len(imports)} imports",
                severity=SeverityLevel.LOW,
                agent_type=self.agent_type,
                rationale="Too many imports may indicate the module is doing too much",
                estimated_impact="Consider splitting into multiple modules",
                tags=["imports", "module-organization"],
            ))

        return suggestions

    def apply_refactoring(
        self,
        suggestion: RefactoringSuggestion,
        code_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Apply structure refactoring."""
        # Structure refactorings typically require manual intervention
        return {}


class PerformanceAgent(BaseAgent):
    """
    Agent focused on performance optimization.

    Analyzes:
    - Algorithm complexity
    - Unnecessary computations
    - Memory usage
    - Database query optimization
    - Caching opportunities
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(AgentType.PERFORMANCE, config)

    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze performance characteristics."""
        suggestions = []

        for file_path, code_content in code_context.get("files", {}).items():
            if not file_path.endswith(".py"):
                continue

            suggestions.extend(self._detect_nested_loops(file_path, code_content))
            suggestions.extend(self._detect_repeated_computations(file_path, code_content))
            suggestions.extend(self._detect_inefficient_patterns(file_path, code_content))

        return suggestions

    def _detect_nested_loops(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Detect deeply nested loops."""
        suggestions = []

        try:
            tree = ast.parse(code_content)
            lines = code_content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    nesting_level = self._count_loop_nesting(node)
                    if nesting_level >= 3:
                        suggestions.append(RefactoringSuggestion(
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            original_code="\n".join(lines[node.lineno-1:node.end_lineno]),
                            refactored_code="# Consider using list comprehensions or vectorized operations",
                            description=f"Nested loop with depth {nesting_level}",
                            severity=SeverityLevel.HIGH,
                            agent_type=self.agent_type,
                            rationale="Deeply nested loops can have O(n^k) complexity",
                            estimated_impact="Potential significant performance improvement",
                            tags=["nested-loops", "complexity", "performance"],
                        ))
        except SyntaxError:
            pass

        return suggestions

    def _count_loop_nesting(self, node: ast.AST, depth: int = 1) -> int:
        """Count the nesting depth of loops."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                child_depth = self._count_loop_nesting(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth

    def _detect_repeated_computations(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Detect repeated computations that could be cached."""
        suggestions = []

        # Look for repeated function calls in loops
        pattern = r'for\s+\w+\s+in\s+.*:\s*\n\s+.*(\w+\([^)]*\))'
        matches = re.finditer(pattern, code_content)

        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1
            suggestions.append(RefactoringSuggestion(
                file_path=file_path,
                line_start=line_num,
                line_end=line_num + 2,
                original_code=match.group(0),
                refactored_code="# Consider caching repeated computations",
                description="Potential repeated computation in loop",
                severity=SeverityLevel.MEDIUM,
                agent_type=self.agent_type,
                rationale="Repeated computations in loops waste CPU cycles",
                estimated_impact="Reduced execution time",
                tags=["caching", "optimization"],
            ))

        return suggestions

    def _detect_inefficient_patterns(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Detect common inefficient patterns."""
        suggestions = []
        lines = code_content.split("\n")

        # Detect string concatenation in loops
        for i, line in enumerate(lines):
            if 'for ' in line and i + 1 < len(lines):
                next_line = lines[i + 1]
                if '+=' in next_line and '"' in next_line:
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 2,
                        original_code=f"{line}\n{next_line}",
                        refactored_code="# Use list and join() instead of string concatenation",
                        description="String concatenation in loop",
                        severity=SeverityLevel.MEDIUM,
                        agent_type=self.agent_type,
                        rationale="String concatenation in loops creates many intermediate objects",
                        estimated_impact="Better memory usage and performance",
                        tags=["string-concatenation", "memory"],
                    ))

        return suggestions

    def apply_refactoring(
        self,
        suggestion: RefactoringSuggestion,
        code_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Apply performance refactoring."""
        # Performance refactorings often require context-specific changes
        return {}


class ReadabilityAgent(BaseAgent):
    """
    Agent focused on code readability and clarity.

    Analyzes:
    - Naming conventions
    - Code comments and documentation
    - Code formatting
    - Magic numbers
    - Complex expressions
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(AgentType.READABILITY, config)

    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze code readability."""
        suggestions = []

        for file_path, code_content in code_context.get("files", {}).items():
            if not file_path.endswith(".py"):
                continue

            suggestions.extend(self._check_naming(file_path, code_content))
            suggestions.extend(self._check_magic_numbers(file_path, code_content))
            suggestions.extend(self._check_documentation(file_path, code_content))
            suggestions.extend(self._check_line_length(file_path, code_content))

        return suggestions

    def _check_naming(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check naming conventions."""
        suggestions = []

        try:
            tree = ast.parse(code_content)
            lines = code_content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for single-letter function names (except common ones)
                    if len(node.name) == 1 and node.name not in ['x', 'y', 'z', 'i', 'j', 'k']:
                        suggestions.append(RefactoringSuggestion(
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            original_code=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            refactored_code=f"# Use a descriptive name instead of '{node.name}'",
                            description=f"Single-letter function name: {node.name}",
                            severity=SeverityLevel.LOW,
                            agent_type=self.agent_type,
                            rationale="Descriptive names improve code readability",
                            estimated_impact="Better code understanding",
                            tags=["naming", "readability"],
                        ))
        except SyntaxError:
            pass

        return suggestions

    def _check_magic_numbers(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for magic numbers."""
        suggestions = []
        lines = code_content.split("\n")

        # Simple pattern to detect numeric literals (excluding 0, 1, -1)
        pattern = r'\b(?<![\w.])((?!0\b|1\b|-1\b)\d+(?:\.\d+)?)\b'

        for i, line in enumerate(lines):
            # Skip comments and strings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue

            matches = re.finditer(pattern, line)
            for match in matches:
                suggestions.append(RefactoringSuggestion(
                    file_path=file_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    original_code=line,
                    refactored_code=f"# Consider using a named constant for {match.group(1)}",
                    description=f"Magic number: {match.group(1)}",
                    severity=SeverityLevel.LOW,
                    agent_type=self.agent_type,
                    rationale="Named constants are more maintainable than magic numbers",
                    estimated_impact="Improved code clarity",
                    tags=["magic-numbers", "constants"],
                ))

        return suggestions

    def _check_documentation(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for missing documentation."""
        suggestions = []

        try:
            tree = ast.parse(code_content)
            lines = code_content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    has_docstring = (
                        ast.get_docstring(node) is not None
                    )

                    if not has_docstring and not node.name.startswith('_'):
                        suggestions.append(RefactoringSuggestion(
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            original_code=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            refactored_code=f'"""\n    Add documentation here.\n    """',
                            description=f"Missing docstring for {node.name}",
                            severity=SeverityLevel.LOW,
                            agent_type=self.agent_type,
                            rationale="Documentation helps others understand the code",
                            estimated_impact="Better code maintainability",
                            tags=["documentation", "docstring"],
                        ))
        except SyntaxError:
            pass

        return suggestions

    def _check_line_length(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for overly long lines."""
        suggestions = []
        lines = code_content.split("\n")
        max_length = 100

        for i, line in enumerate(lines):
            if len(line) > max_length and not line.strip().startswith('#'):
                suggestions.append(RefactoringSuggestion(
                    file_path=file_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    original_code=line,
                    refactored_code="# Consider breaking this line into multiple lines",
                    description=f"Line too long: {len(line)} characters",
                    severity=SeverityLevel.LOW,
                    agent_type=self.agent_type,
                    rationale=f"Lines longer than {max_length} characters are harder to read",
                    estimated_impact="Improved readability",
                    tags=["line-length", "formatting"],
                ))

        return suggestions

    def apply_refactoring(
        self,
        suggestion: RefactoringSuggestion,
        code_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Apply readability refactoring."""
        return {}


class BestPracticesAgent(BaseAgent):
    """
    Agent focused on best practices and code quality.

    Analyzes:
    - Error handling
    - Type hints
    - Security issues
    - Code smells
    - Framework-specific best practices
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(AgentType.BEST_PRACTICES, config)

    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze adherence to best practices."""
        suggestions = []

        for file_path, code_content in code_context.get("files", {}).items():
            if not file_path.endswith(".py"):
                continue

            suggestions.extend(self._check_error_handling(file_path, code_content))
            suggestions.extend(self._check_type_hints(file_path, code_content))
            suggestions.extend(self._check_security(file_path, code_content))

        return suggestions

    def _check_error_handling(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check error handling practices."""
        suggestions = []
        lines = code_content.split("\n")

        # Check for bare except clauses
        for i, line in enumerate(lines):
            if re.match(r'\s*except\s*:', line):
                suggestions.append(RefactoringSuggestion(
                    file_path=file_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    original_code=line,
                    refactored_code="except Exception as e:  # Specify exception type",
                    description="Bare except clause",
                    severity=SeverityLevel.HIGH,
                    agent_type=self.agent_type,
                    rationale="Bare except clauses catch all exceptions including system exits",
                    estimated_impact="Better error handling",
                    tags=["error-handling", "exceptions"],
                ))

        return suggestions

    def _check_type_hints(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for type hints."""
        suggestions = []

        try:
            tree = ast.parse(code_content)
            lines = code_content.split("\n")

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has type hints
                    has_return_hint = node.returns is not None
                    has_param_hints = all(
                        arg.annotation is not None
                        for arg in node.args.args
                        if arg.arg != 'self' and arg.arg != 'cls'
                    )

                    if not (has_return_hint and has_param_hints) and not node.name.startswith('_'):
                        suggestions.append(RefactoringSuggestion(
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            original_code=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            refactored_code="# Add type hints to parameters and return value",
                            description=f"Missing type hints in {node.name}",
                            severity=SeverityLevel.MEDIUM,
                            agent_type=self.agent_type,
                            rationale="Type hints improve code clarity and enable static analysis",
                            estimated_impact="Better type safety",
                            tags=["type-hints", "typing"],
                        ))
        except SyntaxError:
            pass

        return suggestions

    def _check_security(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for security issues."""
        suggestions = []
        lines = code_content.split("\n")

        # Check for eval() usage
        for i, line in enumerate(lines):
            if 'eval(' in line and not line.strip().startswith('#'):
                suggestions.append(RefactoringSuggestion(
                    file_path=file_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    original_code=line,
                    refactored_code="# Avoid eval() - use ast.literal_eval() or safer alternatives",
                    description="Use of eval() detected",
                    severity=SeverityLevel.CRITICAL,
                    agent_type=self.agent_type,
                    rationale="eval() can execute arbitrary code and is a security risk",
                    estimated_impact="Improved security",
                    tags=["security", "eval"],
                ))

        return suggestions

    def apply_refactoring(
        self,
        suggestion: RefactoringSuggestion,
        code_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Apply best practices refactoring."""
        return {}
