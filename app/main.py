"""
Main Streamlit Dashboard - InduSense AI Test Gen
"""
import streamlit as st
import json
import os
import sys
import time

# Fix path to ensure imports work from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Core Modules
from app.core.models import Project, Signal, SignalType, Requirement, TestType
from app.ai.generator import create_generator

# Import UI Components (We will create these next)
try:
    from app.render.pdf_renderer import PDFRenderer
    from app.web.components.metrics_display import display_metrics
    from app.rules.validation import validate_all
except ImportError:
    # Fallback if helper files aren't created yet
    st.error("⚠️ Dependency Error: Helper modules not found. Please create 'app/render/pdf_renderer.py' and 'app/web/components/metrics_display.py'")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="InduSense AI Test Gen",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/sensor.png", width=80)
    st.markdown("### InduSense Analytics")
    st.caption("v1.0.0-pilot")
    st.divider()
    
    st.header("⚙️ Configuration")
    
    # Provider Selection
    provider_mode = st.radio(
        "AI Provider",
        options=["Mock (Free)", "OpenAI (Production)"],
        index=0
    )
    
    st.divider()
    
    # Prompt Versioning
    prompt_ver = st.selectbox(
        "Prompt Strategy",
        options=["v1.2 (Safety Focused)", "v1.1 (Standard)", "v1.0 (Basic)"],
        index=0
    )
    selected_version = prompt_ver.split()[0]
    
    st.divider()
    
    test_type_str = st.selectbox(
        "Test Procedure Type",
        options=[t.name for t in TestType],
        index=0
    )
    
    # API Key Input
    api_key_input = ""
    if "OpenAI" in provider_mode:
        env_key = os.getenv("OPENAI_API_KEY", "")
        api_key_input = st.text_input("OpenAI API Key", value=env_key, type="password")
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
        elif not env_key:
            st.warning("⚠️ API Key required for Production mode")

# --- MAIN INTERFACE ---
st.title("⚡ AI-Assisted Test Procedure Generator")
st.markdown("**Pilot Status:** 🟢 Active | **Engine:** Hybrid (Rule-based + LLM)")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Project Definition")
    
    # Sample Data Button
    if st.button("📝 Load Sample Data"):
        sample_data = {
            "project_id": "P-2026-PILOT",
            "system": "Indigo500 Transmitter",
            "environment": "Cleanroom Class 5",
            "signals": [
                {"id": "SIG-TMP-01", "type": "TEMPERATURE", "range": "-40 to 80 C", "unit": "C", "accuracy": "0.1 C"},
                {"id": "SIG-HUM-01", "type": "HUMIDITY", "range": "0 to 100 %RH", "unit": "%", "accuracy": "1.0 %"}
            ],
            "requirements": [
                {"id": "REQ-ACC-01", "text": "Sensor must stabilize within 2 mins", "priority": "HIGH"},
                {"id": "REQ-SAF-01", "text": "High alarm trigger at 75 C", "priority": "CRITICAL"}
            ]
        }
        st.session_state['project_json'] = json.dumps(sample_data, indent=2)

    # JSON Input
    json_input = st.text_area(
        "Paste Project JSON here:",
        value=st.session_state.get('project_json', ''),
        height=400,
        help="Define signals and requirements in JSON format."
    )

    generate_btn = st.button("🚀 Generate Procedure", type="primary", use_container_width=True)

# --- GENERATION LOGIC ---
if generate_btn:
    with col2:
        st.subheader("2. Generated Output")
        
        try:
            # 1. Parse JSON
            if not json_input:
                st.error("Please provide project data.")
                st.stop()
                
            data = json.loads(json_input)
            
            # 2. Build Models
            signals = []
            for s in data.get('signals', []):
                # Robust Enum Conversion
                try:
                    s_type = SignalType[s['type'].upper()]
                except KeyError:
                    s_type = SignalType.TEMPERATURE
                signals.append(Signal(id=s['id'], type=s_type, range=s['range']))

            requirements = [
                Requirement(id=r['id'], text=r['text']) 
                for r in data.get('requirements', [])
            ]
            
            project = Project(
                project_id=data.get('project_id', 'Unk'),
                system=data.get('system', 'Unk'),
                environment=data.get('environment', 'Unk'),
                signals=signals,
                requirements=requirements
            )
            
            # 3. Run Generator
            provider_arg = "mock" if "Mock" in provider_mode else "openai"
            generator = create_generator(provider_arg)
            
            with st.spinner("🤖 AI is analyzing requirements..."):
                # Handle Sync/Async seamlessly
                import asyncio
                if asyncio.iscoroutinefunction(generator.generate):
                    result = asyncio.run(generator.generate(project, TestType[test_type_str], prompt_version=selected_version))
                else:
                    result = generator.generate(project, TestType[test_type_str], prompt_version=selected_version)
            
            # 4. Display Results
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            
            st.success(f"Generation Complete! ({metadata.get('generation_time_sec', 0.5)}s)")
            
            tab_doc, tab_val, tab_raw = st.tabs(["📄 Document", "✅ Validation", "📊 Metrics"])
            
            with tab_doc:
                st.markdown(content)
                
                # PDF & Markdown Downloads
                c1, c2 = st.columns(2)
                c1.download_button("📥 Download Markdown", content, f"{project.project_id}.md")
                
                # PDF Rendering
                try:
                    pdf_renderer = PDFRenderer()
                    pdf_data = pdf_renderer.render(content, project.project_id)
                    c2.download_button("📄 Download PDF", pdf_data, f"{project.project_id}.pdf", mime="application/pdf")
                except Exception as e:
                    c2.error(f"PDF Error: {e}")
            
            with tab_val:
                # Validation Engine
                try:
                    val_result = validate_all(content, project, test_type_str)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Coverage", f"{val_result.coverage_pct}%")
                    m2.metric("Errors", len(val_result.errors))
                    m3.metric("Warnings", len(val_result.warnings))
                    
                    if val_result.passed:
                        st.success("✅ Validation Passed")
                    else:
                        st.error("❌ Validation Failed")
                        st.write("Missing Signals:", val_result.missing_signals)
                except Exception as e:
                    st.warning(f"Validation engine not fully configured: {e}")

            with tab_raw:
                display_metrics(metadata)
                st.json(result)

        except json.JSONDecodeError:
            st.error("Invalid JSON format.")
        except Exception as e:
            st.error(f"Error: {str(e)}")