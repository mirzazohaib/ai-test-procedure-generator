"""
Core domain models for the test procedure generator.
Uses dataclasses for type safety and immutability.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TestType(Enum):
    """Supported test procedure types"""
    FAT = "Factory Acceptance Test"
    SAT = "Site Acceptance Test"
    IQ = "Installation Qualification"
    OQ = "Operational Qualification"


class SignalType(Enum):
    """Common signal types in environmental monitoring"""
    TEMPERATURE = "Temperature"
    HUMIDITY = "Humidity"
    PRESSURE = "Pressure"
    FLOW = "Flow"
    LEVEL = "Level"
    PH = "pH"
    CONDUCTIVITY = "Conductivity"
    DISSOLVED_OXYGEN = "Dissolved Oxygen"


@dataclass(frozen=True)
class Signal:
    """Represents a measurement signal in the system"""
    id: str
    type: SignalType
    range: str
    unit: Optional[str] = None
    accuracy: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            raise ValueError("Signal ID cannot be empty")


@dataclass(frozen=True)
class Requirement:
    """System requirement that must be tested"""
    id: str
    text: str
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    category: Optional[str] = None
    
    def __post_init__(self):
        if self.priority not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            raise ValueError(f"Invalid priority: {self.priority}")


@dataclass
class Project:
    """Complete project configuration for test generation"""
    project_id: str
    system: str
    signals: List[Signal]
    requirements: List[Requirement]
    environment: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def signal_count(self) -> int:
        return len(self.signals)
    
    @property
    def requirement_count(self) -> int:
        return len(self.requirements)
    
    def get_signals_by_type(self, signal_type: SignalType) -> List[Signal]:
        return [s for s in self.signals if s.type == signal_type]


@dataclass
class TestProcedure:
    """Generated test procedure document"""
    project_id: str
    test_type: TestType
    content: str
    created_at: datetime
    template_version: str
    prompt_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "test_type": self.test_type.name,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "template_version": self.template_version,
            "prompt_version": self.prompt_version,
            "metadata": self.metadata
        }


@dataclass
class ValidationResult:
    """Result of validation checks"""
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    coverage_pct: float = 0.0
    tested_signals: List[str] = field(default_factory=list)
    missing_signals: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return f"""
Validation Report
{status}
Coverage: {self.coverage_pct:.1f}%
Errors: {len(self.errors)}
Warnings: {len(self.warnings)}
"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "coverage_pct": self.coverage_pct,
            "tested_signals": self.tested_signals,
            "missing_signals": self.missing_signals
        }


@dataclass
class GenerationMetrics:
    """Performance and cost metrics for generation"""
    generation_time_sec: float
    token_count: Dict[str, int]  # {"input": n, "output": m}
    cost_usd: float
    validation: ValidationResult
    model: str
    prompt_version: str
    template_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation_time_sec": round(self.generation_time_sec, 3),
            "token_count": self.token_count,
            "cost_usd": round(self.cost_usd, 6),
            "validation": self.validation.to_dict(),
            "model": self.model,
            "prompt_version": self.prompt_version,
            "template_version": self.template_version
        }
