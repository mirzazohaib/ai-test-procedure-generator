"""
Enhanced validation system with comprehensive checks and structured reporting.
"""

import re
from typing import List, Set
from app.core.models import Project, ValidationResult, Signal
from app.core.exceptions import ValidationError


class ProjectValidator:
    """Validates project configuration before generation"""
    
    def validate(self, project: Project) -> ValidationResult:
        """Run all validation checks on project"""
        errors = []
        warnings = []
        
        # Required fields
        if not project.project_id:
            errors.append("Project ID is required")
        
        if not project.system:
            errors.append("System name is required")
        
        if not project.signals:
            errors.append("No signals defined - cannot generate tests")
        
        if not project.requirements:
            warnings.append("No requirements defined - tests may lack traceability")
        
        # Signal validation
        signal_ids = set()
        for signal in project.signals:
            if signal.id in signal_ids:
                errors.append(f"Duplicate signal ID: {signal.id}")
            signal_ids.add(signal.id)
            
            if not signal.range:
                warnings.append(f"Signal {signal.id} has no range specified")
        
        # Requirement validation
        req_ids = set()
        for req in project.requirements:
            if req.id in req_ids:
                errors.append(f"Duplicate requirement ID: {req.id}")
            req_ids.add(req.id)
        
        result = ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            coverage_pct=100.0 if not errors else 0.0
        )
        
        if not result.passed:
            raise ValidationError(errors, warnings)
        
        return result


class GeneratedTestValidator:
    """Validates generated test procedure content"""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
    
    def validate(self, content: str, project: Project) -> ValidationResult:
        """Validate generated test procedure"""
        errors = []
        warnings = []
        tested_signals: Set[str] = set()
        
        # Check all signals are covered
        for signal in project.signals:
            if self._signal_in_content(signal.id, content):
                tested_signals.add(signal.id)
            else:
                errors.append(f"Missing test for signal {signal.id}")
        
        # Check for placeholder text (indicates incomplete generation)
        placeholders = ["TBD", "TODO", "[INSERT", "XXX", "PLACEHOLDER"]
        for placeholder in placeholders:
            if placeholder.lower() in content.lower():
                warnings.append(f"Document contains placeholder text: {placeholder}")
        
        # Check for dangerous patterns
        skip_patterns = [
            r"skip\s+(?:this\s+)?test",
            r"test\s+(?:not\s+)?applicable",
            r"n/?a",
        ]
        for pattern in skip_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append(f"Document contains skip pattern: {pattern}")
        
        # Check structure
        if not self._has_numbered_steps(content):
            warnings.append("Document appears to lack numbered test steps")
        
        if not self._has_expected_results(content):
            warnings.append("Document may be missing expected results section")
        
        # Calculate coverage
        coverage = (len(tested_signals) / len(project.signals) * 100) if project.signals else 0.0
        
        # Strict mode: warnings become errors if coverage < 100%
        if self.strict_mode and coverage < 100.0:
            errors.extend([f"STRICT: {w}" for w in warnings])
            warnings = []
        
        missing_signals = [s.id for s in project.signals if s.id not in tested_signals]
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            coverage_pct=round(coverage, 1),
            tested_signals=list(tested_signals),
            missing_signals=missing_signals
        )
    
    def _signal_in_content(self, signal_id: str, content: str) -> bool:
        """Check if signal ID appears in content (case-insensitive)"""
        # Look for signal ID as whole word (not part of other IDs)
        pattern = r'\b' + re.escape(signal_id) + r'\b'
        return bool(re.search(pattern, content, re.IGNORECASE))
    
    def _has_numbered_steps(self, content: str) -> bool:
        """Check if content has numbered steps"""
        patterns = [
            r'^\s*\d+\.',           # 1. Step
            r'^\s*\d+\)',           # 1) Step
            r'^\s*Step\s+\d+:',     # Step 1:
        ]
        for pattern in patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False
    
    def _has_expected_results(self, content: str) -> bool:
        """Check if content includes expected results"""
        keywords = [
            "expected", "result", "acceptance", "criteria",
            "pass", "fail", "verify", "confirm"
        ]
        content_lower = content.lower()
        return any(kw in content_lower for kw in keywords)


class ComplianceValidator:
    """Validates against industry standards and compliance requirements"""
    
    REQUIRED_SECTIONS = [
        "procedure",
        "expected",
        "equipment",
    ]
    
    def validate(self, content: str, test_type: str) -> ValidationResult:
        """Validate compliance with industry standards"""
        errors = []
        warnings = []
        
        content_lower = content.lower()
        
        # Check for required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in content_lower:
                warnings.append(f"Missing recommended section: {section}")
        
        # FDA 21 CFR Part 11 considerations (for pharma/medical devices)
        if "electronic signature" not in content_lower:
            warnings.append("Consider adding electronic signature requirements for FDA compliance")
        
        # Check for safety warnings if applicable
        if "temperature" in content_lower or "pressure" in content_lower:
            if "safety" not in content_lower and "caution" not in content_lower:
                warnings.append("Consider adding safety precautions for physical measurements")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            coverage_pct=100.0
        )


def validate_all(content: str, project: Project, test_type: str) -> ValidationResult:
    """Run all validators and combine results"""
    
    # Project validation
    project_val = ProjectValidator().validate(project)
    
    # Generated content validation
    content_val = GeneratedTestValidator(strict_mode=False).validate(content, project)
    
    # Compliance validation
    compliance_val = ComplianceValidator().validate(content, test_type)
    
    # Combine results
    all_errors = project_val.errors + content_val.errors + compliance_val.errors
    all_warnings = project_val.warnings + content_val.warnings + compliance_val.warnings
    
    return ValidationResult(
        passed=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        coverage_pct=content_val.coverage_pct,
        tested_signals=content_val.tested_signals,
        missing_signals=content_val.missing_signals
    )
