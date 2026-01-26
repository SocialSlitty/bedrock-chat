"""
Configuration and logging setup for the multi-agent orchestration system.
"""

import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import copy


class OrchestrationLogger:
    """
    Centralized logging configuration for the orchestration system.
    """
    
    @staticmethod
    def setup_logging(
        level: str = "INFO",
        log_file: Optional[str] = None,
        format_string: Optional[str] = None
    ) -> None:
        """
        Setup logging for the orchestration system.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path to write logs to
            format_string: Optional custom format string
        """
        if format_string is None:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format=format_string,
            handlers=[]
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(logging.Formatter(format_string))
        logging.getLogger().addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(logging.Formatter(format_string))
            logging.getLogger().addHandler(file_handler)
        
        # Set specific logger levels
        logging.getLogger("orchestrator").setLevel(getattr(logging, level.upper()))
        logging.getLogger("agent").setLevel(getattr(logging, level.upper()))
        logging.getLogger("kilo_integration").setLevel(getattr(logging, level.upper()))


class ConfigManager:
    """
    Manages configuration for the orchestration system.
    """
    
    DEFAULT_CONFIG = {
        "orchestration": {
            "enabled_agents": ["structure", "performance", "readability", "best_practices"],
            "parallel_execution": True,
            "max_workers": 4,
            "timeout_per_agent": 300.0,
            "max_iterations": 3,
            "convergence_threshold": 0.1,
            "auto_apply_suggestions": False,
        },
        "agents": {
            "structure": {
                "max_function_length": 50,
                "max_class_length": 300,
            },
            "performance": {
                "max_loop_depth": 3,
            },
            "readability": {
                "max_line_length": 100,
                "check_magic_numbers": True,
            },
            "best_practices": {
                "require_type_hints": True,
                "check_security": True,
            },
        },
        "synthesizer": {
            "conflict_strategy": "priority",
        },
        "kilo_integration": {
            "review_after_each_iteration": True,
            "require_approval": False,
            "max_review_cycles": 5,
            "auto_incorporate_feedback": True,
            "feedback_weight": 1.5,
            "verbose_reporting": True,
        },
        "logging": {
            "level": "INFO",
            "log_file": None,
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config manager.
        
        Args:
            config_path: Optional path to a JSON config file
        """
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        
        if config_path:
            self.load_from_file(config_path)
    
    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the config file
        """
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                user_config = json.load(f)
                self._merge_config(user_config)
        else:
            logging.warning(f"Config file not found: {config_path}")
    
    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """Merge user config with default config."""
        for key, value in user_config.items():
            if key in self.config and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save current configuration to a JSON file.
        
        Args:
            config_path: Path to save the config file
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            key: Optional key within the section
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        if section not in self.config:
            return default
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            key: Key within the section
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def get_orchestration_config(self) -> Dict[str, Any]:
        """Get orchestration configuration."""
        return self.config.get("orchestration", {})
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.config.get("agents", {}).get(agent_type, {})
    
    def get_synthesizer_config(self) -> Dict[str, Any]:
        """Get synthesizer configuration."""
        return self.config.get("synthesizer", {})
    
    def get_kilo_config(self) -> Dict[str, Any]:
        """Get Kilo integration configuration."""
        return self.config.get("kilo_integration", {})


class ResultExporter:
    """
    Exports orchestration results in various formats.
    """
    
    @staticmethod
    def export_to_json(
        result: Any,
        output_path: str,
        pretty: bool = True
    ) -> None:
        """
        Export result to JSON file.
        
        Args:
            result: The result to export
            output_path: Path to save the JSON file
            pretty: Whether to pretty-print the JSON
        """
        from .orchestrator import OrchestrationResult
        
        if isinstance(result, OrchestrationResult):
            data = {
                "timestamp": datetime.now().isoformat(),
                "total_iterations": len(result.iterations),
                "total_improvements": result.total_improvements,
                "total_execution_time": result.total_execution_time,
                "converged": result.converged,
                "summary": result.summary,
                "iterations": [
                    {
                        "iteration_number": it.iteration_number,
                        "suggestions_count": len(it.synthesized_result.suggestions),
                        "improvements_applied": it.improvements_applied,
                        "execution_time": it.execution_time,
                        "kilo_feedback": it.kilo_feedback,
                    }
                    for it in result.iterations
                ],
            }
        else:
            data = {"result": str(result)}
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
    
    @staticmethod
    def export_to_markdown(
        result: Any,
        output_path: str
    ) -> None:
        """
        Export result to Markdown file.
        
        Args:
            result: The result to export
            output_path: Path to save the Markdown file
        """
        from .orchestrator import OrchestrationResult
        
        lines = [
            "# Multi-Agent Orchestration Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        if isinstance(result, OrchestrationResult):
            lines.extend([
                "## Summary",
                "",
                result.summary,
                "",
                "## Iterations",
                "",
            ])
            
            for iteration in result.iterations:
                lines.extend([
                    f"### Iteration {iteration.iteration_number}",
                    "",
                    f"- **Suggestions:** {len(iteration.synthesized_result.suggestions)}",
                    f"- **Applied:** {iteration.improvements_applied}",
                    f"- **Execution Time:** {iteration.execution_time:.2f}s",
                    "",
                ])
                
                if iteration.kilo_feedback:
                    lines.extend([
                        "**Kilo Feedback:**",
                        "",
                        "```",
                        iteration.kilo_feedback,
                        "```",
                        "",
                    ])
                
                # Add top suggestions
                suggestions = iteration.synthesized_result.suggestions[:5]
                if suggestions:
                    lines.extend([
                        "**Top Suggestions:**",
                        "",
                    ])
                    for i, suggestion in enumerate(suggestions, 1):
                        lines.extend([
                            f"{i}. **[{suggestion.priority.value.upper()}]** "
                            f"`{suggestion.file_path}:{suggestion.line_start}`",
                            f"   - {suggestion.description}",
                            f"   - *{suggestion.rationale}*",
                            "",
                        ])
        else:
            lines.append(str(result))
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            f.write("\n".join(lines))
    
    @staticmethod
    def export_code_changes(
        original_code: Dict[str, str],
        final_code: Dict[str, str],
        output_dir: str
    ) -> None:
        """
        Export code changes to files.
        
        Args:
            original_code: Original code files
            final_code: Final refactored code files
            output_dir: Directory to save the files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save original code
        original_dir = output_path / "original"
        original_dir.mkdir(exist_ok=True)
        for file_path, content in original_code.items():
            file_output = original_dir / file_path
            file_output.parent.mkdir(parents=True, exist_ok=True)
            with open(file_output, 'w') as f:
                f.write(content)
        
        # Save final code
        final_dir = output_path / "refactored"
        final_dir.mkdir(exist_ok=True)
        for file_path, content in final_code.items():
            file_output = final_dir / file_path
            file_output.parent.mkdir(parents=True, exist_ok=True)
            with open(file_output, 'w') as f:
                f.write(content)
        
        # Generate diff
        import difflib
        diff_file = output_path / "changes.diff"
        with open(diff_file, 'w') as f:
            for file_path in set(original_code.keys()) | set(final_code.keys()):
                original = original_code.get(file_path, "").splitlines()
                final = final_code.get(file_path, "").splitlines()
                
                diff = difflib.unified_diff(
                    original,
                    final,
                    fromfile=f"original/{file_path}",
                    tofile=f"refactored/{file_path}",
                    lineterm=""
                )
                
                f.write("\n".join(diff))
                f.write("\n\n")


# Convenience function to setup everything
def setup_orchestration_environment(
    config_path: Optional[str] = None,
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> ConfigManager:
    """
    Setup the complete orchestration environment.
    
    Args:
        config_path: Optional path to config file
        log_level: Logging level
        log_file: Optional log file path
        
    Returns:
        Configured ConfigManager instance
    """
    # Load configuration
    config_manager = ConfigManager(config_path)
    
    # Setup logging
    log_config = config_manager.get("logging")
    if log_config is None:
        log_config = {}
    OrchestrationLogger.setup_logging(
        level=log_config.get("level", log_level),
        log_file=log_config.get("log_file", log_file)
    )
    
    return config_manager
