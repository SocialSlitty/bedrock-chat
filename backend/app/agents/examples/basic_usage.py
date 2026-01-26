"""
Basic usage example for the multi-agent orchestration system.

This example demonstrates how to use the orchestrator to analyze
and refactor code with multiple specialized agents.
"""

from app.agents import AgentOrchestrator, OrchestrationConfig
from app.agents.base_agent import AgentType
from app.agents.config import setup_orchestration_environment, ResultExporter


def main():
    """Run basic orchestration example."""
    
    # Setup logging
    setup_orchestration_environment(log_level="INFO")
    
    # Define code to analyze
    code_files = {
        "example.py": """
def calculate_total(items):
    total = 0
    for item in items:
        for i in range(item):
            total = total + 1
    return total

def process(data):
    result = ""
    for d in data:
        result = result + str(d)
    return result

class DataProcessor:
    def __init__(self):
        pass
    
    def process_data(self, data):
        # Process data
        output = []
        for item in data:
            try:
                output.append(item * 2)
            except:
                pass
        return output
""",
        "utils.py": """
def helper(x, y):
    return x + y

def another_helper(a, b, c):
    if a > 10:
        if b > 20:
            if c > 30:
                return a + b + c
    return 0
"""
    }
    
    print("=" * 60)
    print("Multi-Agent Code Refactoring - Basic Example")
    print("=" * 60)
    print(f"\nAnalyzing {len(code_files)} files...")
    
    # Create orchestrator with custom config
    config = OrchestrationConfig(
        enabled_agents=[
            AgentType.STRUCTURE,
            AgentType.PERFORMANCE,
            AgentType.READABILITY,
            AgentType.BEST_PRACTICES,
        ],
        parallel_execution=True,
        max_workers=4,
        max_iterations=2,
        convergence_threshold=0.1,
        auto_apply_suggestions=False,  # Don't auto-apply for this example
    )
    
    orchestrator = AgentOrchestrator(config)
    
    # Run orchestration
    result = orchestrator.orchestrate(code_files)
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(result.summary)
    
    # Show detailed suggestions from last iteration
    if result.iterations:
        last_iteration = result.iterations[-1]
        suggestions = last_iteration.synthesized_result.suggestions
        
        print(f"\n\nTop 10 Suggestions:")
        print("-" * 60)
        
        for i, suggestion in enumerate(suggestions[:10], 1):
            print(f"\n{i}. [{suggestion.priority.value.upper()}] "
                  f"{suggestion.agent_type.value.upper()}")
            print(f"   File: {suggestion.file_path}:{suggestion.line_start}")
            print(f"   Issue: {suggestion.description}")
            print(f"   Reason: {suggestion.rationale}")
            print(f"   Impact: {suggestion.estimated_impact}")
    
    # Export results
    print("\n\nExporting results...")
    
    ResultExporter.export_to_json(
        result,
        "output/basic_example_results.json",
        pretty=True
    )
    print("✓ Exported to output/basic_example_results.json")
    
    ResultExporter.export_to_markdown(
        result,
        "output/basic_example_report.md"
    )
    print("✓ Exported to output/basic_example_report.md")
    
    # Generate detailed report
    detailed_report = orchestrator.generate_report(result)
    with open("output/basic_example_detailed.txt", "w") as f:
        f.write(detailed_report)
    print("✓ Exported to output/basic_example_detailed.txt")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
