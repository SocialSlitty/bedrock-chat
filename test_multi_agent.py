#!/usr/bin/env python3
"""
Test script for the multi-agent refactor system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents import AgentOrchestrator, OrchestrationConfig
from app.agents.base_agent import AgentType
from app.agents.kilo_integration import run_multi_agent_refactoring, KiloFeedback

# Sample code files for testing
test_code_files = {
    "sample.py": """
def calculate(x, y):
    result = 0
    for i in range(x):
        for j in range(y):
            for k in range(10):
                result = result + 1
    return result

def process_data(data):
    output = []
    for item in data:
        output = output + [item * 2]
    return output

class VeryLongClassThatDoesTooManyThings:
    def __init__(self):
        self.data = []
    
    def a(self):
        pass
    
    def b(self):
        pass
    
    def method_without_docstring(self):
        x = 42
        y = 3.14159
        try:
            result = eval("2 + 2")
        except:
            pass
        return result
""",
    "utils.py": """
def f(x):
    return x * 2

def another_function_with_a_very_long_line_that_exceeds_the_recommended_line_length_limit():
    pass
"""
}

def test_basic_orchestration():
    """Test basic orchestration without Kilo integration."""
    print("=" * 60)
    print("Testing Basic Multi-Agent Orchestration")
    print("=" * 60)
    
    # Create orchestrator with default config
    orchestrator = AgentOrchestrator()
    
    # Run orchestration
    result = orchestrator.orchestrate(test_code_files)
    
    print(f"\nOrchestration completed:")
    print(f"- Iterations: {len(result.iterations)}")
    print(f"- Total suggestions: {sum(len(it.synthesized_result.suggestions) for it in result.iterations)}")
    print(f"- Execution time: {result.total_execution_time:.2f}s")
    print(f"- Converged: {result.converged}")
    
    print(f"\nSummary:")
    print(result.summary)
    
    # Show some suggestions
    if result.iterations:
        last_iteration = result.iterations[-1]
        suggestions = last_iteration.synthesized_result.suggestions
        
        print(f"\nTop 5 suggestions:")
        for i, suggestion in enumerate(suggestions[:5]):
            print(f"{i+1}. {suggestion.agent_type.value}: {suggestion.description}")
            print(f"   Priority: {suggestion.priority.value}")
            print(f"   File: {suggestion.file_path}:{suggestion.line_start}")
    
    return result

def test_custom_configuration():
    """Test orchestration with custom configuration."""
    print("\n" + "=" * 60)
    print("Testing Custom Configuration")
    print("=" * 60)
    
    # Custom config - only performance and readability agents
    config = OrchestrationConfig(
        enabled_agents=[
            AgentType.PERFORMANCE,
            AgentType.READABILITY,
        ],
        parallel_execution=True,
        max_workers=2,
        max_iterations=2,
        convergence_threshold=0.05,
        auto_apply_suggestions=False,
    )
    
    orchestrator = AgentOrchestrator(config)
    result = orchestrator.orchestrate(test_code_files)
    
    print(f"\nCustom orchestration completed:")
    print(f"- Enabled agents: {[a.value for a in config.enabled_agents]}")
    print(f"- Iterations: {len(result.iterations)}")
    print(f"- Total suggestions: {sum(len(it.synthesized_result.suggestions) for it in result.iterations)}")
    
    return result

def mock_kilo_feedback(report: str) -> KiloFeedback:
    """Mock Kilo feedback for testing."""
    print("\n" + "-" * 40)
    print("KILO REVIEW REQUEST:")
    print("-" * 40)
    print(report)
    print("-" * 40)
    
    # Simulate Kilo feedback
    return KiloFeedback(
        approved=True,
        comments=["The analysis looks comprehensive", "Good prioritization of issues"],
        requested_changes=["Focus more on performance optimizations"],
        priority_areas=["performance", "security"],
        additional_context={"review_cycle": 1}
    )

def test_kilo_integration():
    """Test Kilo integration."""
    print("\n" + "=" * 60)
    print("Testing Kilo Integration")
    print("=" * 60)
    
    result = run_multi_agent_refactoring(
        test_code_files,
        enable_kilo_review=True,
        feedback_callback=mock_kilo_feedback,
        orchestrator_config={
            "max_iterations": 2,
            "parallel_execution": True,
        },
        kilo_config={
            "review_after_each_iteration": True,
            "max_review_cycles": 2,
        }
    )
    
    print(f"\nKilo integration completed:")
    print(f"- Iterations: {len(result.iterations)}")
    print(f"- Total suggestions: {sum(len(it.synthesized_result.suggestions) for it in result.iterations)}")
    
    # Check for Kilo feedback
    kilo_reviews = [it for it in result.iterations if it.kilo_feedback]
    print(f"- Kilo reviews: {len(kilo_reviews)}")
    
    return result

def test_agent_specific_analysis():
    """Test individual agent analysis."""
    print("\n" + "=" * 60)
    print("Testing Individual Agent Analysis")
    print("=" * 60)
    
    from app.agents.agents import StructureAgent, PerformanceAgent, ReadabilityAgent, BestPracticesAgent
    
    agents = [
        StructureAgent(),
        PerformanceAgent(),
        ReadabilityAgent(),
        BestPracticesAgent(),
    ]
    
    code_context = {"files": test_code_files}
    
    for agent in agents:
        print(f"\n{agent.agent_type.value.upper()} AGENT:")
        print("-" * 30)
        
        result = agent.execute(code_context)
        print(f"Success: {result.success}")
        print(f"Suggestions: {len(result.suggestions)}")
        print(f"Execution time: {result.execution_time:.3f}s")
        
        if result.suggestions:
            print("Top suggestions:")
            for i, suggestion in enumerate(result.suggestions[:3]):
                print(f"  {i+1}. {suggestion.description} (Priority: {suggestion.priority.value})")

def main():
    """Run all tests."""
    print("Multi-Agent Refactor System Test Suite")
    print("=" * 60)
    
    try:
        # Test basic orchestration
        basic_result = test_basic_orchestration()
        
        # Test custom configuration
        custom_result = test_custom_configuration()
        
        # Test individual agents
        test_agent_specific_analysis()
        
        # Test Kilo integration
        kilo_result = test_kilo_integration()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)