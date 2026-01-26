"""
Multi-Agent Orchestration System for Automated Code Refactoring

This module provides an orchestration framework that coordinates multiple
specialized refactoring agents to collaboratively improve code quality.
"""

from .orchestrator import AgentOrchestrator, OrchestrationConfig
from .agents import (
    StructureAgent,
    PerformanceAgent,
    ReadabilityAgent,
    BestPracticesAgent,
)
from .synthesizer import ResultSynthesizer

__all__ = [
    "AgentOrchestrator",
    "OrchestrationConfig",
    "StructureAgent",
    "PerformanceAgent",
    "ReadabilityAgent",
    "BestPracticesAgent",
    "ResultSynthesizer",
]
