"""
Versioned prompt templates for test generation.
Each version is tracked and can be A/B tested.
"""

from typing import Dict
from app.core.models import Project, TestType
from app.utils.logging import get_logger

logger = get_logger(__name__)


# Prompt version registry
PROMPTS: Dict[str, Dict[str, str]] = {
    "v1.0": {
        "description": "Initial basic prompt",
        "template": """
Generate a {test_type} test procedure for the following project.

Project: {project_summary}

Include:
- Test steps for each signal
- Expected results
- Use numbered format
"""
    },
    
    "v1.1": {
        "description": "Enhanced with validation rules and structure",
        "template": """
You are a test engineer generating a {test_type} procedure document.

PROJECT DETAILS:
- ID: {project_id}
- System: {system_name}
- Environment: {environment}
- Signals: {signal_count}

SIGNALS TO TEST:
{signals_list}

REQUIREMENTS:
{requirements_list}

CRITICAL RULES:
1. Every signal ID MUST appear in a test
2. Use clear, numbered test steps
3. Include expected results for each test
4. Use active voice (e.g., "Verify..." not "Should verify...")
5. Specify acceptance criteria
6. Be concise but complete

OUTPUT FORMAT:
## Test [N]: [Signal ID] - [Signal Type]

**Purpose**: [Brief description]

**Equipment**: [Required equipment]

**Procedure**:
1. [Step 1]
2. [Step 2]
...

**Expected Result**: [Clear pass/fail criteria]

**Acceptance Criteria**: [Measurable criteria]

---

Generate the complete test procedure now.
"""
    },
    
    "v1.2": {
        "description": "Added safety considerations and compliance hints",
        # NOTE: Double curly braces {{ }} are used here for placeholders 
        # that the AI should see, so Python doesn't try to fill them.
        "template": """
You are a senior test engineer creating a {test_type} procedure for industrial equipment.

PROJECT CONTEXT:
═══════════════════════════════════════════════
Project ID: {project_id}
System: {system_name}
Environment: {environment}
Test Scope: {signal_count} signals, {requirement_count} requirements
═══════════════════════════════════════════════

SIGNALS UNDER TEST:
{signals_detailed}

SYSTEM REQUIREMENTS:
{requirements_detailed}

GENERATION RULES (MANDATORY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Coverage: All signal IDs must be tested (no exceptions)
✓ Structure: Use numbered steps (1. 2. 3...) 
✓ Clarity: Active voice, imperative mood
✓ Precision: Include units, ranges, tolerances
✓ Safety: Note any hazards or precautions
✓ Traceability: Link tests to requirements when applicable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST TEMPLATE (Use this structure):
═══════════════════════════════════════════════

### Test {{test_number}}: {{signal_id}}

**Signal Details**:
- Type: {{signal_type}}
- Range: {{range}}
- Requirement: {{linked_req_id}}

**Test Objective**: 
[One sentence describing what this test verifies]

**Prerequisites**:
- [ ] Equipment calibrated
- [ ] System powered on
- [ ] Safety checks complete

**Procedure**:
1. [Detailed step with expected values]
2. [Detailed step with expected values]
3. [Continue...]

**Expected Results**:
- [Specific measurable outcome 1]
- [Specific measurable outcome 2]

**Acceptance Criteria**:
✓ [Pass condition with tolerance]
✗ [Fail condition]

**Safety Notes**: [Any relevant warnings]

═══════════════════════════════════════════════

Now generate the complete {test_type} procedure following this template exactly.
Ensure EVERY signal listed above has its own test section.
"""
    }
}


def get_prompt(
    test_type: TestType,
    project: Project,
    version: str = "v1.1"
) -> str:
    """
    Get formatted prompt for test generation
    
    Args:
        test_type: Type of test (FAT, SAT, etc.)
        project: Project configuration
        version: Prompt version to use
    
    Returns:
        Formatted prompt string
    """
    if version not in PROMPTS:
        logger.warning(f"Unknown prompt version {version}, falling back to v1.1")
        version = "v1.1"
    
    template = PROMPTS[version]["template"]
    
    # Format signals list
    signals_list = "\n".join([
        f"- {s.id}: {s.type.value} ({s.range})"
        for s in project.signals
    ])
    
    # Format detailed signals
    signals_detailed = "\n".join([
        f"""
Signal ID: {s.id}
  Type: {s.type.value}
  Range: {s.range}
  Unit: {s.unit or 'N/A'}
  Accuracy: {s.accuracy or 'N/A'}
  Description: {s.description or 'N/A'}
"""
        for s in project.signals
    ])
    
    # Format requirements
    requirements_list = "\n".join([
        f"- {r.id}: {r.text}"
        for r in project.requirements
    ])
    
    requirements_detailed = "\n".join([
        f"{r.id} [{r.priority}]: {r.text}"
        for r in project.requirements
    ])
    
    # Format the prompt
    # Note: We only fill variables that we calculated above.
    # The double curly braces in the template {{test_number}} remain as {test_number} for the AI.
    prompt = template.format(
        test_type=test_type.value,
        project_id=project.project_id,
        system_name=project.system,
        environment=project.environment,
        signal_count=len(project.signals),
        requirement_count=len(project.requirements),
        signals_list=signals_list,
        signals_detailed=signals_detailed,
        requirements_list=requirements_list,
        requirements_detailed=requirements_detailed,
        project_summary=f"{project.system} with {len(project.signals)} signals"
    )
    
    logger.debug(f"Generated prompt using version {version}", extra={
        'extra_data': {
            'version': version,
            'prompt_length': len(prompt)
        }
    })
    
    return prompt


def list_prompt_versions() -> Dict[str, str]:
    """Get all available prompt versions with descriptions"""
    return {
        version: details["description"]
        for version, details in PROMPTS.items()
    }


def get_prompt_version_info(version: str) -> Dict[str, str]:
    """Get detailed info about a specific prompt version"""
    if version not in PROMPTS:
        raise ValueError(f"Unknown prompt version: {version}")
    
    return {
        "version": version,
        "description": PROMPTS[version]["description"],
        "template_length": len(PROMPTS[version]["template"])
    }