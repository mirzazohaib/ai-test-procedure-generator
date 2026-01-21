[⬅️ Back to README](../README.md)

---

# 🔌 API Reference (Internal)

This project is structured as a modular Python package. While currently accessed via a Web UI, the core modules are designed to be imported and used in other automation pipelines.

## 1. Core Models (`app.core.models`)

### `Project`

The root entity representing the engineering project.

```python
class Project(BaseModel):
    project_id: str
    system: str
    signals: List[Signal]
    requirements: List[Requirement]
```

### `Signal`

Represents a physical I/O point.

```python
class Signal(BaseModel):
    id: str         # e.g., "SIG-TMP-01"
    type: SignalType # Analog, Digital, etc.
    range: str      # e.g., "4-20mA"
```

## 2. Generator Factory (`app.ai.generator`)

The main entry point for generating content.

`create_generator(provider_name: str)`
Factory method to instantiate an AI backend.

- Args: `provider_name` ("openai" | "mock")

- Returns: An instance implementing `AIProvider`.

Example:

```python
from app.ai.generator import create_generator

# Initialize
gen = create_generator("openai")

# Generate
result = gen.generate(project, test_type="FAT")
print(result['content'])
```

## 3. Validation Engine (`app.rules.validation`)

`validate_all(content: str, project: Project)`
Runs a full suite of compliance checks on the generated text.

- Returns: `ValidationResult` object containing:
  - `passed` (bool): Overall status.

  - `coverage_pct` (float): 0-100% signal coverage.

  - `missing_signals` (List[str]): IDs of ignored signals.

  - `errors` (List[str]): Critical failures.

```python
from app.rules.validation import validate_all

report = validate_all(generated_markdown, project_data)
if not report.passed:
    print(f"Failed! Missing: {report.missing_signals}")
```
