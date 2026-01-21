"""Main Streamlit Dashboard"""
import streamlit as st
import json
import os
import sys
from app.render.pdf_renderer import PDFRenderer


# Ensure app modules can be imported if running directly
sys.path.append(os.getcwd())

from app.core.models import Project, Signal, SignalType, Requirement, TestType
from app.ai.generator import create_generator
from app.rules.validation import validate_all
from app.web.components.metrics_display import display_metrics

# Page Config
st.set_page_config(
    page_title="InduSense AI Test Gen",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    # GENERIC LOGO (Industrial/Scientific Theme)
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
    
    # Prompt Versioning (Advanced Feature)
    prompt_ver = st.selectbox(
        "Prompt Strategy",
        options=["v1.2 (Safety Focused)", "v1.1 (Standard)", "v1.0 (Basic)"],
        index=0
    )
    selected_version = prompt_ver.split()[0] # Extract "v1.2"
    
    st.divider()
    
    test_type = st.selectbox(
        "Test Procedure Type",
        options=[t.value for t in TestType],
        index=0
    )
    
    api_key_input = ""
    if "OpenAI" in provider_mode:
        api_key_input = st.text_input("OpenAI API Key", type="password")
        if not api_key_input:
            st.warning("⚠️ API Key required for Production mode")

# --- MAIN INTERFACE ---
st.title("⚡ AI-Assisted Test Procedure Generator")
st.markdown("""
**Pilot Status:** 🟢 Active | **Engine:** Hybrid (Rule-based + LLM)
""")

# Two columns: Input (Left) and Output (Right)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Project Definition")
    
    # Helper to load sample data
    if st.button("📝 Load Sample Data"):
        sample_data = {
            "project_id": "P-2026-PILOT",
            "system": "Indigo500 Transmitter",
            "environment": "Cleanroom Class 5",
            "signals": [
                {"id": "SIG-TMP-01", "type": "Temperature", "range": "-40 to 80 C", "unit": "C", "accuracy": "0.1 C"},
                {"id": "SIG-HUM-01", "type": "Humidity", "range": "0 to 100 %RH", "unit": "%", "accuracy": "1.0 %"}
            ],
            "requirements": [
                {"id": "REQ-ACC-01", "text": "Sensor must stabilize within 2 mins", "priority": "HIGH"},
                {"id": "REQ-SAF-01", "text": "High alarm trigger at 75 C", "priority": "CRITICAL"}
            ]
        }
        st.session_state['project_json'] = json.dumps(sample_data, indent=2)

    # Text Area for JSON Input
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
            # 1. Parse JSON Input
            if not json_input:
                st.error("Please provide project data.")
                st.stop()
                
            data = json.loads(json_input)
            
            # 2. Convert to Domain Models
            signals = [
                Signal(
                    id=s['id'], 
                    type=SignalType(s['type']), 
                    range=s['range'],
                    unit=s.get('unit'),
                    accuracy=s.get('accuracy')
                ) 
                for s in data['signals']
            ]
            requirements = [
                Requirement(id=r['id'], text=r['text'], priority=r.get('priority', 'MEDIUM')) 
                for r in data.get('requirements', [])
            ]
            
            project = Project(
                project_id=data['project_id'],
                system=data['system'],
                environment=data['environment'],
                signals=signals,
                requirements=requirements
            )
            
            # 3. Configure Generator
            provider_arg = "mock" if "Mock" in provider_mode else "openai"
            
            generator = create_generator(provider_name=provider_arg)
            
            with st.spinner("🤖 AI is analyzing requirements and generating tests..."):
                result = generator.generate(
                    project=project, 
                    test_type=TestType(test_type),
                    prompt_version=selected_version
                )
                content = result['content']
                metadata = result['metadata']
                
            # 4. Show Result
            st.success(f"Generation Complete! ({metadata['generation_time_sec']}s)")
            
            # Tabs for Document vs Validation
            tab_doc, tab_val, tab_raw = st.tabs(["📄 Document", "✅ Validation", "📊 Metrics"])
            
            with tab_doc:
                st.markdown(content)
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(
                        "📥 Download Markdown",
                        data=content,
                        file_name=f"test_{project.project_id}.md"
                    )
                with col_d2:
                    # PDF Generation Logic
                    pdf_renderer = PDFRenderer()
                    pdf_data = pdf_renderer.render(content, project.project_id)
                    st.download_button(
                        "📄 Download PDF",
                        data=pdf_data,
                        file_name=f"test_{project.project_id}.pdf",
                        mime="application/pdf"
                    )
            
            with tab_val:
                # Run Validation Engine
                val_result = validate_all(content, project, test_type)
                
                # Visual Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Coverage", f"{val_result.coverage_pct}%", delta_color="normal" if val_result.coverage_pct == 100 else "inverse")
                c2.metric("Errors", len(val_result.errors), delta_color="inverse")
                c3.metric("Warnings", len(val_result.warnings), delta_color="inverse")
                
                if val_result.passed:
                    st.success("PASSED: All signals are covered and structure is valid.")
                else:
                    st.error("FAILED: Critical validation checks failed.")
                    if val_result.missing_signals:
                        st.write("❌ **Missing Tests for Signals:**")
                        st.write(val_result.missing_signals)
            
            with tab_raw:
                display_metrics(metadata)
                with st.expander("Debug JSON"):
                    st.json(result)

        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please check your input.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)