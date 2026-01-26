"""
Error Handling Agent for improved exception management.

Specializes in error detection, handling improvements, and robust exception patterns.
"""

from typing import Dict, List, Any, Optional
import ast
import re
from .base_agent import (
    BaseAgent,
    AgentType,
    RefactoringSuggestion,
    SeverityLevel,
    GitIntegrationData
)


class ErrorHandlingAgent(BaseAgent):
    """
    Agent focused on error handling and exception management.

    Analyzes:
    - Exception handling patterns
    - Error detection and recovery
    - Robust error handling practices
    - Exception propagation
    - Error logging and monitoring
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(AgentType.ERROR_HANDLING, config)
        self.preferred_exception_types = self.config.get("preferred_exception_types", [
            "ValueError", "TypeError", "IndexError", "KeyError",
            "FileNotFoundError", "IOError", "RuntimeError"
        ])

    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze error handling practices."""
        suggestions = []

        for file_path, code_content in code_context.get("files", {}).items():
            if not file_path.endswith(".py"):
                continue

            suggestions.extend(self._check_bare_excepts(file_path, code_content))
            suggestions.extend(self._check_overly_broad_excepts(file_path, code_content))
            suggestions.extend(self._check_missing_error_handling(file_path, code_content))
            suggestions.extend(self._check_error_logging(file_path, code_content))
            suggestions.extend(self._check_exception_patterns(file_path, code_content))

        return suggestions

    def _check_bare_excepts(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for bare except clauses."""
        suggestions = []
        lines = code_content.split("\n")

        for i, line in enumerate(lines):
            if re.match(r'^\s*except\s*:', line) and not line.strip().startswith('#'):
                suggestions.append(RefactoringSuggestion(
                    file_path=file_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    original_code=line,
                    refactored_code="except Exception as e:  # Specify exception type",
                    description="Bare except clause found",
                    severity=SeverityLevel.CRITICAL,
                    agent_type=self.agent_type,
                    rationale="Bare except clauses catch all exceptions including system exits and keyboard interrupts",
                    estimated_impact="Prevents unintended exception catching and improves debugging",
                    tags=["error-handling", "exceptions", "critical"],
                    git_integration=GitIntegrationData(
                        file_path=file_path,
                        line_number=i + 1,
                        commit_hash=None,
                        branch_name=None,
                        diff_content=None
                    )
                ))

        return suggestions

    def _check_overly_broad_excepts(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for overly broad exception catching."""
        suggestions = []
        lines = code_content.split("\n")

        broad_exception_patterns = [
            r'except\s+Exception\s*:',
            r'except\s+\w+Error\s*:',
            r'except\s+BaseException\s*:',
        ]

        for i, line in enumerate(lines):
            for pattern in broad_exception_patterns:
                if re.match(pattern, line) and not line.strip().startswith('#'):
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code="except SpecificException as e:  # Use more specific exception",
                        description="Overly broad exception catching",
                        severity=SeverityLevel.HIGH,
                        agent_type=self.agent_type,
                        rationale="Broad exception catching can mask unexpected errors and make debugging harder",
                        estimated_impact="Better error handling specificity and debugging",
                        tags=["error-handling", "exceptions", "specificity"],
                        git_integration=GitIntegrationData(
                            file_path=file_path,
                            line_number=i + 1,
                            commit_hash=None,
                            branch_name=None,
                            diff_content=None
                        )
                    ))

        return suggestions

    def _check_missing_error_handling(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for missing error handling in critical operations."""
        suggestions = []
        lines = code_content.split("\n")

        critical_operations = [
            (r'open\(.*\)', "File operations"),
            (r'requests\.\w+\(.*\)', "HTTP requests"),
            (r'json\.loads?\(.*\)', "JSON parsing"),
            (r'yaml\.load\(.*\)', "YAML parsing"),
            (r'connect\(.*\)', "Database/network connections"),
        ]

        for i, line in enumerate(lines):
            for pattern, operation_type in critical_operations:
                if re.search(pattern, line) and not line.strip().startswith('#'):
                    # Check if there's error handling in the next few lines
                    has_error_handling = False
                    for j in range(i + 1, min(i + 6, len(lines))):
                        if re.search(r'try\s*:|except\s+|with\s+.*:', lines[j]):
                            has_error_handling = True
                            break

                    if not has_error_handling:
                        suggestions.append(RefactoringSuggestion(
                            file_path=file_path,
                            line_start=i + 1,
                            line_end=i + 1,
                            original_code=line,
                            refactored_code=f"# Add error handling for {operation_type.lower()}",
                            description=f"Missing error handling for {operation_type}",
                            severity=SeverityLevel.HIGH,
                            agent_type=self.agent_type,
                            rationale=f"{operation_type} can fail and should have proper error handling",
                            estimated_impact="Improved robustness and error recovery",
                            tags=["error-handling", "missing", operation_type.lower()],
                            git_integration=GitIntegrationData(
                                file_path=file_path,
                                line_number=i + 1,
                                commit_hash=None,
                                branch_name=None,
                                diff_content=None
                            )
                        ))

        return suggestions

    def _check_error_logging(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for proper error logging practices."""
        suggestions = []
        lines = code_content.split("\n")

        # Look for exception handling without logging
        for i, line in enumerate(lines):
            if re.match(r'^\s*except\s+\w+.*:', line) and not line.strip().startswith('#'):
                # Check if there's logging in the exception block
                has_logging = False
                indent_level = len(line) - len(line.lstrip())
                for j in range(i + 1, min(i + 11, len(lines))):
                    current_line = lines[j]
                    current_indent = len(current_line) - len(current_line.lstrip())

                    # Check if we're still in the same block
                    if current_indent <= indent_level and current_line.strip():
                        break

                    if re.search(r'logger\.\w+\(.*\)|logging\.\w+\(.*\)|print\(.*\)', current_line):
                        has_logging = True
                        break

                if not has_logging:
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code="except SpecificException as e:\n            logger.error(f\"Error occurred: {{e}}\")  # Add proper logging",
                        description="Exception handling without proper logging",
                        severity=SeverityLevel.MEDIUM,
                        agent_type=self.agent_type,
                        rationale="Proper error logging is essential for debugging and monitoring",
                        estimated_impact="Better error visibility and debugging capabilities",
                        tags=["error-handling", "logging", "monitoring"],
                        git_integration=GitIntegrationData(
                            file_path=file_path,
                            line_number=i + 1,
                            commit_hash=None,
                            branch_name=None,
                            diff_content=None
                        )
                    ))

        return suggestions

    def _check_exception_patterns(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for common exception handling patterns that could be improved."""
        suggestions = []
        lines = code_content.split("\n")

        # Look for patterns that could be improved
        improvement_patterns = [
            (r'except\s+\w+\s*:\s*pass', "Silent exception handling", "except SpecificException as e:\n    logger.warning(f\"Handled exception: {{e}}\")"),
            (r'except\s+\w+\s*:\s*return\s+None', "Return None on exception", "except SpecificException as e:\n    logger.error(f\"Failed to process: {{e}}\")\n    return None"),
            (r'except\s+\w+\s*:\s*raise', "Re-raise without context", "except SpecificException as e:\n    logger.error(f\"Error in processing: {{e}}\")\n    raise"),
        ]

        for i, line in enumerate(lines):
            for pattern, description, refactored in improvement_patterns:
                if re.match(pattern, line) and not line.strip().startswith('#'):
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code=refactored,
                        description=f"Improvable exception pattern: {description}",
                        severity=SeverityLevel.MEDIUM,
                        agent_type=self.agent_type,
                        rationale="Better exception handling patterns improve code quality and debugging",
                        estimated_impact="More robust and maintainable error handling",
                        tags=["error-handling", "patterns", "improvement"],
                        git_integration=GitIntegrationData(
                            file_path=file_path,
                            line_number=i + 1,
                            commit_hash=None,
                            branch_name=None,
                            diff_content=None
                        )
                    ))

        return suggestions

    def apply_refactoring(
        self,
        suggestion: RefactoringSuggestion,
        code_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Apply error handling refactoring."""
        # Error handling refactorings often require specific context
        return {}

    def analyze_error_patterns(
        self,
        code_content: str
    ) -> Dict[str, Any]:
        """
        Analyze code for common error patterns and suggest improvements.

        Args:
            code_content: The code content to analyze

        Returns:
            Dictionary with error pattern analysis
        """
        analysis = {
            "bare_excepts": [],
            "broad_excepts": [],
            "missing_handling": [],
            "logging_issues": [],
            "pattern_improvements": []
        }

        lines = code_content.split("\n")

        # Analyze each line for error patterns
        for i, line in enumerate(lines):
            line_num = i + 1

            # Check for bare excepts
            if re.match(r'^\s*except\s*:', line):
                analysis["bare_excepts"].append(line_num)

            # Check for broad excepts
            if re.search(r'except\s+(Exception|BaseException)\s*:', line):
                analysis["broad_excepts"].append(line_num)

            # Check for critical operations without error handling
            critical_ops = [
                r'open\(.*\)',
                r'requests\.\w+\(.*\)',
                r'json\.loads?\(.*\)',
                r'connect\(.*\)'
            ]

            for op_pattern in critical_ops:
                if re.search(op_pattern, line):
                    # Simple check - in real implementation would look ahead for try/except
                    analysis["missing_handling"].append({
                        "line": line_num,
                        "pattern": op_pattern
                    })

        return analysis

    def suggest_robust_error_handling(
        self,
        operation_type: str
    ) -> str:
        """
        Suggest robust error handling for a specific operation type.

        Args:
            operation_type: Type of operation (file, network, json, etc.)

        Returns:
            Suggested error handling code
        """
        suggestions = {
            "file": """try:
    with open(filename, 'r') as f:
        content = f.read()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    raise
except IOError as e:
    logger.error(f"I/O error reading file: {e}")
    raise""",

            "network": """try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    logger.error(f"Network request failed: {e}")
    return None
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse JSON response: {e}")
    return None""",

            "json": """try:
    data = json.loads(json_string)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON format: {e}")
    return None
except TypeError as e:
    logger.error(f"Invalid input type for JSON parsing: {e}")
    return None"""
        }

        return suggestions.get(operation_type, """try:
    # Your operation here
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # Handle or re-raise as appropriate""")
