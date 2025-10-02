"""
Clean Streamlit UI for Political Analyst Workbench
Port 8500 - LangFuse Tracing
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
import time
import threading
from queue import Queue, Empty
from langfuse_agent import LangFuseAgent

# Configure Streamlit page
st.set_page_config(
    page_title="Political Analyst Workbench - Clean UI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Aistra theme
st.markdown("""
<style>
    .main-header {
        color: #1c1e20;
        font-family: 'Roboto Flex', sans-serif;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #d9f378, #5d535c);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .reasoning-step {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-left: 5px solid #d9f378;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .step-title {
        color: #1c1e20;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 0.5rem;
    }
    
    .step-details {
        color: #5d535c;
        font-size: 0.95em;
        line-height: 1.4;
    }
    
    .status-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    .status-processing {
        background: linear-gradient(45deg, #ffc107, #ff9800);
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
    }
    
    .status-completed {
        background: linear-gradient(45deg, #28a745, #20c997);
        box-shadow: 0 0 10px rgba(40, 167, 69, 0.3);
    }
    
    .status-warning {
        background: linear-gradient(45deg, #fd7e14, #ffc107);
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #d9f378, #5d535c);
        height: 8px;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def display_reasoning_step(step, index):
    """Display a reasoning step with input/output"""
    
    status_class = f"status-{step.get('status', 'processing')}"
    progress = step.get('progress', 0) * 100
    
    # Get input and output
    step_input = step.get('input', 'N/A')
    step_output = step.get('output', 'N/A')
    
    st.markdown(f"""
    <div class="reasoning-step">
        <div class="step-title">
            <span class="status-indicator {status_class}"></span>
            Step {index}: {step['action']}
        </div>
        <div class="step-details">
            <strong>📥 Input:</strong><br>
            <div style="background: rgba(217, 243, 120, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; font-family: 'Courier New', monospace; font-size: 0.9em; white-space: pre-wrap;">{step_input}</div>
            
            <strong>📤 Output:</strong><br>
            <div style="background: rgba(93, 83, 92, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; font-family: 'Courier New', monospace; font-size: 0.9em; white-space: pre-wrap;">{step_output}</div>
            
            <strong>ℹ️ Details:</strong> {step['details']}<br>
            <strong>⏰ Time:</strong> {step['timestamp']}<br>
            <strong>📊 Progress:</strong> {progress:.1f}%
        </div>
        <div style="background-color: #e9ecef; border-radius: 4px; padding: 2px; margin-top: 8px;">
            <div class="progress-bar" style="width: {progress}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Political Analyst Workbench</h1>
        <p>🔍 <strong>LangFuse Tracing</strong> | Real-time AI Agent Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'reasoning_steps' not in st.session_state:
        st.session_state.reasoning_steps = []
    if 'final_result' not in st.session_state:
        st.session_state.final_result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Agent status
        try:
            if 'agent' not in st.session_state:
                st.session_state.agent = LangFuseAgent()
            st.success("✅ LangFuse agent ready")
            st.info("🔍 Traces: http://localhost:3761")
            agent_ready = True
        except Exception as e:
            st.error(f"❌ Agent failed: {e}")
            agent_ready = False
        
        st.header("🎯 Quick Queries")
        example_queries = [
            "Find all AI players and companies in Gurugram",
            "Latest developments in US foreign policy",
            "Current political situation in Ukraine",
            "Major fintech companies in Bangalore",
            "Climate change policies globally"
        ]
        
        for query in example_queries:
            if st.button(f"🚀 {query[:35]}...", key=f"ex_{hash(query)}", disabled=st.session_state.processing):
                st.session_state.query_input = query
        
        # Clear button
        if st.button("🗑️ Clear All", disabled=st.session_state.processing):
            st.session_state.reasoning_steps = []
            st.session_state.final_result = None
            st.session_state.query_input = ""
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.header("💬 Query Input")
        
        # Query input
        query = st.text_area(
            "Enter your query:",
            value=st.session_state.get('query_input', ''),
            height=120,
            placeholder="Ask about politics, companies, current events...",
            disabled=st.session_state.processing
        )
        
        # Process button
        if st.button("🚀 **Analyze**", disabled=not agent_ready or st.session_state.processing or not query.strip(), type="primary"):
            st.session_state.processing = True
            st.session_state.reasoning_steps = []
            st.session_state.final_result = None
            
            # Create update callback
            def update_callback(step_data):
                st.session_state.reasoning_steps.append(step_data)
            
            # Set callback and process
            st.session_state.agent.update_callback = update_callback
            
            with st.spinner("🤔 Agent analyzing..."):
                try:
                    result = st.session_state.agent.process_query_sync(query)
                    st.session_state.final_result = result
                    st.session_state.processing = False
                    st.success("✅ Analysis complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.session_state.processing = False
    
    with col2:
        st.header("🧠 Agent Reasoning")
        
        # Display reasoning steps
        if st.session_state.reasoning_steps:
            for i, step in enumerate(st.session_state.reasoning_steps, 1):
                display_reasoning_step(step, i)
    
    # Display final results
    if st.session_state.final_result and not st.session_state.processing:
        st.header("📋 Analysis Results")
        
        result = st.session_state.final_result
        
        # Response box
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ffffff, #f8f9fa); border: 3px solid #d9f378; border-radius: 15px; padding: 2rem; margin: 1.5rem 0; box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);">
            <h3>🤖 Agent Response:</h3>
            <div style="white-space: pre-wrap; line-height: 1.6;">{result['response']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Steps", result['total_steps'])
        
        with col2:
            st.metric("📝 Length", f"{len(result['response'])} chars")
        
        with col3:
            if len(result['reasoning_log']) >= 2:
                start_time = datetime.fromisoformat(result['reasoning_log'][0]['timestamp'])
                end_time = datetime.fromisoformat(result['reasoning_log'][-1]['timestamp'])
                processing_time = f"{(end_time - start_time).total_seconds():.1f}s"
            else:
                processing_time = "N/A"
            st.metric("⏱️ Time", processing_time)
        
        with col4:
            st.metric("✅ Status", result.get('status', 'completed').title())
        
        # LangFuse link
        if result.get('langfuse_url'):
            st.info(f"🔍 **View detailed traces**: {result['langfuse_url']}")

if __name__ == "__main__":
    main()
