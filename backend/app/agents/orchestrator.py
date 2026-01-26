"""
Main orchestrator for coordinating multi-agent refactoring workflows.
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass, field
import time

from .base_agent import BaseAgent, AgentResult, AgentType
from .agents import (
    StructureAgent,
    PerformanceAgent,
    ReadabilityAgent,
    BestPracticesAgent,
)
from .synthesizer import ResultSynthesizer, SynthesizedResult


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestrator."""
    
    # Agent selection
    enabled_agents: List[AgentType] = field(default_factory=lambda: [
        AgentType.STRUCTURE,
        AgentType.PERFORMANCE,
        AgentType.READABILITY,
        AgentType.BEST_PRACTICES,
    ])
    
    # Execution settings
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_per_agent: float = 300.0  # 5 minutes
    
    # Iteration settings
    max_iterations: int = 3
    convergence_threshold: float = 0.1  # Stop if improvement < 10%
    
    # Agent-specific configs
    agent_configs: Dict[AgentType, Dict[str, Any]] = field(default_factory=dict)
    
    # Synthesizer config
    synthesizer_config: Dict[str, Any] = field(default_factory=dict)
    
    # Kilo integration
    kilo_review_enabled: bool = True
    auto_apply_suggestions: bool = False


@dataclass
class IterationResult:
    """Result from a single iteration of refactoring."""
    
    iteration_number: int
    synthesized_result: SynthesizedResult
    code_context: Dict[str, Any]
    improvements_applied: int
    execution_time: float
    kilo_feedback: Optional[str] = None


@dataclass
class OrchestrationResult:
    """Final result from the orchestration process."""
    
    iterations: List[IterationResult]
    final_code: Dict[str, str]
    total_improvements: int
    total_execution_time: float
    converged: bool
    summary: str


