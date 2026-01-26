"""
Git Integration Agent for version control operations.

Handles Git operations and version control integration for the refactoring system.
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


class GitIntegrationAgent(BaseAgent):
    """
    Agent focused on Git integration and version control.

    Analyzes:
    - Git commit history and patterns
    - Branch management
    - Version control best practices
    - Commit message quality
    - Git workflow compliance
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(AgentType.GIT_INTEGRATION, config)
        self.max_commit_message_length = self.config.get("max_commit_message_length", 72)
        self.preferred_commit_patterns = self.config.get("preferred_commit_patterns", [
            r'^[a-z]+: .+',  # conventional commits pattern
            r'^[A-Z][a-z]+: .+',  # GitHub-style pattern
        ])

    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze Git integration and version control practices."""
        suggestions = []

        # Analyze Git-related aspects in the code
        for file_path, code_content in code_context.get("files", {}).items():
            if not file_path.endswith(".py"):
                continue

            suggestions.extend(self._check_git_operations(file_path, code_content))
            suggestions.extend(self._check_commit_patterns(file_path, code_content))
            suggestions.extend(self._check_version_control(file_path, code_content))

        return suggestions

    def _check_git_operations(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for proper Git operations in code."""
        suggestions = []
        lines = code_content.split("\n")

        # Look for Git command patterns that might need improvement
        git_patterns = [
            (r'subprocess\.run\(.*git.*\)', "Direct Git command execution"),
            (r'os\.system\(.*git.*\)', "Git commands via os.system"),
            (r'Popen\(.*git.*\)', "Git commands via Popen"),
        ]

        for i, line in enumerate(lines):
            for pattern, description in git_patterns:
                if re.search(pattern, line) and not line.strip().startswith('#'):
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code="# Consider using GitPython library for safer Git operations",
                        description=f"Direct Git command: {description}",
                        severity=SeverityLevel.MEDIUM,
                        agent_type=self.agent_type,
                        rationale="Direct Git commands can be unsafe and platform-dependent",
                        estimated_impact="Improved safety and cross-platform compatibility",
                        tags=["git-operations", "safety"],
                        git_integration=GitIntegrationData(
                            file_path=file_path,
                            line_number=i + 1,
                            commit_hash=None,
                            branch_name=None,
                            diff_content=None
                        )
                    ))

        return suggestions

    def _check_commit_patterns(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for commit message patterns and conventions."""
        suggestions = []
        lines = code_content.split("\n")

        # Look for commit message related code
        commit_patterns = [
            (r'commit.*message.*=', "Commit message assignment"),
            (r'git\.commit\(.*message.*\)', "Git commit with message"),
        ]

        for i, line in enumerate(lines):
            for pattern, description in commit_patterns:
                if re.search(pattern, line, re.IGNORECASE) and not line.strip().startswith('#'):
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code="# Ensure commit messages follow conventional commit patterns",
                        description=f"Commit message pattern: {description}",
                        severity=SeverityLevel.LOW,
                        agent_type=self.agent_type,
                        rationale="Consistent commit messages improve project maintainability",
                        estimated_impact="Better Git history and team collaboration",
                        tags=["commit-messages", "conventions"],
                        git_integration=GitIntegrationData(
                            file_path=file_path,
                            line_number=i + 1,
                            commit_hash=None,
                            branch_name=None,
                            diff_content=None
                        )
                    ))

        return suggestions

    def _check_version_control(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for version control best practices."""
        suggestions = []
        lines = code_content.split("\n")

        # Look for version control related patterns
        version_patterns = [
            (r'\.gitignore', "Gitignore file operations"),
            (r'\.gitattributes', "Gitattributes file operations"),
            (r'git.*branch', "Branch operations"),
            (r'git.*tag', "Tag operations"),
        ]

        for i, line in enumerate(lines):
            for pattern, description in version_patterns:
                if re.search(pattern, line, re.IGNORECASE) and not line.strip().startswith('#'):
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code="# Follow Git best practices for version control operations",
                        description=f"Version control pattern: {description}",
                        severity=SeverityLevel.LOW,
                        agent_type=self.agent_type,
                        rationale="Proper version control practices improve project quality",
                        estimated_impact="Better version control management",
                        tags=["version-control", "best-practices"],
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
        """Apply Git integration refactoring."""
        # Git integration refactorings often require specific context
        return {}

    def create_git_commit(
        self,
        file_path: str,
        changes: Dict[str, str],
        commit_message: str
    ) -> Dict[str, Any]:
        """
        Create a Git commit for the applied refactoring changes.

        Args:
            file_path: The main file being refactored
            changes: Dictionary of file paths to their updated content
            commit_message: The commit message to use

        Returns:
            Dictionary containing commit information
        """
        # In a real implementation, this would use GitPython or similar
        # to actually create a commit. For now, we return a mock response.

        return {
            "success": True,
            "commit_hash": "mock_commit_hash_12345",
            "message": commit_message,
            "files_changed": list(changes.keys()),
            "timestamp": "2023-01-01T00:00:00Z"
        }

    def generate_commit_message(
        self,
        suggestions: List[RefactoringSuggestion]
    ) -> str:
        """
        Generate a meaningful commit message based on refactoring suggestions.

        Args:
            suggestions: List of refactoring suggestions being applied

        Returns:
            Generated commit message
        """
        if not suggestions:
            return "Refactor: Apply code improvements"

        # Group suggestions by type
        by_type = {}
        for suggestion in suggestions:
            agent_type = suggestion.agent_type.value.replace("_", " ")
            by_type[agent_type] = by_type.get(agent_type, 0) + 1

        # Generate message parts
        parts = []
        for agent_type, count in by_type.items():
            parts.append(f"{count} {agent_type} improvement(s)")

        if len(parts) == 1:
            return f"Refactor: {parts[0]}"
        else:
            return f"Refactor: {' and '.join(parts)}"

    def get_git_integration_data(
        self,
        file_path: str,
        line_number: int
    ) -> GitIntegrationData:
        """
        Get Git integration data for a specific file and line.

        Args:
            file_path: Path to the file
            line_number: Line number in the file

        Returns:
            Git integration data
        """
        # In a real implementation, this would query Git for actual data
        return GitIntegrationData(
            file_path=file_path,
            line_number=line_number,
            commit_hash="current_commit_hash",
            branch_name="main",
            diff_content=None
        )
