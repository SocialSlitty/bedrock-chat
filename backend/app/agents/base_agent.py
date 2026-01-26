"""
Base Agent class for refactoring operations.

Provides the foundation for specialized refactoring agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypedDict
from enum import Enum
import logging


class AgentType(Enum):
    """Types of refactoring agents."""
    STRUCTURE = "structure"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    BEST_PRACTICES = "best_practices"
    GIT_INTEGRATION = "git_integration"
    ERROR_HANDLING = "error_handling"

    def description(self) -> str:
        """Get human-readable description of agent type."""
        descriptions = {
            "structure": "Analyzes code structure and organization",
            "performance": "Optimizes code performance and efficiency",
            "readability": "Improves code readability and maintainability",
            "best_practices": "Ensures adherence to coding best practices",
            "git_integration": "Handles Git operations and version control",
            "error_handling": "Enhances error detection and handling"
        }
        return descriptions.get(self.value, f"Agent for {self.value}")


class SeverityLevel(Enum):
    """Severity levels for refactoring suggestions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RefactoringPriority(Enum):
    """Priority ordering for synthesized suggestions."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class GitIntegrationData(TypedDict):
    """Data structure for Git integration information."""
    file_path: str
    line_number: int
    commit_hash: Optional[str]
    branch_name: Optional[str]
    diff_content: Optional[str]

class AgentPerformanceMetrics(TypedDict):
    """Performance metrics for agent execution."""
    execution_time_ms: float
    suggestions_generated: int
    suggestions_applied: int
    error_rate: float


@dataclass
class RefactoringSuggestion:
    """Represents a single refactoring suggestion."""

    file_path: str
    line_start: int
    line_end: int
    original_code: str
    refactored_code: str
    description: str
    severity: SeverityLevel
    agent_type: AgentType
    rationale: str
    estimated_impact: str
    priority: RefactoringPriority = RefactoringPriority.MEDIUM
    code_changes: Optional[Dict[str, str]] = None
    git_integration: Optional[GitIntegrationData] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from an agent's refactoring pass."""
    
    agent_type: AgentType
    suggestions: List[RefactoringSuggestion]
    summary: str
    metrics: Dict[str, Any]
    execution_time: float
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Abstract base class for refactoring agents.
    
    Each agent specializes in a specific dimension of code quality
    and provides targeted refactoring suggestions.
    """
    
    def __init__(self, agent_type: AgentType, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            agent_type: The type of refactoring this agent performs
            config: Optional configuration dictionary
        """
        self.agent_type = agent_type
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{agent_type.value}")
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize agent-specific resources. Override in subclasses."""
        pass
    
    @abstractmethod
    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """
        Analyze code and generate refactoring suggestions.
        
        Args:
            code_context: Dictionary containing code files, metadata, and context
            
        Returns:
            List of refactoring suggestions
        """
        pass
    
    @abstractmethod
    def apply_refactoring(
        self,
        suggestion: RefactoringSuggestion,
        code_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Apply a refactoring suggestion to the code.
        
        Args:
            suggestion: The refactoring suggestion to apply
            code_context: Current code context
            
        Returns:
            Dictionary mapping file paths to updated code
        """
        pass
    
    def validate_suggestion(self, suggestion: RefactoringSuggestion) -> bool:
        """
        Validate that a suggestion is safe to apply.
        
        Args:
            suggestion: The suggestion to validate
            
        Returns:
            True if the suggestion is valid and safe
        """
        # Basic validation - override in subclasses for specific checks
        return bool(
            suggestion.file_path and
            suggestion.line_start > 0 and
            suggestion.line_end >= suggestion.line_start and
            suggestion.original_code and
            suggestion.refactored_code
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about the agent's performance.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "agent_type": self.agent_type.value,
            "config": self.config,
        }
    
    def execute(self, code_context: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's refactoring pass.
        
        Args:
            code_context: Dictionary containing code files and metadata
            
        Returns:
            AgentResult containing suggestions and metrics
        """
        import time
        
        start_time = time.time()
        errors = []
        warnings = []
        suggestions = []
        
        try:
            self.logger.info(f"Starting {self.agent_type.value} analysis")
            suggestions = self.analyze(code_context)
            
            # Validate suggestions
            valid_suggestions = []
            for suggestion in suggestions:
                if self.validate_suggestion(suggestion):
                    valid_suggestions.append(suggestion)
                else:
                    warnings.append(
                        f"Invalid suggestion for {suggestion.file_path}:"
                        f"{suggestion.line_start}-{suggestion.line_end}"
                    )
            
            suggestions = valid_suggestions
            execution_time = time.time() - start_time
            
            summary = self._generate_summary(suggestions)
            metrics = self.get_metrics()
            metrics.update({
                "suggestions_count": len(suggestions),
                "execution_time": execution_time,
            })
            
            self.logger.info(
                f"Completed {self.agent_type.value} analysis: "
                f"{len(suggestions)} suggestions in {execution_time:.2f}s"
            )
            
            return AgentResult(
                agent_type=self.agent_type,
                suggestions=suggestions,
                summary=summary,
                metrics=metrics,
                execution_time=execution_time,
                success=True,
                errors=errors,
                warnings=warnings,
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error in {self.agent_type.value} agent: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            
            return AgentResult(
                agent_type=self.agent_type,
                suggestions=[],
                summary=f"Agent failed: {str(e)}",
                metrics=self.get_metrics(),
                execution_time=execution_time,
                success=False,
                errors=errors,
                warnings=warnings,
            )
    
    def _generate_summary(self, suggestions: List[RefactoringSuggestion]) -> str:
        """Generate a summary of the refactoring suggestions."""
        if not suggestions:
            return f"No {self.agent_type.value} improvements found."

        severity_counts = {}
        for suggestion in suggestions:
            severity = suggestion.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        summary_parts = [
            f"Found {len(suggestions)} {self.agent_type.value} improvements:"
        ]
        for severity, count in sorted(severity_counts.items()):
            summary_parts.append(f"  - {count} {severity} severity")

        return "\n".join(summary_parts)
