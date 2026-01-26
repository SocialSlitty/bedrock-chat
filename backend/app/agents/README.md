# Multi-Agent Code Refactoring Orchestration System

A sophisticated system for orchestrating multiple specialized AI agents to collaboratively refactor and improve code quality through parallel analysis and iterative refinement.

## Overview

This system implements an automated workflow that:

1. **Coordinates Multiple Specialized Agents** - Each agent focuses on a specific dimension of code quality:
   - **Structure Agent**: Analyzes code organization, module structure, and design patterns
   - **Performance Agent**: Identifies performance bottlenecks and optimization opportunities
   - **Readability Agent**: Improves code clarity, naming, and documentation
   - **Best Practices Agent**: Ensures adherence to coding standards and security practices

2. **Executes in Parallel** - Agents run concurrently for faster analysis

3. **Synthesizes Results** - Intelligently combines suggestions from all agents, resolving conflicts and prioritizing improvements

4. **Integrates with Kilo** - Submits results for review and incorporates feedback iteratively

5. **Iterates Until Convergence** - Continues refining until quality goals are met or convergence is detected

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Kilo Integration                       │
│              (Review & Feedback Loop)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                Agent Orchestrator                        │
│         (Coordinates & Manages Workflow)                 │
└────────┬────────────────────────────────────────────────┘
         │
         ├──────────┬──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Structure│ │Perform.│ │Readab. │ │  Best  │
    │ Agent  │ │ Agent  │ │ Agent  │ │Practice│
    └────────┘ └────────┘ └────────┘ └────────┘
         │          │          │          │
         └──────────┴──────────┴──────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Result Synthesizer   │
         │ (Conflict Resolution) │
         └───────────────────────┘
```

## Installation

The system is located in `backend/app/agents/` and requires Python 3.8+.

```bash
cd backend
poetry install
```

## Quick Start

### Basic Usage

```python
from app.agents import AgentOrchestrator, OrchestrationConfig

# Define your code files
code_files = {
    "app.py": """
def calculate(x, y):
    result = 0
    for i in range(x):
        for j in range(y):
            result = result + 1
    return result
""",
    "utils.py": """
def process_data(data):
    # Process the data
    output = []
    for item in data:
        output = output + [item * 2]
    return output
"""
}

# Create orchestrator with default config
orchestrator = AgentOrchestrator()

# Run refactoring analysis
result = orchestrator.orchestrate(code_files)

# View results
print(result.summary)
print(f"Total suggestions: {len(result.iterations[-1].synthesized_result.suggestions)}")

# Access refactored code
for file_path, content in result.final_code.items():
    print(f"\n{file_path}:\n{content}")
```

### With Custom Configuration

```python
from app.agents import AgentOrchestrator, OrchestrationConfig
from app.agents.base_agent import AgentType

# Custom configuration
config = OrchestrationConfig(
    enabled_agents=[
        AgentType.PERFORMANCE,
        AgentType.READABILITY,
    ],
    parallel_execution=True,
    max_workers=2,
    max_iterations=5,
    convergence_threshold=0.05,
    auto_apply_suggestions=True,
)

orchestrator = AgentOrchestrator(config)
result = orchestrator.orchestrate(code_files)
```

### With Kilo Integration

```python
from app.agents.kilo_integration import (
    run_multi_agent_refactoring,
    KiloFeedback
)

def my_kilo_feedback_handler(report: str) -> KiloFeedback:
    """
    This function would integrate with Kilo to get feedback.
    For now, it returns a mock response.
    """
    print("Kilo Review Request:")
    print(report)
    
    # In practice, this would call Kilo's API or interface
    user_input = input("Approve? (y/n): ")
    
    return KiloFeedback(
        approved=user_input.lower() == 'y',
        comments=["Review complete"],
        requested_changes=["Focus on performance" if user_input.lower() != 'y' else ""],
        priority_areas=["performance"],
        additional_context={}
    )

# Run with Kilo integration
result = run_multi_agent_refactoring(
    code_files,
    enable_kilo_review=True,
    feedback_callback=my_kilo_feedback_handler
)

print(result.summary)
```

### Using Configuration Files

```python
from app.agents.config import setup_orchestration_environment
from app.agents import AgentOrchestrator

# Setup from config file
config_manager = setup_orchestration_environment(
    config_path="orchestration_config.json",
    log_level="DEBUG"
)

# Create orchestrator from config
from app.agents.orchestrator import OrchestrationConfig
from app.agents.base_agent import AgentType

orc_config = OrchestrationConfig(
    enabled_agents=[AgentType[a.upper()] for a in config_manager.get_orchestration_config()["enabled_agents"]],
    parallel_execution=config_manager.get_orchestration_config()["parallel_execution"],
    max_workers=config_manager.get_orchestration_config()["max_workers"],
)

orchestrator = AgentOrchestrator(orc_config)
result = orchestrator.orchestrate(code_files)
```

Example `orchestration_config.json`:

```json
{
  "orchestration": {
    "enabled_agents": ["structure", "performance", "readability", "best_practices"],
    "parallel_execution": true,
    "max_workers": 4,
    "max_iterations": 3,
    "convergence_threshold": 0.1,
    "auto_apply_suggestions": false
  },
  "agents": {
    "structure": {
      "max_function_length": 50,
      "max_class_length": 300
    },
    "performance": {
      "max_loop_depth": 3
    },
    "readability": {
      "max_line_length": 100
    }
  },
  "kilo_integration": {
    "review_after_each_iteration": true,
    "max_review_cycles": 5
  },
  "logging": {
    "level": "INFO",
    "log_file": "orchestration.log"
  }
}
```

## Exporting Results

```python
from app.agents.config import ResultExporter

