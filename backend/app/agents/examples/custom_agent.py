"""
Example demonstrating how to create and use custom agents.

This shows how to extend the system with your own specialized agents.
"""

from typing import Dict, List, Any
import ast
from app.agents.base_agent import (
    BaseAgent,
    AgentType,
    RefactoringSuggestion,
    RefactoringPriority,
)
from app.agents import AgentOrchestrator, OrchestrationConfig
from app.agents.config import setup_orchestration_environment


class DocumentationAgent(BaseAgent):
    """
    Custom agent that focuses on documentation quality.
    
    Checks for:
    - Missing module docstrings
    - Incomplete function documentation
    - Missing parameter descriptions
    - Missing return value descriptions
    - TODO/FIXME comments
    """
    
    def __init__(self, config: Dict[str, Any] | None = None):
        # Use a custom agent type
        super().__init__(AgentType.READABILITY, config)  # Reuse existing type
        self.require_examples = self.config.get("require_examples", False)
    
    def analyze(self, code_context: Dict[str, Any]) -> List[RefactoringSuggestion]:
        """Analyze documentation quality."""
        suggestions = []
        
        for file_path, code_content in code_context.get("files", {}).items():
            if not file_path.endswith(".py"):
                continue
            
            try:
                tree = ast.parse(code_content)
                suggestions.extend(self._check_module_docstring(file_path, tree, code_content))
                suggestions.extend(self._check_function_docs(file_path, tree, code_content))
                suggestions.extend(self._check_todos(file_path, code_content))
            except SyntaxError:
                self.logger.warning(f"Could not parse {file_path}")
        
        return suggestions
    
    def _check_module_docstring(
        self,
        file_path: str,
        tree: ast.AST,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for module-level docstring."""
        suggestions = []
        
        # ast.get_docstring expects Module, not AST
        module_docstring = ast.get_docstring(tree) if isinstance(tree, ast.Module) else None
        if not module_docstring:
            suggestions.append(RefactoringSuggestion(
                file_path=file_path,
                line_start=1,
                line_end=1,
                original_code="",
                refactored_code='"""\nModule description here.\n"""',
                description="Missing module docstring",
                priority=RefactoringPriority.MEDIUM,
                agent_type=self.agent_type,
                rationale="Module docstrings help users understand the purpose of the file",
                estimated_impact="Better code documentation",
                tags=["documentation", "module-docstring"],
            ))
        
        return suggestions
    
    def _check_function_docs(
        self,
        file_path: str,
        tree: ast.AST,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check function documentation quality."""
        suggestions = []
        lines = code_content.split("\n")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                
                if not docstring:
                    continue  # Already handled by readability agent
                
                # Check for parameter documentation
                params = [arg.arg for arg in node.args.args if arg.arg not in ['self', 'cls']]
                
                if params:
                    # Check if parameters are documented
                    params_documented = all(
                        param in docstring for param in params
                    )
                    
                    if not params_documented:
                        suggestions.append(RefactoringSuggestion(
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.lineno + 5,
                            original_code="\n".join(lines[node.lineno-1:node.lineno+5]),
                            refactored_code="# Add parameter documentation",
                            description=f"Incomplete parameter docs in {node.name}",
                            priority=RefactoringPriority.LOW,
                            agent_type=self.agent_type,
                            rationale="All parameters should be documented",
                            estimated_impact="Clearer API documentation",
                            tags=["documentation", "parameters"],
                        ))
                
                # Check for return documentation
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                if has_return and "return" not in docstring.lower():
                    suggestions.append(RefactoringSuggestion(
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.lineno + 5,
                        original_code="\n".join(lines[node.lineno-1:node.lineno+5]),
                        refactored_code="# Add return value documentation",
                        description=f"Missing return documentation in {node.name}",
                        priority=RefactoringPriority.LOW,
                        agent_type=self.agent_type,
                        rationale="Return values should be documented",
                        estimated_impact="Better API understanding",
                        tags=["documentation", "return-value"],
                    ))
        
        return suggestions
    
    def _check_todos(
        self,
        file_path: str,
        code_content: str
    ) -> List[RefactoringSuggestion]:
        """Check for TODO/FIXME comments."""
        suggestions = []
        lines = code_content.split("\n")
        
        for i, line in enumerate(lines):
            if "TODO" in line or "FIXME" in line:
                suggestions.append(RefactoringSuggestion(
                    file_path=file_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    original_code=line,
                    refactored_code="",
                    description="Unresolved TODO/FIXME comment",
                    priority=RefactoringPriority.INFO,
                    agent_type=self.agent_type,
                    rationale="TODO/FIXME comments indicate incomplete work",
                    estimated_impact="Code completeness",
                    tags=["documentation", "todo"],
                ))
        
        return suggestions
    
    def apply_refactoring(
        self,
        suggestion: RefactoringSuggestion,
        code_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Apply documentation refactoring."""
        # Documentation changes typically require manual review
        return {}


def main():
    """Run custom agent example."""
    
    setup_orchestration_environment(log_level="INFO")
    
    # Code with documentation issues
    code_files = {
        "example.py": """
import os

def calculate(x, y, z):
    result = x + y + z
    return result

def process_data(data, options):
    '''Process the data.'''
    # TODO: Add validation
    output = []
    for item in data:
        output.append(item * 2)
    return output

class Calculator:
    def add(self, a, b):
        '''Add two numbers.'''
        return a + b
    
    def multiply(self, a, b):
        # FIXME: Handle overflow
        return a * b
"""
    }
    
    print("=" * 60)
    print("Custom Agent Example - Documentation Agent")
    print("=" * 60)
    
    # Create custom agent
    doc_agent = DocumentationAgent(config={
        "require_examples": True
    })
    
    # Create orchestrator with custom agent
    # Note: We're adding it to the standard agents
    orchestrator = AgentOrchestrator(OrchestrationConfig(
        parallel_execution=False,  # Run sequentially for clarity
        max_iterations=1,
    ))
    
    # Add our custom agent
    orchestrator.agents.append(doc_agent)
    
    print(f"\nRunning with {len(orchestrator.agents)} agents:")
    for agent in orchestrator.agents:
        print(f"  - {agent.agent_type.value}")
    
    # Run analysis
    result = orchestrator.orchestrate(code_files)
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(result.summary)
    
    # Show documentation-specific suggestions
    if result.iterations:
        last_iteration = result.iterations[-1]
        doc_suggestions = [
            s for s in last_iteration.synthesized_result.suggestions
            if "documentation" in s.tags
        ]
        
        if doc_suggestions:
            print(f"\n\nDocumentation Issues Found ({len(doc_suggestions)}):")
            print("-" * 60)
            for i, suggestion in enumerate(doc_suggestions, 1):
                print(f"\n{i}. {suggestion.file_path}:{suggestion.line_start}")
                print(f"   {suggestion.description}")
                print(f"   Tags: {', '.join(suggestion.tags)}")
    
    print("\n" + "=" * 60)
    print("Custom Agent Example Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("- Custom agents extend BaseAgent")
    print("- Implement analyze() and apply_refactoring() methods")
    print("- Can be added to the orchestrator's agent list")
    print("- Suggestions are synthesized with other agents")


if __name__ == "__main__":
    main()
