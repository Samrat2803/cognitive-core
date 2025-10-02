"""
Enhanced Real-time Streaming UI for Political Analyst Workbench
Uses Streamlit's real-time capabilities for live agent reasoning display
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
import time
import threading
from queue import Queue
from streaming_agent import StreamingPoliticalAgent

# Configure Streamlit page
st.set_page_config(
    page_title="Political Analyst Workbench - Real-time",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced real-time styling
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
        transition: all 0.3s ease;
    }
    
    .reasoning-step:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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
    
    .response-box {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 3px solid #d9f378;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
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
        animation: pulse 2s infinite;
    }
    
    .status-error {
        background: linear-gradient(45deg, #dc3545, #e74c3c);
        box-shadow: 0 0 10px rgba(220, 53, 69, 0.3);
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .progress-container {
        background-color: #e9ecef;
        border-radius: 10px;
        padding: 3px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #d9f378, #5d535c);
        height: 20px;
        border-radius: 8px;
        transition: width 0.5s ease;
    }
    
    .live-indicator {
        color: #dc3545;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    .query-input {
        font-size: 1.1em;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #d9f378;
    }
</style>
""", unsafe_allow_html=True)

def display_reasoning_step_realtime(step, index, container):
    """Display a reasoning step with real-time styling"""
    
    status_class = f"status-{step.get('status', 'processing')}"
    progress = step.get('progress', 0) * 100
    
    with container:
        st.markdown(f"""
        <div class="reasoning-step">
            <div class="step-title">
                <span class="status-indicator {status_class}"></span>
                Step {index}: {step['action']}
            </div>
            <div class="step-details">
                <strong>Details:</strong> {step['details']}<br>
                <strong>Time:</strong> {step['timestamp']}<br>
                <strong>Progress:</strong> {progress:.1f}%
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main Streamlit app with real-time streaming"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Political Analyst Workbench</h1>
        <p><span class="live-indicator">● LIVE</span> Real-time AI Agent with Streaming Updates</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'reasoning_steps' not in st.session_state:
        st.session_state.reasoning_steps = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Real-time Configuration")
        
        # Agent status
        try:
            if 'agent' not in st.session_state:
                st.session_state.agent = StreamingPoliticalAgent()
            st.success("✅ Streaming agent ready")
            agent_ready = True
        except Exception as e:
            st.error(f"❌ Agent initialization failed: {e}")
            st.info("Please check your API keys in the .env file")
            agent_ready = False
        
        st.header("🎯 Quick Test Queries")
        example_queries = [
            "Find all AI players and companies in Gurugram",
            "What are the latest developments in US foreign policy?",
            "Analyze current political situation in Ukraine",
            "List major fintech companies in Bangalore",
            "Current status of climate change policies globally"
        ]
        
        for query in example_queries:
            if st.button(f"🚀 {query[:35]}...", key=f"example_{hash(query)}", disabled=st.session_state.processing):
                st.session_state.query_input = query
                st.rerun()
        
        if st.session_state.processing:
            st.markdown("### 🔴 **PROCESSING LIVE**")
            st.markdown("Agent is working in real-time...")
        
        # Clear button
        if st.button("🗑️ Clear All", disabled=st.session_state.processing):
            for key in ['reasoning_steps', 'final_result', 'query_input', 'current_step']:
                if key in st.session_state:
                    st.session_state[key] = [] if key == 'reasoning_steps' else (0 if key == 'current_step' else None)
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.header("💬 Query Input")
        
        # Query input with enhanced styling
        query = st.text_area(
            "Enter your query for real-time analysis:",
            value=st.session_state.get('query_input', ''),
            height=120,
            placeholder="Ask me anything about politics, companies, current events...",
            key="query_textarea",
            disabled=st.session_state.processing
        )
        
        # Process button
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🚀 **Process Query**", disabled=not agent_ready or st.session_state.processing or not query.strip(), type="primary"):
                st.session_state.current_query = query
                st.session_state.processing = True
                st.session_state.reasoning_steps = []
                st.session_state.current_step = 0
                st.rerun()
        
        with col_btn2:
            if st.button("⏹️ Stop", disabled=not st.session_state.processing):
                st.session_state.processing = False
                st.rerun()
    
    with col2:
        st.header("🧠 Live Agent Reasoning")
        
        if st.session_state.processing:
            st.markdown("### 🔴 **LIVE PROCESSING**")
        
        # Real-time reasoning display
        reasoning_container = st.container()
    
    # Process query with real-time updates
    if st.session_state.processing and 'current_query' in st.session_state:
        
        # Create update callback for real-time streaming
        def update_callback(step_data):
            st.session_state.reasoning_steps.append(step_data)
            st.session_state.current_step += 1
        
        # Set up the agent with callback
        st.session_state.agent.update_callback = update_callback
        
        # Progress indicators
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # Process query asynchronously
            with st.spinner("🤔 Agent is thinking..."):
                
                # Create a container for live updates
                live_container = st.empty()
                
                # Start processing
                result = asyncio.run(st.session_state.agent.process_query_streaming(st.session_state.current_query))
                
                # Display final results
                st.session_state.final_result = result
                st.session_state.processing = False
                
                st.success("✅ **Query processed successfully!**")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ **Error processing query:** {e}")
            st.session_state.processing = False
    
    # Display reasoning steps in real-time
    if st.session_state.reasoning_steps:
        with reasoning_container:
            for i, step in enumerate(st.session_state.reasoning_steps, 1):
                step_container = st.empty()
                display_reasoning_step_realtime(step, i, step_container)
    
    # Display final results
    if st.session_state.get('final_result') and not st.session_state.processing:
        st.header("📋 Final Analysis Results")
        
        result = st.session_state.final_result
        
        # Response box with enhanced styling
        st.markdown(f"""
        <div class="response-box">
            <h3>🤖 Agent Response:</h3>
            <div style="white-space: pre-wrap; line-height: 1.6;">{result['response']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Steps", result['total_steps'])
        
        with col2:
            st.metric("📝 Response Length", f"{len(result['response'])} chars")
        
        with col3:
            if len(result['reasoning_log']) >= 2:
                start_time = datetime.fromisoformat(result['reasoning_log'][0]['timestamp'])
                end_time = datetime.fromisoformat(result['reasoning_log'][-1]['timestamp'])
                processing_time = f"{(end_time - start_time).total_seconds():.1f}s"
            else:
                processing_time = "N/A"
            st.metric("⏱️ Processing Time", processing_time)
        
        with col4:
            st.metric("✅ Status", result.get('status', 'completed').title())
        
        # Expandable sections
        with st.expander("🔍 **Detailed Reasoning Timeline**"):
            for i, step in enumerate(result['reasoning_log'], 1):
                st.json({
                    "step": i,
                    "type": step['step'],
                    "action": step['action'],
                    "details": step['details'],
                    "timestamp": step['timestamp'],
                    "progress": f"{step.get('progress', 0) * 100:.1f}%"
                })
        
        with st.expander("🌐 **Raw Search Results**"):
            if result.get('search_results'):
                search_text = str(result['search_results'])
                if len(search_text) > 3000:
                    st.text(search_text[:3000] + "\n\n... (truncated for display)")
                else:
                    st.text(search_text)
            else:
                st.info("No search results available")

if __name__ == "__main__":
    main()

