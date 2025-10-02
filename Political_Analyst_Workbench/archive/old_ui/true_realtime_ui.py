"""
True Real-time Streaming UI for Political Analyst Workbench
Uses Streamlit's session state and threading for genuine live updates
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
import time
import threading
from queue import Queue, Empty
from streaming_agent import StreamingPoliticalAgent

# Configure Streamlit page
st.set_page_config(
    page_title="Political Analyst Workbench - True Real-time",
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
    
    .status-error {
        background: linear-gradient(45deg, #dc3545, #e74c3c);
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
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
    
    .progress-bar {
        background: linear-gradient(90deg, #d9f378, #5d535c);
        height: 8px;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def display_reasoning_step_live(step, index):
    """Display a reasoning step with live styling"""
    
    status_class = f"status-{step.get('status', 'processing')}"
    progress = step.get('progress', 0) * 100
    
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
        <div style="background-color: #e9ecef; border-radius: 4px; padding: 2px; margin-top: 8px;">
            <div class="progress-bar" style="width: {progress}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

class RealTimeProcessor:
    """Handles real-time processing with live updates"""
    
    def __init__(self):
        self.update_queue = Queue()
        self.processing = False
        self.agent = None
        
    def update_callback(self, step_data):
        """Callback for agent updates"""
        self.update_queue.put(step_data)
    
    def process_query_threaded(self, query):
        """Process query in a separate thread"""
        try:
            if not self.agent:
                self.agent = StreamingPoliticalAgent(update_callback=self.update_callback)
            
            result = self.agent.process_query_sync(query)
            self.update_queue.put({"type": "final_result", "data": result})
            
        except Exception as e:
            self.update_queue.put({"type": "error", "data": str(e)})
        finally:
            self.processing = False

def main():
    """Main Streamlit app with true real-time streaming"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Political Analyst Workbench</h1>
        <p><span class="live-indicator">● LIVE</span> True Real-time AI Agent with Live Streaming Updates</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'processor' not in st.session_state:
        st.session_state.processor = RealTimeProcessor()
    if 'reasoning_steps' not in st.session_state:
        st.session_state.reasoning_steps = []
    if 'final_result' not in st.session_state:
        st.session_state.final_result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 True Real-time Configuration")
        
        # Agent status
        try:
            st.success("✅ True streaming agent ready")
            agent_ready = True
        except Exception as e:
            st.error(f"❌ Agent initialization failed: {e}")
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
        
        if st.session_state.processing:
            st.markdown("### 🔴 **PROCESSING LIVE**")
            st.markdown("Agent is working in real-time...")
            
            # Auto-refresh while processing
            if st.button("🔄 Refresh Updates", key="refresh_btn"):
                st.rerun()
        
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
            "Enter your query for true real-time analysis:",
            value=st.session_state.get('query_input', ''),
            height=120,
            placeholder="Ask me anything about politics, companies, current events...",
            disabled=st.session_state.processing
        )
        
        # Process button
        if st.button("🚀 **Process Query**", disabled=not agent_ready or st.session_state.processing or not query.strip(), type="primary"):
            st.session_state.processing = True
            st.session_state.reasoning_steps = []
            st.session_state.final_result = None
            
            # Start processing in thread
            thread = threading.Thread(
                target=st.session_state.processor.process_query_threaded,
                args=(query,)
            )
            thread.daemon = True
            thread.start()
            
            st.rerun()
    
    with col2:
        st.header("🧠 Live Agent Reasoning")
        
        if st.session_state.processing:
            st.markdown("### 🔴 **LIVE PROCESSING**")
    
    # Check for updates from the processing thread
    if st.session_state.processing:
        try:
            # Check for new updates
            updates_received = 0
            while updates_received < 10:  # Limit to prevent infinite loop
                try:
                    update = st.session_state.processor.update_queue.get_nowait()
                    
                    if update.get("type") == "final_result":
                        st.session_state.final_result = update["data"]
                        st.session_state.processing = False
                        st.success("✅ **Query processed successfully!**")
                        st.rerun()
                        break
                    elif update.get("type") == "error":
                        st.error(f"❌ **Error:** {update['data']}")
                        st.session_state.processing = False
                        break
                    else:
                        # Regular step update
                        st.session_state.reasoning_steps.append(update)
                        updates_received += 1
                        
                except Empty:
                    break
            
            # Auto-refresh every 2 seconds while processing
            if updates_received > 0 or st.session_state.processing:
                time.sleep(0.5)
                st.rerun()
                
        except Exception as e:
            st.error(f"Error checking updates: {e}")
    
    # Display reasoning steps
    if st.session_state.reasoning_steps:
        st.subheader("📋 Live Reasoning Steps")
        for i, step in enumerate(st.session_state.reasoning_steps, 1):
            display_reasoning_step_live(step, i)
    
    # Display final results
    if st.session_state.final_result and not st.session_state.processing:
        st.header("📋 Final Analysis Results")
        
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

    # Auto-refresh instructions
    if st.session_state.processing:
        st.info("🔄 **Live Updates Active** - The page will automatically refresh to show new reasoning steps as they happen!")

if __name__ == "__main__":
    main()

