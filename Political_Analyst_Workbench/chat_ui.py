"""
Simple Chat UI with Graph Visualization
Run with: streamlit run chat_ui.py
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import asyncio
import os
from datetime import datetime
from langgraph_master_agent.main import MasterPoliticalAnalyst
from langgraph_master_agent.graph import create_master_agent_graph

# Page config
st.set_page_config(
    page_title="Political Analyst Agent",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .step-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
        color: #000;
    }
    .step-title {
        font-weight: bold;
        color: #1976D2;
        font-size: 1.1em;
        margin-bottom: 8px;
    }
    .step-detail {
        margin: 5px 0;
        padding: 8px;
        background-color: #fff;
        border-radius: 4px;
    }
    .input-label {
        font-weight: bold;
        color: #FF6B6B;
    }
    .output-label {
        font-weight: bold;
        color: #51CF66;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎯 Political Analyst Agent")
st.markdown("**Master Agent with LangGraph Visualization**")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    st.session_state.agent = MasterPoliticalAnalyst()

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Agent Graph Architecture")
    
    # Show graph structure
    st.markdown("""
    ```
    START
      ↓
    [Conversation Manager]
      ↓
    [Strategic Planner]
      ↓
    [Tool Executor]
      ↓
    [Decision Gate]
      ↓ (loop or continue)
      ↓
    [Response Synthesizer]
      ↓
    END
    ```
    """)
    
    st.markdown("---")
    
    # Graph visualization
    try:
        app = create_master_agent_graph()
        mermaid = app.get_graph().draw_mermaid()
        
        st.markdown("**Mermaid Diagram:**")
        st.code(mermaid, language="mermaid")
        
        st.info("💡 Copy the mermaid code above and paste at [mermaid.live](https://mermaid.live/) for interactive visualization")
        
    except Exception as e:
        st.error(f"Could not generate graph: {e}")

with col2:
    st.subheader("💬 Chat Interface")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "metadata" in msg:
                with st.expander("📊 Execution Details"):
                    st.json(msg["metadata"])
    
    # Chat input
    if prompt := st.chat_input("Ask about politics, news, or request analysis..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show assistant response
        with st.chat_message("assistant"):
            # Create placeholder for live updates
            status_placeholder = st.empty()
            response_placeholder = st.empty()
            
            status_placeholder.info("🔄 Processing your query...")
            
            # Process query
            try:
                result = asyncio.run(st.session_state.agent.process_query(prompt))
                
                # Show execution log
                with st.expander("🔍 Execution Steps", expanded=True):
                    for i, step in enumerate(result.get('execution_log', []), 1):
                        # Create a container for each step
                        with st.container():
                            st.markdown(f"### Step {i}: {step.get('step', 'Unknown')}")
                            st.markdown(f"**Action:** {step.get('action', '')}")
                            
                            if step.get('details'):
                                st.markdown(f"**Details:** {step.get('details', '')}")
                            
                            # Input/Output in columns
                            col_in, col_out = st.columns(2)
                            
                            with col_in:
                                st.markdown("**📥 Input:**")
                                step_input = step.get('input', 'N/A')
                                if isinstance(step_input, str):
                                    st.info(step_input[:300] + "..." if len(str(step_input)) > 300 else step_input)
                                else:
                                    st.info(str(step_input)[:300])
                            
                            with col_out:
                                st.markdown("**📤 Output:**")
                                step_output = step.get('output', 'N/A')
                                if isinstance(step_output, str):
                                    st.success(step_output[:300] + "..." if len(str(step_output)) > 300 else step_output)
                                else:
                                    st.success(str(step_output)[:300])
                            
                            st.markdown("---")
                
                # Show response
                status_placeholder.success(f"✅ Complete! (Confidence: {result['confidence']:.0%})")
                response_placeholder.markdown(result['response'])
                
                # Show artifact if created
                if result.get('artifact'):
                    st.success("🎨 **Artifact Created!**")
                    
                    artifact = result['artifact']
                    artifact_type = artifact.get('type', 'unknown')
                    
                    col_art1, col_art2 = st.columns([2, 1])
                    
                    with col_art1:
                        # Preview artifact (if HTML/image)
                        if artifact_type in ['bar_chart', 'line_chart', 'mind_map']:
                            html_path = artifact.get('html_path', '')
                            if os.path.exists(html_path):
                                with open(html_path, 'r') as f:
                                    html_content = f.read()
                                st.components.v1.html(html_content, height=500, scrolling=True)
                    
                    with col_art2:
                        st.markdown(f"**Type:** {artifact_type.replace('_', ' ').title()}")
                        st.markdown(f"**ID:** `{artifact.get('artifact_id', 'N/A')}`")
                        
                        # Download buttons
                        html_path = artifact.get('html_path', '')
                        png_path = artifact.get('png_path', '')
                        
                        if os.path.exists(html_path):
                            with open(html_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download HTML",
                                    data=f.read(),
                                    file_name=f"{artifact['artifact_id']}.html",
                                    mime="text/html"
                                )
                        
                        if os.path.exists(png_path):
                            with open(png_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download PNG",
                                    data=f.read(),
                                    file_name=f"{artifact['artifact_id']}.png",
                                    mime="image/png"
                                )
                
                # Show metadata
                with st.expander("📈 Metadata"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Tools Used", ", ".join(result['tools_used']))
                    with col_b:
                        st.metric("Iterations", result['iterations'])
                    with col_c:
                        st.metric("Confidence", f"{result['confidence']:.0%}")
                    
                    if result['citations']:
                        st.markdown("**📚 Citations:**")
                        for i, citation in enumerate(result['citations'], 1):
                            st.markdown(f"{i}. [{citation['title']}]({citation['url']})")
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['response'],
                    "metadata": {
                        "tools": result['tools_used'],
                        "iterations": result['iterations'],
                        "confidence": result['confidence'],
                        "citations": result['citations']
                    }
                })
                
            except Exception as e:
                status_placeholder.error(f"❌ Error: {str(e)}")
                st.error(f"Failed to process query: {e}")

# Sidebar with info
with st.sidebar:
    st.subheader("ℹ️ Agent Information")
    
    st.markdown("""
    **Available Tools:**
    - 🔍 Tavily Search
    - 📄 Tavily Extract
    - 🕷️ Tavily Crawl
    - 📊 Sentiment Analysis (coming soon)
    
    **Visualizations:**
    - 📊 Bar Charts (categorical data)
    - 📈 Line Charts (trends)
    - 🧠 Mind Maps (concepts)
    
    **Features:**
    - Real-time web search
    - Multi-step reasoning
    - Auto artifact creation
    - Source citations
    - Confidence scoring
    """)
    
    st.markdown("---")
    
    st.subheader("🎨 LangGraph Studio")
    st.markdown("[Open Studio UI](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024)")
    
    st.markdown("---")
    
    st.subheader("📊 LangSmith Traces")
    st.markdown("[View Traces](https://smith.langchain.com/)")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #5d535c;'>
    <small>Powered by LangGraph • OpenAI • Tavily</small>
</div>
""", unsafe_allow_html=True)

