"""
Example with Kilo integration for iterative review and refinement.

This demonstrates the complete workflow including Kilo feedback loops.
"""

from app.agents.kilo_integration import (
    run_multi_agent_refactoring,
    KiloFeedback
)
from app.agents.config import setup_orchestration_environment, ResultExporter


def kilo_feedback_callback(report: str) -> KiloFeedback:
    """
    Simulated Kilo feedback callback.
    
    In a real implementation, this would:
    1. Send the report to Kilo
    2. Wait for Kilo's analysis and feedback
    3. Return structured feedback
    
    For this example, we'll simulate the interaction.
    """
    print("\n" + "=" * 60)
    print("KILO REVIEW REQUEST")
    print("=" * 60)
    print(report)
    print("\n" + "=" * 60)
    
    # Simulate Kilo's analysis
    # In practice, this would be an API call or interactive session
    
    # For demo purposes, we'll auto-approve after showing the report
    # In real usage, this would wait for actual Kilo feedback
    
    # Simulate different feedback based on iteration
    if "Iteration 1" in report:
        return KiloFeedback(
            approved=False,
            comments=[
                "Good initial analysis",
                "Focus more on performance issues",
                "Security concerns should be addressed first"
            ],
            requested_changes=[
                "Prioritize CRITICAL and HIGH priority items",
                "Add more detail to performance suggestions"
            ],
            priority_areas=["performance", "security"],
            additional_context={
                "focus": "performance_optimization",
                "urgency": "high"
            }
        )
    else:
        return KiloFeedback(
            approved=True,
            comments=[
                "Improvements look good",
                "Performance issues addressed",
                "Ready to proceed"
            ],
            requested_changes=[],
            priority_areas=[],
            additional_context={}
        )


def main():
    """Run Kilo integration example."""
    
    # Setup environment
    setup_orchestration_environment(log_level="INFO")
    
    # Code with various issues for agents to find
    code_files = {
        "app.py": """
import os
import sys

def calculate_metrics(data):
    # Calculate various metrics
    total = 0
    count = 0
    max_val = 0
    min_val = 999999
    
    for item in data:
        for i in range(len(item)):
            for j in range(len(item[i])):
                val = item[i][j]
                total = total + val
                count = count + 1
                if val > max_val:
                    max_val = val
                if val < min_val:
                    min_val = val
    
    avg = total / count if count > 0 else 0
    return total, count, avg, max_val, min_val

def process_user_input(user_input):
    # SECURITY ISSUE: Using eval
    result = eval(user_input)
    return result

class DataManager:
    def __init__(self):
        self.data = []
    
    def add(self, item):
        self.data.append(item)
    
    def remove(self, item):
        try:
            self.data.remove(item)
        except:
            pass
    
    def get_all(self):
        return self.data
    
    def clear(self):
        self.data = []
    
    def process(self):
        result = ""
        for item in self.data:
            result = result + str(item) + ","
        return result
""",
        "utils.py": """
def h(x, y):
    return x + y

def calculate(a, b, c, d, e, f, g):
    if a > 100:
        if b > 200:
            if c > 300:
                if d > 400:
                    return a + b + c + d + e + f + g
    return 0

def format_output(data):
    output = ""
    for i in range(len(data)):
        output = output + data[i]
    return output
"""
    }
    
    print("=" * 60)
    print("Multi-Agent Refactoring with Kilo Integration")
    print("=" * 60)
    print(f"\nAnalyzing {len(code_files)} files with Kilo review loop...")
    
    # Run with Kilo integration
    result = run_multi_agent_refactoring(
        code_files,
        enable_kilo_review=True,
        feedback_callback=kilo_feedback_callback,
        orchestrator_config={
            "max_iterations": 2,
            "parallel_execution": True,
            "auto_apply_suggestions": False,
        },
        kilo_config={
            "review_after_each_iteration": True,
            "max_review_cycles": 3,
            "auto_incorporate_feedback": True,
        }
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(result.summary)
    
    # Show Kilo feedback history
    print("\n\nKilo Feedback History:")
    print("-" * 60)
    for iteration in result.iterations:
        if iteration.kilo_feedback:
            print(f"\nIteration {iteration.iteration_number}:")
            print(iteration.kilo_feedback)
    
    # Show critical and high priority suggestions
    if result.iterations:
        last_iteration = result.iterations[-1]
        critical_high = [
            s for s in last_iteration.synthesized_result.suggestions
            if s.priority.value in ["critical", "high"]
        ]
        
        if critical_high:
            print(f"\n\nCritical & High Priority Issues ({len(critical_high)}):")
            print("-" * 60)
            for i, suggestion in enumerate(critical_high, 1):
                print(f"\n{i}. [{suggestion.priority.value.upper()}] "
                      f"{suggestion.agent_type.value}")
                print(f"   {suggestion.file_path}:{suggestion.line_start}")
                print(f"   {suggestion.description}")
                print(f"   → {suggestion.rationale}")
    
    # Export results
    print("\n\nExporting results...")
    
    ResultExporter.export_to_json(
        result,
        "output/kilo_example_results.json",
        pretty=True
    )
    print("✓ Exported to output/kilo_example_results.json")
    
    ResultExporter.export_to_markdown(
        result,
        "output/kilo_example_report.md"
    )
    print("✓ Exported to output/kilo_example_report.md")
    
    print("\n" + "=" * 60)
    print("Kilo Integration Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