# Export to JSON
ResultExporter.export_to_json(
    result,
    "output/results.json",
    pretty=True
)

# Export to Markdown report
ResultExporter.export_to_markdown(
    result,
    "output/report.md"
)

# Export code changes
ResultExporter.export_code_changes(
    original_code=code_files,
    final_code=result.final_code,
    output_dir="output/code"
)
```

## Agent Details

### Structure Agent

Analyzes code organization and structure:
- Function and class length
- Module organization
- Import management
- Code duplication
- Design pattern adherence

**Configuration:**
```python
{
    "max_function_length": 50,
    "max_class_length": 300
}
```

### Performance Agent

Identifies performance issues:
- Nested loop complexity
- Repeated computations
- Inefficient patterns (string concatenation in loops)
- Algorithm complexity
- Caching opportunities

**Configuration:**
```python
{
    "max_loop_depth": 3
}
```

### Readability Agent

Improves code clarity:
- Naming conventions
- Magic numbers
- Documentation and docstrings
- Line length
- Code comments

**Configuration:**
```python
{
    "max_line_length": 100,
    "check_magic_numbers": true
}
```

### Best Practices Agent

Ensures quality standards:
- Error handling (bare except clauses)
- Type hints
- Security issues (eval usage)
- Code smells
- Framework-specific practices

**Configuration:**
```python
{
    "require_type_hints": true,
    "check_security": true
}
```

## Result Synthesis

The [`ResultSynthesizer`](synthesizer.py) combines suggestions from all agents:

1. **Conflict Detection**: Identifies overlapping suggestions
2. **Conflict Resolution**: Uses strategies like priority-based or merging
3. **Deduplication**: Removes duplicate suggestions
4. **Priority Ranking**: Orders suggestions by importance

## Iterative Refinement

The system supports iterative refinement:

1. Run initial analysis
2. Apply high-priority suggestions
3. Re-analyze improved code
4. Continue until convergence or max iterations

**Convergence** is detected when the improvement rate falls below the threshold.

## Integration Points

### Kilo Integration

The [`KiloIntegration`](kilo_integration.py) class provides:

- **Review Requests**: Submit results to Kilo for feedback
- **Feedback Processing**: Parse and incorporate Kilo's suggestions
- **Priority Adjustment**: Modify agent focus based on feedback
- **Iterative Loop**: Continue until Kilo approves

### Custom Agents

Create custom agents by extending [`BaseAgent`](base_agent.py):

```python
from app.agents.base_agent import BaseAgent, AgentType, RefactoringSuggestion

class CustomAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(AgentType.CUSTOM, config)
    
    def analyze(self, code_context):
        suggestions = []
        # Your analysis logic
        return suggestions
    
    def apply_refactoring(self, suggestion, code_context):
        # Your refactoring logic
        return {}
```

## API Reference

### AgentOrchestrator

Main orchestration class.

**Methods:**
- `orchestrate(initial_code, metadata)`: Run complete orchestration
- `execute_parallel(code_context)`: Execute agents in parallel
- `run_iteration(code_context, iteration_number)`: Run single iteration
- `apply_suggestions(code_context, synthesized_result)`: Apply refactorings

### KiloIntegration

Manages Kilo integration.

**Methods:**
- `set_feedback_callback(callback)`: Set feedback handler
- `request_kilo_review(iteration_result)`: Request review
- `run_with_kilo_loop(initial_code, metadata)`: Run with review loop

### ConfigManager

Manages configuration.

**Methods:**
- `load_from_file(config_path)`: Load config from JSON
- `save_to_file(config_path)`: Save config to JSON
- `get(section, key, default)`: Get config value
- `set(section, key, value)`: Set config value

## Examples

See the [`examples/`](examples/) directory for complete examples:

- `basic_usage.py`: Simple refactoring example
- `with_kilo.py`: Kilo integration example
- `custom_agent.py`: Creating custom agents
- `batch_processing.py`: Processing multiple projects

## Logging

Logging is configured via [`OrchestrationLogger`](config.py):

```python
from app.agents.config import OrchestrationLogger

OrchestrationLogger.setup_logging(
    level="DEBUG",
    log_file="orchestration.log"
)
```

Log levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical issues

## Performance Considerations

- **Parallel Execution**: Enabled by default, uses ThreadPoolExecutor
- **Timeout**: Each agent has a 5-minute timeout
- **Memory**: Agents process code in memory; large codebases may require chunking
- **Convergence**: Set appropriate thresholds to avoid excessive iterations

## Limitations

- Currently supports Python code analysis only
- Some refactorings require manual review before application
- Complex structural changes may need human oversight
- Performance analysis is heuristic-based

## Future Enhancements

- Support for additional languages (JavaScript, TypeScript, Java)
- Machine learning-based suggestion ranking
- Automated test generation for refactored code
- Integration with CI/CD pipelines
- Real-time collaboration features
- Advanced conflict resolution strategies

## Contributing

To add new agents or improve existing ones:

1. Extend [`BaseAgent`](base_agent.py)
2. Implement `analyze()` and `apply_refactoring()` methods
3. Add agent to [`agents.py`](agents.py)
4. Update [`orchestrator.py`](orchestrator.py) to include new agent type
5. Add tests and documentation

## License

This module is part of the bedrock-chat project and follows the same license.

## Support

For issues or questions:
- Check the documentation
- Review example code
- Open an issue on the project repository