class AgentOrchestrator:
    """
    Orchestrates multiple refactoring agents to collaboratively improve code.
    
    The orchestrator:
    1. Coordinates parallel execution of specialized agents
    2. Synthesizes their results
    3. Manages iterative refinement
    4. Integrates with Kilo for review and guidance
    """
    
    def __init__(self, config: Optional[OrchestrationConfig] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Optional orchestration configuration
        """
        self.config = config or OrchestrationConfig()
        self.logger = logging.getLogger("orchestrator")
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Initialize synthesizer
        self.synthesizer = ResultSynthesizer(self.config.synthesizer_config)
        
        self.logger.info(
            f"Initialized orchestrator with {len(self.agents)} agents: "
            f"{[a.agent_type.value for a in self.agents]}"
        )
    
    def _initialize_agents(self) -> List[BaseAgent]:
        """Initialize the configured agents."""
        agents = []
        
        agent_classes = {
            AgentType.STRUCTURE: StructureAgent,
            AgentType.PERFORMANCE: PerformanceAgent,
            AgentType.READABILITY: ReadabilityAgent,
            AgentType.BEST_PRACTICES: BestPracticesAgent,
        }
        
        for agent_type in self.config.enabled_agents:
            agent_class = agent_classes.get(agent_type)
            if agent_class:
                agent_config = self.config.agent_configs.get(agent_type, {})
                agents.append(agent_class(agent_config))
            else:
                self.logger.warning(f"Unknown agent type: {agent_type}")
        
        return agents
    
    def execute_parallel(self, code_context: Dict[str, Any]) -> List[AgentResult]:
        """
        Execute agents in parallel.
        
        Args:
            code_context: Dictionary containing code files and metadata
            
        Returns:
            List of agent results
        """
        results = []
        
        if self.config.parallel_execution and len(self.agents) > 1:
            self.logger.info(f"Executing {len(self.agents)} agents in parallel")
            
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_agent = {
                    executor.submit(agent.execute, code_context): agent
                    for agent in self.agents
                }
                
                done, not_done = wait(
                    future_to_agent,
                    timeout=self.config.timeout_per_agent
                )
                
                # Handle completed futures
                for future in done:
                    agent = future_to_agent[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(
                            f"Agent {agent.agent_type.value} failed: {e}",
                            exc_info=True
                        )
                        results.append(AgentResult(
                            agent_type=agent.agent_type,
                            suggestions=[],
                            summary=f"Agent failed: {str(e)}",
                            metrics={},
                            execution_time=0.0,
                            success=False,
                            errors=[str(e)],
                        ))
                
                # Handle timeouts
                for future in not_done:
                    agent = future_to_agent[future]
                    self.logger.error(
                        f"Agent {agent.agent_type.value} timed out after "
                        f"{self.config.timeout_per_agent}s"
                    )
                    future.cancel()
                    results.append(AgentResult(
                        agent_type=agent.agent_type,
                        suggestions=[],
                        summary="Agent timed out",
                        metrics={},
                        execution_time=self.config.timeout_per_agent,
                        success=False,
                        errors=[f"Timed out after {self.config.timeout_per_agent}s"],
                    ))
        else:
            self.logger.info(f"Executing {len(self.agents)} agents sequentially")
            for agent in self.agents:
                try:
                    result = agent.execute(code_context)
                    results.append(result)
                except Exception as e:
                    self.logger.error(
                        f"Agent {agent.agent_type.value} failed: {e}",
                        exc_info=True
                    )
                    results.append(AgentResult(
                        agent_type=agent.agent_type,
                        suggestions=[],
                        summary=f"Agent failed: {str(e)}",
                        metrics={},
                        execution_time=0.0,
                        success=False,
                        errors=[str(e)],
                    ))
        
        return results
    
    def run_iteration(
        self,
        code_context: Dict[str, Any],
        iteration_number: int
    ) -> IterationResult:
        """
        Run a single iteration of multi-agent refactoring.
        
        Args:
            code_context: Current code context
            iteration_number: The iteration number
            
        Returns:
            IterationResult with synthesized suggestions
        """
        start_time = time.time()
        
        self.logger.info(f"Starting iteration {iteration_number}")
        
        # Execute agents
        agent_results = self.execute_parallel(code_context)
        
        # Synthesize results
        synthesized = self.synthesizer.synthesize(agent_results)
        
        # Log summary
        self.logger.info(f"Iteration {iteration_number} complete:")
        self.logger.info(synthesized.summary)
        
        execution_time = time.time() - start_time
        
        return IterationResult(
            iteration_number=iteration_number,
            synthesized_result=synthesized,
            code_context=code_context,
            improvements_applied=0,  # Will be updated if suggestions are applied
            execution_time=execution_time,
        )
    
    def apply_suggestions(
        self,
        code_context: Dict[str, Any],
        synthesized_result: SynthesizedResult,
        max_suggestions: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Apply refactoring suggestions to the code.
        
        Args:
            code_context: Current code context
            synthesized_result: Synthesized suggestions
            max_suggestions: Maximum number of suggestions to apply
            
        Returns:
            Updated code files
        """
        updated_files = dict(code_context.get("files", {}))
        suggestions_to_apply = synthesized_result.suggestions
        
        if max_suggestions:
            suggestions_to_apply = suggestions_to_apply[:max_suggestions]
        
        self.logger.info(f"Applying {len(suggestions_to_apply)} suggestions")
        
        # Group suggestions by file
        by_file: Dict[str, List] = {}
        for suggestion in suggestions_to_apply:
            if suggestion.file_path not in by_file:
                by_file[suggestion.file_path] = []
            by_file[suggestion.file_path].append(suggestion)
        
        # Apply suggestions file by file
        for file_path, file_suggestions in by_file.items():
            if file_path in updated_files:
                # Sort by line number (reverse order to avoid offset issues)
                file_suggestions.sort(key=lambda s: s.line_start, reverse=True)
                
                lines = updated_files[file_path].split("\n")
                
                for suggestion in file_suggestions:
                    # Simple replacement (in practice, would need more sophisticated merging)
                    if suggestion.refactored_code and not suggestion.refactored_code.startswith("#"):
                        start_idx = suggestion.line_start - 1
                        end_idx = suggestion.line_end
                        
                        if 0 <= start_idx < len(lines):
                            # Replace the lines
                            new_lines = suggestion.refactored_code.split("\n")
                            lines[start_idx:end_idx] = new_lines
                
                updated_files[file_path] = "\n".join(lines)
        
        return updated_files
    
    def check_convergence(
        self,
        current_iteration: IterationResult,
        previous_iteration: Optional[IterationResult]
    ) -> bool:
        """
        Check if the refactoring process has converged.
        
        Args:
            current_iteration: Current iteration result
            previous_iteration: Previous iteration result
            
        Returns:
            True if converged
        """
        if not previous_iteration:
            return False
        
        current_count = len(current_iteration.synthesized_result.suggestions)
        previous_count = len(previous_iteration.synthesized_result.suggestions)
        
        if previous_count == 0:
            return current_count == 0
        
        improvement_ratio = abs(current_count - previous_count) / previous_count
        
        converged = improvement_ratio < self.config.convergence_threshold
        
        if converged:
            self.logger.info(
                f"Convergence detected: improvement ratio {improvement_ratio:.2%} "
                f"< threshold {self.config.convergence_threshold:.2%}"
            )
        
        return converged
    
    def orchestrate(
        self,
        initial_code: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Orchestrate the complete multi-agent refactoring process.
        
        Args:
            initial_code: Dictionary mapping file paths to code content
            metadata: Optional metadata about the code
            
        Returns:
            OrchestrationResult with all iterations and final code
        """
        start_time = time.time()
        
        self.logger.info("Starting multi-agent orchestration")
        self.logger.info(f"Processing {len(initial_code)} files")
        
        iterations: List[IterationResult] = []
        current_code = dict(initial_code)
        total_improvements = 0
        converged = False
        
        for i in range(1, self.config.max_iterations + 1):
            # Prepare code context
            code_context = {
                "files": current_code,
                "metadata": metadata or {},
                "iteration": i,
            }
            
            # Run iteration
            iteration_result = self.run_iteration(code_context, i)
            
            # Apply suggestions if configured
            if self.config.auto_apply_suggestions:
                updated_code = self.apply_suggestions(
                    code_context,
                    iteration_result.synthesized_result
                )
                improvements = len(iteration_result.synthesized_result.suggestions)
                iteration_result.improvements_applied = improvements
                total_improvements += improvements
                current_code = updated_code
            
            iterations.append(iteration_result)
            
            # Check convergence
            previous = iterations[-2] if len(iterations) > 1 else None
            if self.check_convergence(iteration_result, previous):
                converged = True
                self.logger.info(f"Converged after {i} iterations")
                break
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = self._generate_orchestration_summary(
            iterations,
            total_improvements,
            total_time,
            converged
        )
        
        self.logger.info("Orchestration complete")
        self.logger.info(summary)
        
        return OrchestrationResult(
            iterations=iterations,
            final_code=current_code,
            total_improvements=total_improvements,
            total_execution_time=total_time,
            converged=converged,
            summary=summary,
        )
    
    def _generate_orchestration_summary(
        self,
        iterations: List[IterationResult],
        total_improvements: int,
        total_time: float,
        converged: bool
    ) -> str:
        """Generate a summary of the orchestration process."""
        lines = [
            "Multi-Agent Orchestration Summary",
            "=" * 50,
            "",
            f"Total Iterations: {len(iterations)}",
            f"Total Improvements: {total_improvements}",
            f"Total Execution Time: {total_time:.2f}s",
            f"Converged: {'Yes' if converged else 'No'}",
            "",
            "Iteration Details:",
        ]
        
        for iteration in iterations:
            result = iteration.synthesized_result
            lines.append(
                f"  Iteration {iteration.iteration_number}: "
                f"{len(result.suggestions)} suggestions, "
                f"{iteration.improvements_applied} applied, "
                f"{iteration.execution_time:.2f}s"
            )
        
        return "\n".join(lines)
    
    def generate_report(self, result: OrchestrationResult) -> str:
        """
        Generate a detailed report of the orchestration.
        
        Args:
            result: The orchestration result
            
        Returns:
            Formatted report string
        """
        lines = [result.summary, "", "Detailed Iteration Reports:", "=" * 50]
        
        for iteration in result.iterations:
            lines.append("")
            lines.append(f"Iteration {iteration.iteration_number}")
            lines.append("-" * 50)
            report = self.synthesizer.generate_report(iteration.synthesized_result)
            lines.append(report)
        
        return "\n".join(lines)
