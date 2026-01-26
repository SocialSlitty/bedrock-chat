"""
Kilo integration module for iterative review and refinement.

This module provides integration with Kilo (the AI assistant) to enable
iterative code review and refinement loops.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import logging

from .orchestrator import AgentOrchestrator, OrchestrationResult, IterationResult
from .synthesizer import SynthesizedResult


@dataclass
class KiloFeedback:
    """Feedback from Kilo review."""
    
    approved: bool
    comments: List[str]
    requested_changes: List[str]
    priority_areas: List[str]
    additional_context: Dict[str, Any]


@dataclass
class KiloIntegrationConfig:
    """Configuration for Kilo integration."""
    
    # Review settings
    review_after_each_iteration: bool = True
    require_approval: bool = False
    max_review_cycles: int = 5
    
    # Feedback handling
    auto_incorporate_feedback: bool = True
    feedback_weight: float = 1.5  # Weight for Kilo-suggested priorities
    
    # Communication
    verbose_reporting: bool = True


class KiloIntegration:
    """
    Manages integration between the multi-agent orchestrator and Kilo.
    
    This class handles:
    - Submitting results to Kilo for review
    - Processing Kilo's feedback
    - Adjusting agent priorities based on feedback
    - Managing iterative refinement loops
    """
    
    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        config: Optional[KiloIntegrationConfig] = None
    ):
        """
        Initialize Kilo integration.
        
        Args:
            orchestrator: The agent orchestrator
            config: Optional integration configuration
        """
        self.orchestrator = orchestrator
        self.config = config or KiloIntegrationConfig()
        self.logger = logging.getLogger("kilo_integration")
        
        # Callback for getting Kilo feedback (to be set by user)
        self.feedback_callback: Optional[Callable[[str], KiloFeedback]] = None
    
    def set_feedback_callback(
        self,
        callback: Callable[[str], KiloFeedback]
    ) -> None:
        """
        Set the callback function for getting Kilo feedback.
        
        Args:
            callback: Function that takes a report string and returns KiloFeedback
        """
        self.feedback_callback = callback
    
    def request_kilo_review(
        self,
        iteration_result: IterationResult
    ) -> Optional[KiloFeedback]:
        """
        Request Kilo to review an iteration result.
        
        Args:
            iteration_result: The iteration result to review
            
        Returns:
            KiloFeedback if callback is set, None otherwise
        """
        if not self.feedback_callback:
            self.logger.warning("No feedback callback set, skipping Kilo review")
            return None
        
        # Generate report for Kilo
        report = self._generate_review_report(iteration_result)
        
        self.logger.info("Requesting Kilo review...")
        
        try:
            feedback = self.feedback_callback(report)
            self.logger.info(f"Received Kilo feedback: approved={feedback.approved}")
            return feedback
        except Exception as e:
            self.logger.error(f"Error getting Kilo feedback: {e}", exc_info=True)
            return None
    
    def _generate_review_report(self, iteration_result: IterationResult) -> str:
        """Generate a report for Kilo review."""
        result = iteration_result.synthesized_result
        
        lines = [
            f"Iteration {iteration_result.iteration_number} Review Request",
            "=" * 60,
            "",
            "Summary:",
            result.summary,
            "",
            "Key Findings:",
        ]
        
        # Group suggestions by priority
        critical = [s for s in result.suggestions if s.priority.value == "critical"]
        high = [s for s in result.suggestions if s.priority.value == "high"]
        medium = [s for s in result.suggestions if s.priority.value == "medium"]
        
        if critical:
            lines.append(f"\nCRITICAL ({len(critical)}):")
            for s in critical[:5]:  # Show top 5
                lines.append(f"  - {s.file_path}:{s.line_start} - {s.description}")
        
        if high:
            lines.append(f"\nHIGH ({len(high)}):")
            for s in high[:5]:
                lines.append(f"  - {s.file_path}:{s.line_start} - {s.description}")
        
        if medium:
            lines.append(f"\nMEDIUM ({len(medium)}):")
            for s in medium[:3]:
                lines.append(f"  - {s.file_path}:{s.line_start} - {s.description}")
        
        lines.extend([
            "",
            "Questions for Review:",
            "1. Are these priorities correct?",
            "2. Are there specific areas that need more attention?",
            "3. Should any suggestions be applied immediately?",
            "4. Are there any concerns about the proposed changes?",
        ])
        
        return "\n".join(lines)
    
    def incorporate_feedback(
        self,
        feedback: KiloFeedback,
        code_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Incorporate Kilo feedback into the code context.
        
        Args:
            feedback: The feedback from Kilo
            code_context: Current code context
            
        Returns:
            Updated code context with feedback incorporated
        """
        updated_context = dict(code_context)
        
        # Add feedback to metadata
        if "metadata" not in updated_context:
            updated_context["metadata"] = {}
        
        updated_context["metadata"]["kilo_feedback"] = {
            "approved": feedback.approved,
            "comments": feedback.comments,
            "requested_changes": feedback.requested_changes,
            "priority_areas": feedback.priority_areas,
        }
        
        # Adjust agent configurations based on priority areas
        if feedback.priority_areas:
            self._adjust_agent_priorities(feedback.priority_areas)
        
        return updated_context
    
    def _adjust_agent_priorities(self, priority_areas: List[str]) -> None:
        """
        Adjust agent configurations based on Kilo's priority areas.
        
        Args:
            priority_areas: List of areas Kilo wants prioritized
        """
        # Map priority areas to agent types
        area_to_agent = {
            "structure": "structure",
            "organization": "structure",
            "performance": "performance",
            "optimization": "performance",
            "readability": "readability",
            "clarity": "readability",
            "best practices": "best_practices",
            "security": "best_practices",
            "quality": "best_practices",
        }
        
        for area in priority_areas:
            area_lower = area.lower()
            for keyword, agent_type in area_to_agent.items():
                if keyword in area_lower:
                    self.logger.info(f"Prioritizing {agent_type} based on feedback")
                    # Could adjust agent configs here
                    break
    
    def run_with_kilo_loop(
        self,
        initial_code: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Run the orchestration with Kilo review loop.
        
        This implements the complete cycle:
        1. Run multi-agent refactoring
        2. Submit to Kilo for review
        3. Incorporate feedback
        4. Repeat until approved or max cycles reached
        
        Args:
            initial_code: Initial code to refactor
            metadata: Optional metadata
            
        Returns:
            Final orchestration result
        """
        self.logger.info("Starting orchestration with Kilo review loop")
        
        current_code = dict(initial_code)
        current_metadata = metadata or {}
        all_iterations: List[IterationResult] = []
        result = None
        
        for cycle in range(1, self.config.max_review_cycles + 1):
            self.logger.info(f"Starting review cycle {cycle}")
            
            # Run orchestration
            result = self.orchestrator.orchestrate(current_code, current_metadata)
            current_code = result.final_code  # keep latest code even if we break early
            
            # Add iterations to our tracking
            all_iterations.extend(result.iterations)
            
            # Get the last iteration for review
            if result.iterations:
                last_iteration = result.iterations[-1]
                
                # Request Kilo review if configured
                if self.config.review_after_each_iteration:
                    feedback = self.request_kilo_review(last_iteration)
                    
                    if feedback:
                        # Store feedback
                        last_iteration.kilo_feedback = self._format_feedback(feedback)
                        
                        # Check if approved
                        if feedback.approved:
                            self.logger.info("Kilo approved the changes")
                            if not self.config.require_approval or feedback.approved:
                                break
                        
                        # Incorporate feedback for next cycle
                        if self.config.auto_incorporate_feedback:
                            current_metadata = self.incorporate_feedback(
                                feedback,
                                {"files": current_code, "metadata": current_metadata}
                            ).get("metadata", {})
                    
                    # current_code already updated above
            
            # Check if we should continue
            if result.converged and cycle > 1:
                self.logger.info("Process converged, ending review loop")
                break
        
        # Create final result
        final_result = OrchestrationResult(
            iterations=all_iterations,
            final_code=current_code,
            total_improvements=sum(
                len(it.synthesized_result.suggestions) for it in all_iterations
            ),
            total_execution_time=sum(it.execution_time for it in all_iterations),
            converged=result.converged if result and result.iterations else False,
            summary=self._generate_final_summary(all_iterations),
        )
        
        self.logger.info("Kilo review loop complete")
        return final_result
    
    def _format_feedback(self, feedback: KiloFeedback) -> str:
        """Format feedback for storage."""
        lines = [
            f"Approved: {feedback.approved}",
            "",
            "Comments:",
        ]
        lines.extend(f"  - {comment}" for comment in feedback.comments)
        
        if feedback.requested_changes:
            lines.append("")
            lines.append("Requested Changes:")
            lines.extend(f"  - {change}" for change in feedback.requested_changes)
        
        if feedback.priority_areas:
            lines.append("")
            lines.append("Priority Areas:")
            lines.extend(f"  - {area}" for area in feedback.priority_areas)
        
        return "\n".join(lines)
    
    def _generate_final_summary(self, iterations: List[IterationResult]) -> str:
        """Generate final summary including Kilo feedback."""
        lines = [
            "Multi-Agent Orchestration with Kilo Review - Final Summary",
            "=" * 60,
            "",
            f"Total Review Cycles: {len([it for it in iterations if it.kilo_feedback])}",
            f"Total Iterations: {len(iterations)}",
            f"Total Suggestions: {sum(len(it.synthesized_result.suggestions) for it in iterations)}",
            "",
            "Iteration History:",
        ]
        
        for iteration in iterations:
            lines.append(
                f"  Iteration {iteration.iteration_number}: "
                f"{len(iteration.synthesized_result.suggestions)} suggestions"
            )
            if iteration.kilo_feedback:
                lines.append("    Kilo Review: Provided")
        
        return "\n".join(lines)


# Convenience function for easy usage
def run_multi_agent_refactoring(
    code_files: Dict[str, str],
    enable_kilo_review: bool = True,
    feedback_callback: Optional[Callable[[str], KiloFeedback]] = None,
    orchestrator_config: Optional[Dict[str, Any]] = None,
    kilo_config: Optional[Dict[str, Any]] = None
) -> OrchestrationResult:
    """
    Convenience function to run multi-agent refactoring.
    
    Args:
        code_files: Dictionary mapping file paths to code content
        enable_kilo_review: Whether to enable Kilo review loop
        feedback_callback: Optional callback for Kilo feedback
        orchestrator_config: Optional orchestrator configuration
        kilo_config: Optional Kilo integration configuration
        
    Returns:
        OrchestrationResult with final code and analysis
    
    Example:
        ```python
        code = {
            "app.py": "def foo():\\n    pass",
            "utils.py": "def bar():\\n    pass",
        }
        
        def my_feedback_callback(report: str) -> KiloFeedback:
            # Process report and return feedback
            return KiloFeedback(
                approved=True,
                comments=["Looks good"],
                requested_changes=[],
                priority_areas=[],
                additional_context={}
            )
        
        result = run_multi_agent_refactoring(
            code,
            enable_kilo_review=True,
            feedback_callback=my_feedback_callback
        )
        
        print(result.summary)
        for file_path, content in result.final_code.items():
            print(f"\\n{file_path}:\\n{content}")
        ```
    """
    from .orchestrator import AgentOrchestrator, OrchestrationConfig
    
    # Create orchestrator
    orc_config = OrchestrationConfig(**(orchestrator_config or {}))
    orchestrator = AgentOrchestrator(orc_config)
    
    if enable_kilo_review and feedback_callback:
        # Use Kilo integration
        kilo_int_config = KiloIntegrationConfig(**(kilo_config or {}))
        integration = KiloIntegration(orchestrator, kilo_int_config)
        integration.set_feedback_callback(feedback_callback)
        
        return integration.run_with_kilo_loop(code_files)
    else:
        # Run without Kilo review
        return orchestrator.orchestrate(code_files)
