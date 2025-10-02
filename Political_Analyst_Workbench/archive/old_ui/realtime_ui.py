"""
Real-time UI for Political Analyst Workbench
Shows agent reasoning and working in real-time using Streamlit
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
import time
import threading
from queue import Queue
from simple_agent import SimplePoliticalAgent

# Configure Streamlit page
st.set_page_config(
    page_title="Political Analyst Workbench",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (Aistra color palette)
st.markdown("""
<style>
    .main-header {
        color: #1c1e20;
        font-family: 'Roboto Flex', sans-serif;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #d9f378, #5d535c);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .reasoning-step {
        background-color: #f8f9fa;
        border-left: 4px solid #d9f378;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    
    .step-title {
        color: #1c1e20;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    .step-details {
        color: #5d535c;
        margin-top: 0.5rem;
    }
    
    .response-box {
        background-color: #ffffff;
        border: 2px solid #d9f378;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-processing {
        background-color: #ffc107;
        animation: pulse 1.5s infinite;
    }
    
    .status-complete {
        background-color: #28a745;
    }
    
    .status-error {
        background-color: #dc3545;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

def display_reasoning_step(step, index, is_current=False):
    """Display a single reasoning step"""
    
    status_class = "status-processing" if is_current else "status-complete"
    
    st.markdown(f"""
    <div class="reasoning-step">
        <div class="step-title">
            <span class="status-indicator {status_class}"></span>
            Step {index}: {step['step'].replace('_', ' ').title()}
        </div>
        <div class="step-details">
            <strong>Action:</strong> {step['action']}<br>
            <strong>Details:</strong> {step['details']}<br>
            <strong>Time:</strong> {step['timestamp']}
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Political Analyst Workbench</h1>
        <p>Real-time AI Agent with Tavily Integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Agent status
        try:
            agent = SimplePoliticalAgent()
            st.success("✅ Agent initialized successfully")
            agent_ready = True
        except Exception as e:
            st.error(f"❌ Agent initialization failed: {e}")
            st.info("Please check your API keys in the .env file")
            agent_ready = False
        
        st.header("📊 Agent Graph Nodes")
        st.markdown("""
        **Current Agent Architecture:**
        
        1. **Analysis Node**
           - Analyzes user query
           - Determines if web search needed
        
        2. **Web Search Node**
           - Performs Tavily search
           - Handles search errors
        
        3. **LLM Processing Node**
           - Processes search results
           - Generates final response
        
        4. **Response Node**
           - Formats and returns response
           - Logs completion status
        """)
        
        st.header("🎯 Example Queries")
        example_queries = [
            "Find all AI players and companies in Gurugram",
            "What are the latest developments in US foreign policy?",
            "Analyze the current political situation in Ukraine",
            "List major tech companies in Bangalore",
            "What is the current status of climate change policies?"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query[:30]}...", key=query):
                st.session_state.query_input = query
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("💬 Query Input")
        
        # Query input
        query = st.text_area(
            "Enter your query:",
            value=st.session_state.get('query_input', ''),
            height=100,
            placeholder="Ask me anything about politics, companies, current events..."
        )
        
        # Process button
        if st.button("🚀 Process Query", disabled=not agent_ready):
            if query.strip():
                st.session_state.current_query = query
                st.session_state.processing = True
                st.rerun()
            else:
                st.warning("Please enter a query first!")
    
    with col2:
        st.header("🧠 Real-time Reasoning")
        
        # Reasoning display area
        reasoning_container = st.container()
    
    # Processing area
    if st.session_state.get('processing', False):
        
        with st.spinner("🤔 Agent is thinking..."):
            
            # Create placeholders for real-time updates
            progress_bar = st.progress(0)
            status_text = st.empty()
            reasoning_display = st.empty()
            
            try:
                # Process query
                result = agent.process_query_sync(st.session_state.current_query)
                
                # Display reasoning steps in real-time simulation
                for i, step in enumerate(result['reasoning_log']):
                    progress = (i + 1) / len(result['reasoning_log'])
                    progress_bar.progress(progress)
                    status_text.text(f"Step {i+1}/{len(result['reasoning_log'])}: {step['action']}")
                    
                    # Display reasoning step
                    with reasoning_display.container():
                        for j, prev_step in enumerate(result['reasoning_log'][:i+1]):
                            display_reasoning_step(prev_step, j+1, j == i)
                    
                    # Simulate real-time delay
                    time.sleep(0.5)
                
                # Store results
                st.session_state.last_result = result
                st.session_state.processing = False
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                st.success("✅ Query processed successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing query: {e}")
                st.session_state.processing = False
    
    # Display final results
    if st.session_state.get('last_result'):
        st.header("📋 Final Response")
        
        result = st.session_state.last_result
        
        # Response box
        st.markdown(f"""
        <div class="response-box">
            <h3>🤖 Agent Response:</h3>
            <p>{result['response']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Steps", result['total_steps'])
        
        with col2:
            st.metric("Response Length", f"{len(result['response'])} chars")
        
        with col3:
            processing_time = "N/A"
            if len(result['reasoning_log']) >= 2:
                start_time = datetime.fromisoformat(result['reasoning_log'][0]['timestamp'])
                end_time = datetime.fromisoformat(result['reasoning_log'][-1]['timestamp'])
                processing_time = f"{(end_time - start_time).total_seconds():.1f}s"
            st.metric("Processing Time", processing_time)
        
        # Detailed reasoning log
        with st.expander("🔍 Detailed Reasoning Log"):
            for i, step in enumerate(result['reasoning_log'], 1):
                st.json({
                    "step": i,
                    "type": step['step'],
                    "action": step['action'],
                    "details": step['details'],
                    "timestamp": step['timestamp']
                })
        
        # Raw search results
        if result.get('search_results'):
            with st.expander("🌐 Raw Search Results"):
                st.text(str(result['search_results'])[:2000] + "..." if len(str(result['search_results'])) > 2000 else str(result['search_results']))
        
        # Clear results button
        if st.button("🗑️ Clear Results"):
            for key in ['last_result', 'current_query', 'processing']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    main()
