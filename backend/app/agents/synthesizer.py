"""
Result synthesizer for combining multi-agent refactoring suggestions.
"""

from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import difflib

from .base_agent import (
    AgentResult,
    RefactoringSuggestion,
    RefactoringPriority,
    AgentType,
)


@dataclass
class ConflictResolution:
    """Represents a resolved conflict between suggestions."""
    
    conflicting_suggestions: List[RefactoringSuggestion]
    resolved_suggestion: RefactoringSuggestion
    resolution_strategy: str
    rationale: str


@dataclass
class SynthesizedResult:
    """Combined result from multiple agents."""
    
    suggestions: List[RefactoringSuggestion]
    conflicts: List[ConflictResolution]
    agent_results: List[AgentResult]
    summary: str
    metrics: Dict[str, Any]
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ResultSynthesizer:
    """
    Synthesizes results from multiple refactoring agents.
    
    Handles:
    - Conflict detection and resolution
    - Priority-based suggestion ranking
    - Deduplication
    - Impact analysis
    """
    
    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize the synthesizer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.conflict_strategy = self.config.get("conflict_strategy", "priority")
    
    def synthesize(self, agent_results: List[AgentResult]) -> SynthesizedResult:
        """
        Synthesize results from multiple agents.
        
        Args:
            agent_results: List of results from different agents
            
        Returns:
            SynthesizedResult containing combined suggestions
        """
        errors = []
        warnings = []
        
        # Collect all suggestions
        all_suggestions = []
        for result in agent_results:
            if result.success:
                all_suggestions.extend(result.suggestions)
            else:
                errors.extend(result.errors)
            warnings.extend(result.warnings)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(all_suggestions)
        
        # Resolve conflicts
        resolved_conflicts = [
            self._resolve_conflict(conflict) for conflict in conflicts
        ]
        
        # Get non-conflicting suggestions
        conflicting_ids = set()
        for conflict in conflicts:
            conflicting_ids.update(id(s) for s in conflict)
        
        non_conflicting = [
            s for s in all_suggestions
            if id(s) not in conflicting_ids
        ]
        
        # Combine resolved and non-conflicting suggestions
        final_suggestions = non_conflicting + [
            rc.resolved_suggestion for rc in resolved_conflicts
        ]
        
        # Sort by priority
        final_suggestions = self._sort_by_priority(final_suggestions)
        
        # Deduplicate
        final_suggestions = self._deduplicate(final_suggestions)
        
        # Generate summary
        summary = self._generate_summary(final_suggestions, resolved_conflicts, agent_results)
        
        # Calculate metrics
        metrics = self._calculate_metrics(final_suggestions, agent_results)
        
        success = all(r.success for r in agent_results)
        
        return SynthesizedResult(
            suggestions=final_suggestions,
            conflicts=resolved_conflicts,
            agent_results=agent_results,
            summary=summary,
            metrics=metrics,
            success=success,
            errors=errors,
            warnings=warnings,
        )
    
    def _detect_conflicts(
        self,
        suggestions: List[RefactoringSuggestion]
    ) -> List[List[RefactoringSuggestion]]:
        """
        Detect conflicting suggestions.
        
        Suggestions conflict if they modify overlapping code regions.
        """
        conflicts = []
        
        # Group by file
        by_file: Dict[str, List[RefactoringSuggestion]] = defaultdict(list)
        for suggestion in suggestions:
            by_file[suggestion.file_path].append(suggestion)
        
        # Check for overlaps within each file
        for file_path, file_suggestions in by_file.items():
            for i, s1 in enumerate(file_suggestions):
                conflicting_group = [s1]
                
                for s2 in file_suggestions[i+1:]:
                    if self._ranges_overlap(
                        (s1.line_start, s1.line_end),
                        (s2.line_start, s2.line_end)
                    ):
                        conflicting_group.append(s2)
                
                if len(conflicting_group) > 1:
                    conflicts.append(conflicting_group)
        
        return conflicts
    
    def _ranges_overlap(
        self,
        range1: Tuple[int, int],
        range2: Tuple[int, int]
    ) -> bool:
        """Check if two line ranges overlap."""
        return not (range1[1] < range2[0] or range2[1] < range1[0])
    
    def _resolve_conflict(
        self,
        conflicting_suggestions: List[RefactoringSuggestion]
    ) -> ConflictResolution:
        """
        Resolve a conflict between suggestions.
        
        Strategies:
        - priority: Choose highest priority suggestion
        - merge: Attempt to merge suggestions
        - agent_order: Prefer certain agent types
        """
        if self.conflict_strategy == "priority":
            return self._resolve_by_priority(conflicting_suggestions)
        elif self.conflict_strategy == "merge":
            return self._resolve_by_merge(conflicting_suggestions)
        else:
            return self._resolve_by_priority(conflicting_suggestions)
    
    def _resolve_by_priority(
        self,
        suggestions: List[RefactoringSuggestion]
    ) -> ConflictResolution:
        """Resolve conflict by choosing highest priority suggestion."""
        priority_order = [
            RefactoringPriority.CRITICAL,
            RefactoringPriority.HIGH,
            RefactoringPriority.MEDIUM,
            RefactoringPriority.LOW,
            RefactoringPriority.INFO,
        ]
        
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: priority_order.index(s.priority)
        )
        
        chosen = sorted_suggestions[0]
        
        return ConflictResolution(
            conflicting_suggestions=suggestions,
            resolved_suggestion=chosen,
            resolution_strategy="priority",
            rationale=f"Chose {chosen.agent_type.value} suggestion with "
                      f"{chosen.priority.value} priority",
        )
    
    def _resolve_by_merge(
        self,
        suggestions: List[RefactoringSuggestion]
    ) -> ConflictResolution:
        """Attempt to merge conflicting suggestions."""
        # For now, fall back to priority-based resolution
        # True merging would require sophisticated code analysis
        return self._resolve_by_priority(suggestions)
    
    def _sort_by_priority(
        self,
        suggestions: List[RefactoringSuggestion]
    ) -> List[RefactoringSuggestion]:
        """Sort suggestions by priority."""
        priority_order = {
            RefactoringPriority.CRITICAL: 0,
            RefactoringPriority.HIGH: 1,
            RefactoringPriority.MEDIUM: 2,
            RefactoringPriority.LOW: 3,
            RefactoringPriority.INFO: 4,
        }
        
        return sorted(
            suggestions,
            key=lambda s: (priority_order[s.priority], s.file_path, s.line_start)
        )
    
    def _deduplicate(
        self,
        suggestions: List[RefactoringSuggestion]
    ) -> List[RefactoringSuggestion]:
        """Remove duplicate suggestions."""
        seen: Set[Tuple[str, int, int, str]] = set()
        unique = []
        
        for suggestion in suggestions:
            key = (
                suggestion.file_path,
                suggestion.line_start,
                suggestion.line_end,
                suggestion.description,
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(suggestion)
        
        return unique
    
    def _generate_summary(
        self,
        suggestions: List[RefactoringSuggestion],
        conflicts: List[ConflictResolution],
        agent_results: List[AgentResult]
    ) -> str:
        """Generate a summary of the synthesized results."""
        lines = ["Multi-Agent Refactoring Analysis Complete", "=" * 50, ""]
        
        # Agent execution summary
        lines.append("Agent Execution:")
        for result in agent_results:
            status = "✓" if result.success else "✗"
            lines.append(
                f"  {status} {result.agent_type.value}: "
                f"{len(result.suggestions)} suggestions in {result.execution_time:.2f}s"
            )
        lines.append("")
        
        # Suggestions by priority
        lines.append("Suggestions by Priority:")
        by_priority: Dict[RefactoringPriority, int] = defaultdict(int)
        for suggestion in suggestions:
            by_priority[suggestion.priority] += 1
        
        for priority in RefactoringPriority:
            count = by_priority.get(priority, 0)
            if count > 0:
                lines.append(f"  {priority.value.upper()}: {count}")
        lines.append("")
        
        # Suggestions by agent
        lines.append("Suggestions by Agent:")
        by_agent: Dict[AgentType, int] = defaultdict(int)
        for suggestion in suggestions:
            by_agent[suggestion.agent_type] += 1
        
        for agent_type in AgentType:
            count = by_agent.get(agent_type, 0)
            if count > 0:
                lines.append(f"  {agent_type.value}: {count}")
        lines.append("")
        
        # Conflicts
        if conflicts:
            lines.append(f"Conflicts Resolved: {len(conflicts)}")
            lines.append("")
        
        # Total
        lines.append(f"Total Suggestions: {len(suggestions)}")
        
        return "\n".join(lines)
    
    def _calculate_metrics(
        self,
        suggestions: List[RefactoringSuggestion],
        agent_results: List[AgentResult]
    ) -> Dict[str, Any]:
        """Calculate metrics about the synthesized results."""
        by_priority = defaultdict(int)
        by_agent = defaultdict(int)
        by_file = defaultdict(int)
        
        for suggestion in suggestions:
            by_priority[suggestion.priority.value] += 1
            by_agent[suggestion.agent_type.value] += 1
            by_file[suggestion.file_path] += 1
        
        total_time = sum(r.execution_time for r in agent_results)
        
        return {
            "total_suggestions": len(suggestions),
            "by_priority": dict(by_priority),
            "by_agent": dict(by_agent),
            "by_file": dict(by_file),
            "total_execution_time": total_time,
            "agents_executed": len(agent_results),
            "agents_succeeded": sum(1 for r in agent_results if r.success),
        }
    
    def generate_report(self, result: SynthesizedResult) -> str:
        """
        Generate a detailed report of the synthesized results.
        
        Args:
            result: The synthesized result
            
        Returns:
            Formatted report string
        """
        lines = [result.summary, "", "Detailed Suggestions:", "=" * 50, ""]
        
        for i, suggestion in enumerate(result.suggestions, 1):
            lines.append(f"{i}. [{suggestion.priority.value.upper()}] "
                        f"{suggestion.file_path}:{suggestion.line_start}")
            lines.append(f"   Agent: {suggestion.agent_type.value}")
            lines.append(f"   Description: {suggestion.description}")
            lines.append(f"   Rationale: {suggestion.rationale}")
            lines.append(f"   Impact: {suggestion.estimated_impact}")
            if suggestion.tags:
                lines.append(f"   Tags: {', '.join(suggestion.tags)}")
            lines.append("")
        
        if result.conflicts:
            lines.append("Conflicts Resolved:")
            lines.append("=" * 50)
            for i, conflict in enumerate(result.conflicts, 1):
                lines.append(f"{i}. {conflict.resolution_strategy}: {conflict.rationale}")
                lines.append("")
        
        return "\n".join(lines)
