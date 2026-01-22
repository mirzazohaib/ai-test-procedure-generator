# ⚡ AI-Assisted Test Procedure Generator (InduSense)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI Pipeline](https://github.com/mirzazohaib/ai-test-procedure-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/mirzazohaib/ai-test-procedure-generator/actions)
[![Azure Deployment](https://github.com/mirzazohaib/ai-test-procedure-generator/actions/workflows/deploy_azure.yml/badge.svg)](https://github.com/mirzazohaib/ai-test-procedure-generator/actions)
[![Live App](https://img.shields.io/badge/Azure-Live%20App-0078D4?style=flat&logo=microsoft-azure&logoColor=white)](https://indusense-app-h3cbeah2hfcpdqds.francecentral-01.azurewebsites.net/)

> **Automating the critical path from Engineering Requirements to FAT/SAT Procedures.**

---

### 🚀 Live Demo

**[👉 Click here to launch the App on Azure](https://indusense-app-h3cbeah2hfcpdqds.francecentral-01.azurewebsites.net/)**

![InduSense Demo](docs/DEMO.gif)
_Generating a compliant Factory Acceptance Test in < 2 seconds._

---

## 📖 Overview

In industrial automation (HVAC, Manufacturing, Sensing), engineers spend up to **40% of their time** writing manual test documentation. This "End-to-End" pilot project demonstrates how a **Hybrid AI Engine** can reduce this time to seconds while maintaining strict engineering compliance.

**Key Capabilities:**

- **📄 PDF Generation:** Auto-creates professional, signed PDF reports using `ReportLab`.
- **🛡️ Validation Engine:** Deterministic rule-checks ensure 100% signal coverage (prevents AI hallucinations).
- **💰 Cost Analytics:** Live tracking of Token usage and USD/EUR conversion rates.
- **🧠 Hybrid Intelligence:** Uses LLMs (OpenAI GPT-4) for creative text generation but enforces strict Logic constraints for safety.

---

## 🏗️ System Architecture

The system follows a modular **Hexagonal Architecture** to separate core logic from the AI providers.

- **Core:** Domain models (`Project`, `Signal`, `Requirement`).
- **AI Layer:** Pluggable providers (Mock for testing, OpenAI for Production).
- **Interface:** Streamlit Dashboard for rapid prototyping.

---

## 🛠️ Tech Stack

- Frontend: Streamlit (Python)
- Core Logic: Pydantic (Data Validation), Python 3.11
- AI Integration: OpenAI API, AsyncIO
- Document Generation: ReportLab (PDF), FPDF
- Infrastructure: Azure Web Apps, GitHub Actions (CI/CD)

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone [https://github.com/mirzazohaib/ai-test-procedure-generator.git](https://github.com/mirzazohaib/ai-test-procedure-generator.git)
cd ai-test-procedure-generator

python -m venv venv
# Windows
source venv/Scripts/activate

pip install -r requirements.txt
```

### 2. Configuration

The app runs in Mock Mode by default (free, no API key required).

To enable real GPT-4 generation, create a .env file:

```bash
OPENAI_API_KEY=sk-proj-12345...
```

### 3. Run the App

```bash
# Run the main entry point (Project Root)
streamlit run app/main.py
```

---

## 📚 Documentation

Detailed documentation for developers and integrators:

- [📂 Project Architecture](docs/ARCHITECTURE.md) - Deep dive into Hexagonal layers and logic.

- [🚀 Deployment Guide](docs/DEPLOYMENT.md) - Docker and Cloud deployment strategies.

- [🔌 API Reference](docs/API.md) - Internal module interfaces and AI Provider contracts.

---

### ⚖️ Disclaimer

This is a personal portfolio project. It is a conceptual prototype designed to demonstrate software architecture and Generative AI capabilities in an engineering context. It is not affiliated with, endorsed by, or connected to any specific hardware manufacturer or company. All logos and system names used in examples are fictional or generic.

---

### 📜 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
