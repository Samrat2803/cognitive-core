"""
Synthesizer Node - Generate final response with summary and recommendations
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from typing import Dict, Any
from state import CognitiveCrawlerState
from openai import AsyncOpenAI
from config import MODEL, TEMPERATURE
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../.env'))

client = AsyncOpenAI()


async def synthesizer(state: CognitiveCrawlerState) -> Dict[str, Any]:
    """
    Synthesize final response based on workflow results
    
    Generates:
    - Summary
    - Key findings
    - Recommendations
    - Confidence score
    """
    
    action = state.get("action", "query")
    query = state["query"]
    
    print(f"\n📊 Synthesizer: Generating final response...")
    
    state["execution_log"].append({
        "step": "synthesizer",
        "action": "Synthesizing final response"
    })
    
    try:
        # Build context based on action
        if action == "discover":
            portals = state.get("portals_discovered", [])
            listing_pages = state.get("listing_pages", [])
            context = f"""
            Query: {query}
            
            Discovered Portals: {len(portals)}
            Tender Listing Pages Found: {len(listing_pages)}
            
            Top Portals:
            {chr(10).join([f"- {p.get('title', 'Unknown')}: {p.get('url', 'N/A')}" for p in portals[:5]])}
            """
            
        elif action == "crawl":
            tenders_stored = state.get("tenders_stored", 0)
            embeddings = state.get("embeddings_generated", 0)
            context = f"""
            Query: {query}
            
            Tenders Crawled and Stored: {tenders_stored}
            Embeddings Generated: {embeddings}
            """
            
        else:  # chat/query - RAG mode
            relevant_tenders = state.get("relevant_tenders", [])
            
            if relevant_tenders:
                # Build context from relevant documents for RAG
                context_docs = []
                sources = []
                for t in relevant_tenders[:5]:  # Top 5 most relevant
                    content = t.get('content', '')[:500]  # First 500 chars
                    url = t.get('metadata', {}).get('url', t.get('url', 'Unknown'))
                    sources.append(url)
                    context_docs.append(f"Document from {url}:\n{content}")
                
                # Generate RAG answer
                rag_prompt = f"""Based on the following documents, answer this question: "{query}"

Documents:
{chr(10).join(context_docs)}

Provide a comprehensive answer based ONLY on the information in the documents above.
If the documents don't contain relevant information, say so."""

                rag_response = await client.chat.completions.create(
                    model=MODEL,
                    temperature=TEMPERATURE,
                    messages=[{"role": "user", "content": rag_prompt}]
                )
                
                state["answer"] = rag_response.choices[0].message.content
                state["sources"] = sources
                print(f"   💬 Generated RAG answer from {len(relevant_tenders)} documents")
            else:
                state["answer"] = "No relevant documents found for your query."
                state["sources"] = []
                print(f"   ⚠️  No relevant documents found")
            
            context = f"""
            Query: {query}
            
            Relevant Documents Found: {len(relevant_tenders)}
            
            Top Matches:
            {chr(10).join([f"- {t.get('metadata', {}).get('url', 'Unknown')[:60]}... (score: {t.get('score', 0):.3f})" for t in relevant_tenders[:5]])}
            """
        
        # Generate summary using LLM
        prompt = f"""You are a Cognitive Crawler Assistant. Summarize the following results:

{context}

Provide:
1. A brief summary (2-3 sentences)
2. 3-5 key findings as bullet points
3. 2-3 actionable recommendations

Be concise and specific."""
        
        response = await client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.choices[0].message.content
        
        # Parse response (simple split for now)
        lines = result_text.split('\n')
        summary_lines = []
        findings = []
        recommendations = []
        
        current_section = "summary"
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "findings" in line.lower() or "key points" in line.lower():
                current_section = "findings"
                continue
            elif "recommendations" in line.lower():
                current_section = "recommendations"
                continue
            
            if current_section == "summary" and not line.startswith('-') and not line.startswith('•'):
                summary_lines.append(line)
            elif current_section == "findings" and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                findings.append(line.lstrip('-•0123456789. '))
            elif current_section == "recommendations" and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                recommendations.append(line.lstrip('-•0123456789. '))
        
        state["summary"] = ' '.join(summary_lines) if summary_lines else result_text[:200]
        state["key_findings"] = findings if findings else [result_text[:100]]
        state["recommendations"] = recommendations if recommendations else ["Continue monitoring tender portals"]
        
        # Calculate confidence based on results
        if action == "discover":
            confidence = min(1.0, len(state.get("portals_discovered", [])) / 5)
        elif action == "crawl":
            confidence = min(1.0, state.get("tenders_stored", 0) / 100)
        else:
            confidence = min(1.0, len(state.get("relevant_tenders", [])) / 10)
        
        state["confidence"] = confidence
        
        print(f"   ✅ Summary generated")
        print(f"   📈 Confidence: {confidence:.2%}")
        
    except Exception as e:
        error_msg = f"synthesizer error: {str(e)}"
        print(f"   ❌ {error_msg}")
        state["error_log"].append(error_msg)
        state["summary"] = "Error generating summary"
        state["key_findings"] = []
        state["recommendations"] = []
        state["confidence"] = 0.0
    
    return state

