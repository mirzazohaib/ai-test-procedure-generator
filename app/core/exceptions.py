"""
Custom exception hierarchy for better error handling and reporting.
"""


class GeneratorError(Exception):
    """Base exception for all generator errors"""
    pass


class ValidationError(GeneratorError):
    """Raised when validation fails"""
    def __init__(self, errors: list[str], warnings: list[str] = None):
        self.errors = errors
        self.warnings = warnings or []
        message = f"Validation failed with {len(errors)} error(s)"
        super().__init__(message)


class ProjectLoadError(GeneratorError):
    """Raised when project file cannot be loaded"""
    pass


class AIGenerationError(GeneratorError):
    """Raised when AI generation fails"""
    pass


class TemplateError(GeneratorError):
    """Raised when template processing fails"""
    pass


class RenderError(GeneratorError):
    """Raised when document rendering fails"""
    pass


class ApprovalWorkflowError(GeneratorError):
    """Raised when approval workflow operations fail"""
    pass


class ConfigurationError(GeneratorError):
    """Raised when configuration is invalid"""
    pass


class RetryExhaustedError(AIGenerationError):
    """Raised when all retry attempts are exhausted"""
    def __init__(self, attempts: int, last_error: Exception):
        self.attempts = attempts
        self.last_error = last_error
        message = f"Failed after {attempts} attempts. Last error: {last_error}"
        super().__init__(message)
