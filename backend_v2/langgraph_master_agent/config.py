"""
Configuration for Master Agent
"""

import os
from dotenv import load_dotenv

load_dotenv()


class MasterAgentConfig:
    """Configuration settings for master agent"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # LLM Settings (GPT-5 with Enhanced Reasoning)
    MODEL_NAME = "gpt-5"  # Full capability for complex investigative tasks
    TEMPERATURE = 0  # Always 0 as per user rules
    MAX_TOKENS = 4000
    
    # GPT-5 Specific Parameters  
    REASONING_EFFORT = "low"  # Faster responses with basic reasoning
    VERBOSITY = "low"  # Concise responses
    
    # Agent Behavior
    MAX_TOOL_ITERATIONS = 5  # Maximum loops before forcing response (increased for persistence)
    MAX_CONVERSATION_HISTORY = 10  # Keep last N messages
    
    # Tavily Settings (Enhanced Defaults)
    TAVILY_SEARCH_DEPTH = "advanced"  # Use "advanced" for political analysis (3x more content)
    TAVILY_MAX_RESULTS = 15  # Increased from 8 for better coverage
    TAVILY_INCLUDE_ANSWER = True
    TAVILY_DEFAULT_TOPIC = "news"  # Focus on news for political intelligence
    TAVILY_DEFAULT_DAYS = 7  # Default to last 7 days for recent information
    TAVILY_INCLUDE_RAW_CONTENT = False  # Set to True for deep article analysis
    
    # Trusted news sources for domain filtering
    TRUSTED_NEWS_SOURCES = [
        "bbc.com", "reuters.com", "apnews.com",
        "aljazeera.com", "theguardian.com",
        "nytimes.com", "washingtonpost.com",
        "wsj.com", "ft.com", "economist.com"
    ]
    
    # Exclude unreliable/propaganda sources
    EXCLUDED_SOURCES = [
        "rt.com",  # Russian state media
        "presstv.ir",  # Iranian state media
        # Add more as needed
    ]
    
    # LangFuse Observability
    LANGFUSE_HOST = "http://localhost:3761"
    LANGFUSE_ENABLED = True
    
    # Tool/Sub-agent Registry
    AVAILABLE_TOOLS = {
        "tavily_search": {
            "description": """
            Real-time web search for current political information and news.
            
            PURPOSE: Retrieve up-to-date, relevant articles and data from the web. Use when you need current information about political events, policies, or figures.
            
            KEY PARAMETERS:
            - query (required): Search term/question (e.g., "Hamas ceasefire negotiations 2024")
            - search_depth: "basic" (faster, generic snippets) or "advanced" (slower, detailed content with 3x more data per source)
            - max_results: Number of results to return (1-20). Default: 8. Use 15+ for comprehensive analysis.
            - days: Limit results to last N days (e.g., 7 for last week). Essential for "recent" or "latest" queries.
            - topic: "general" (broad) or "news" (mainstream media focus). Use "news" for political analysis.
            - country: Prioritize results from specific country (e.g., "US", "UK", "India"). Use for localized analysis.
            - include_domains: List of trusted domains to focus on (e.g., ["bbc.com", "reuters.com", "apnews.com"])
            - exclude_domains: List of domains to avoid (e.g., ["rt.com"] for state propaganda)
            - include_images: Set true to get image URLs for visual context
            - include_raw_content: Set true to get full article text (10x more content than snippets)
            
            RETURNS: JSON with answer, results array (title, content, url, score, published_date), and images (if requested)
            
            WHEN TO USE:
            - User asks about "latest", "recent", "current", "2024" events
            - Need factual information about political topics
            - Researching specific political figures, policies, or events
            - Gathering sources for sentiment or bias analysis
            
            WHEN TO USE ADVANCED:
            - Queries requiring deep research (use search_depth="advanced")
            - Time-sensitive topics (use days=7 or days=30)
            - Source quality matters (use include_domains with trusted sources)
            - Need to exclude propaganda (use exclude_domains)
            - Want full articles for analysis (use include_raw_content=true)
            
            EXAMPLES:
            - "Latest Hamas ceasefire news" → query="Hamas ceasefire", days=7, topic="news"
            - "US policy on Iran" → query="US Iran policy", country="US", search_depth="advanced"
            - "Trusted sources on Ukraine conflict" → query="Ukraine conflict", include_domains=["bbc.com","reuters.com","apnews.com"]
            
            LIMITATIONS: Rate limit 50 requests/minute. Max 20 results per search.
            """,
            "use_for": ["news", "current events", "factual lookups", "recent updates", "political research", "source gathering"]
        },
        "tavily_extract": {
            "description": """
            Extract full structured content from specific URLs.
            
            PURPOSE: Retrieve complete article text, tables, and embedded content from known URLs. Use when you have URLs and need their full content for deep analysis.
            
            KEY PARAMETERS:
            - urls (required): List of URLs to extract (e.g., ["https://bbc.com/article1", "https://reuters.com/article2"])
            - format: "markdown" (structured, preserves formatting) or "text" (plain text only). Prefer markdown.
            - extract_depth: "basic" (main content only) or "advanced" (includes tables, embedded content, metadata)
            - include_images: Set true to extract all image URLs from the articles
            
            RETURNS: JSON with results array containing raw_content (full article text), images, url, and extraction metadata
            
            WHEN TO USE:
            - You have URLs from tavily_search and need full article text (not just snippets)
            - Performing detailed content analysis (quote extraction, comprehensive reading)
            - Need to analyze article structure, tables, or embedded data
            - Want to extract images from specific articles
            - Comparing full text across multiple sources
            
            WHEN TO USE ADVANCED:
            - Analysis requires tables or data (use extract_depth="advanced")
            - Need images for context (use include_images=true)
            - Want maximum content extraction (use format="markdown" + extract_depth="advanced")
            
            EXAMPLES:
            - After tavily_search: Extract top 5 article URLs for deep analysis
            - "Get full text from this BBC article" → urls=["bbc.com/..."], extract_depth="advanced"
            - "Extract quotes from these 3 sources" → urls=[url1, url2, url3], format="markdown"
            
            BEST PRACTICE: Use after tavily_search to get full content (search gives snippets, extract gives complete articles)
            
            LIMITATIONS: Max 10 URLs per request. Timeout 60 seconds. Some paywalled content may be limited.
            """,
            "use_for": ["article content", "deep reading", "detailed analysis", "quote extraction", "full text retrieval", "content comparison"]
        },
        "tavily_map": {
            "description": """
            Generate comprehensive website sitemaps through intelligent graph traversal (Beta).
            
            PURPOSE: Discover all URLs on a website by traversing it like a graph. Explores hundreds of paths in parallel with intelligent discovery. Use when you need to find ALL pages on a site, not just content.
            
            KEY DIFFERENCE from Crawl:
            - MAP: Discovers URLs (sitemap generation) - returns list of URLs found
            - CRAWL: Extracts content from pages - returns page content
            
            KEY PARAMETERS:
            - url (required): Root URL to map (e.g., "docs.tavily.com", "whitehouse.gov/briefing-room")
            - instructions: Natural language guidance for intelligent discovery (e.g., "Find all policy pages")
            - max_depth: How far from root to explore (default: 1). Higher = more comprehensive.
            - max_breadth: Max links to follow per page (default: 20)
            - limit: Total URLs to discover before stopping (default: 50)
            - select_paths: Regex patterns to include only specific paths (e.g., ["/docs/.*", "/policies/.*"])
            - exclude_paths: Regex patterns to skip paths (e.g., ["/private/.*", "/admin/.*"])
            - allow_external: Include external domain links (default: True)
            
            RETURNS: JSON with base_url, results (array of discovered URLs), response_time
            
            WHEN TO USE:
            - Need complete sitemap of a website (discovery vs extraction)
            - Finding all policy pages on government sites
            - Discovering documentation structure
            - Mapping research repositories
            - Finding hidden/linked content not in search results
            - Building URL inventory before targeted extraction
            
            WHEN TO USE ADVANCED:
            - Comprehensive discovery → max_depth=3, limit=100+
            - Focused discovery → use instructions like "Find all humanitarian reports"
            - Selective mapping → select_paths=["/research/.*", "/publications/.*"]
            - Exclude noise → exclude_paths=["/private/.*", "/admin/.*", "/login/.*"]
            
            EXAMPLES:
            - "Find all UN humanitarian pages" → url="un.org", instructions="Find humanitarian reports", max_depth=2
            - "Map WHO COVID documentation" → url="who.int", select_paths=["/covid/.*"], limit=100
            - "Discover all State Department policy pages" → url="state.gov", select_paths=["/policy/.*"]
            
            BEST PRACTICE: Use MAP to discover URLs, then use EXTRACT to get content from discovered URLs
            
            COST: 1 credit per 10 URLs (2 credits per 10 if using instructions parameter)
            
            BETA FEATURE: API may undergo changes during refinement
            """,
            "use_for": ["sitemap generation", "URL discovery", "website structure mapping", "finding all pages", "comprehensive site exploration", "documentation discovery"]
        },
        "tavily_crawl": {
            "description": """
            Systematically explore and extract content from entire websites.
            
            PURPOSE: Crawl multiple pages of a website starting from a base URL. Use when you need comprehensive coverage of a website section (e.g., policy pages, research repositories, news archives).
            
            KEY PARAMETERS:
            - url (required): Starting URL to begin crawl (e.g., "https://whitehouse.gov/policies/foreign-policy")
            - max_depth: How many link levels to follow (1-3). Default: 2. Use 3 for comprehensive crawls.
            - max_breadth: How many links to follow per page (e.g., 50). Controls crawl width.
            - limit: Maximum total pages to crawl (e.g., 100). Prevents runaway crawls.
            - format: "markdown" (structured) or "text" (plain). Prefer markdown.
            - extract_depth: "basic" or "advanced" (includes tables, metadata)
            - select_paths: Regex patterns to focus crawl (e.g., ["/policies/", "/statements/"])
            - select_domains: Regex patterns for allowed domains (e.g., ["whitehouse.gov"])
            
            RETURNS: JSON with results array containing pages crawled (raw_content, url, depth_level)
            
            WHEN TO USE:
            - Need comprehensive coverage of a topic from one source
            - Analyzing entire policy sections (government websites)
            - Building knowledge bases from think tank research
            - Comparing party platforms (crawl party website policy pages)
            - Historical analysis (crawl news archive sections)
            - Monitoring specific website sections for updates
            
            WHEN TO USE ADVANCED:
            - Government policy analysis → crawl policy section with max_depth=3
            - Think tank research → select_paths=["/research/", "/publications/"]
            - Party platform analysis → crawl policy pages for comprehensive comparison
            - Systematic monitoring → crawl news outlet sections on specific topics
            
            EXAMPLES:
            - "Analyze White House foreign policy" → url="whitehouse.gov/foreign-policy", max_depth=3
            - "Brookings Middle East research" → url="brookings.edu/middle-east/", select_paths=["/research/"]
            - "Democratic party platform on healthcare" → url="democrats.org/healthcare", max_depth=2
            
            BEST PRACTICE: Start with max_depth=2, increase to 3 only if needed. Use select_paths to focus crawl. Always set limit to prevent excessive crawling.
            
            LIMITATIONS: Time-intensive (2-5 minutes for large crawls). Respect robots.txt. Max depth 3. Timeout 120 seconds.
            """,
            "use_for": ["website analysis", "multi-page content", "systematic collection", "policy research", "comprehensive coverage", "knowledge base building"]
        },
        "deep_intelligence_analyzer": {
            "description": """
            Comprehensive multi-layered intelligence analysis combining ALL Tavily features.
            
            PURPOSE: Demonstrate the UNIQUE ADVANTAGE of real-time intelligence by using Search + Extract + Crawl + Geographic Mapping + Timeline Analysis together. This is the most powerful tool for crisis analysis.
            
            WHAT IT DOES (6 Analysis Layers):
            1. Real-Time Discovery (Search API) - Find latest developments across 15+ trusted sources
            2. Deep Content Extraction (Extract API) - Get full article text (10-30x more data than snippets)
            3. Comprehensive Coverage (Crawl API) - Systematic crawling of official sources
            4. Geographic Mapping (MAP feature) - Spatial distribution of events and hotspots
            5. Timeline Analysis - Data freshness analysis showing real-time advantage
            6. Intelligence Synthesis - Multi-source fusion with AI-powered insights
            
            INPUT PARAMETERS:
            - topic (required): Crisis or topic to analyze (e.g., "Israel Gaza conflict humanitarian aid")
            - days: Time window for analysis (default: 7)
            
            OUTPUT (Comprehensive Intelligence Report):
            - Executive Summary (synthesized insights demonstrating real-time value)
            - Key Insights (5-7 findings only possible with real-time data)
            - Geographic Analysis (spatial hotspots, event distribution MAP)
            - Timeline Analysis (data freshness, showing 70%+ sources from last 48 hours vs 0% in static databases)
            - Source Intelligence (credibility scoring, 15+ sources analyzed)
            - Trend Analysis (momentum, escalation patterns)
            - Real-Time Advantage Demonstration (why real-time data matters)
            - Strategic Recommendations (actionable intelligence)
            
            UNIQUE ADVANTAGES DEMONSTRATED:
            1. FRESHNESS: 70%+ sources from last 48 hours (vs 0% in static databases)
            2. DEPTH: 10,000+ characters per source via Extract (vs 300 character snippets)
            3. COMPLETENESS: 15+ sources + crawled pages (vs scattered manual research)
            4. SYNTHESIS: Multi-source intelligence fusion (vs disconnected articles)
            5. GEOGRAPHIC AWARENESS: Spatial mapping of events (MAP feature)
            6. TEMPORAL AWARENESS: Timeline showing data recency
            
            WHEN TO USE:
            - User asks for "comprehensive analysis" or "deep dive"
            - Political crisis analysis requiring real-time intelligence
            - Need to demonstrate why real-time data matters
            - Geographic distribution of events is important
            - Multi-source synthesis and credibility assessment needed
            
            EXAMPLES:
            - "Deep analysis of Israel Gaza conflict" → Uses ALL 6 layers
            - "Comprehensive intelligence on Ukraine negotiations" → Multi-source synthesis with geographic mapping
            - "Crisis analysis with real-time data" → Demonstrates freshness advantage
            
            EXECUTION TIME: 30-60 seconds (worth it for comprehensive intelligence)
            
            BEST PRACTICE: Use this when user needs true intelligence analysis, not just search results. This tool demonstrates the FULL POWER of Tavily.
            """,
            "use_for": ["comprehensive analysis", "crisis intelligence", "deep dive", "multi-source synthesis", "geographic mapping", "real-time advantage demonstration", "intelligence fusion"]
        },
        "sentiment_analysis_agent": {
            "description": """
            Comprehensive geopolitical sentiment analysis across multiple countries.
            Features:
            - Multi-country sentiment scoring (-1 to +1)
            - Bias detection (7 types: selection, framing, language, source, citation, temporal, geographic)
            - Source credibility assessment
            - Multi-iteration refinement with bias correction
            - Detailed reasoning and citations
            
            Use for:
            - "Analyze sentiment on [topic]"
            - "How does [country] view [issue]"
            - "Compare international perspectives on [topic]"
            - "Give me unbiased analysis of [political event]"
            """,
            "use_for": ["sentiment analysis", "bias detection", "multi-country analysis", "credibility assessment"]
        },
        "deep_investigative_reporter": {
            "description": """
            Deep investigative journalism agent that conducts persistent, recursive investigation.
            
            PURPOSE: Act as an investigative journalist who doesn't stop at the first answer. Follows every entity, traces funding, identifies hidden connections, and maps entire networks until root causes are uncovered.
            
            WHAT IT DOES (Strategic Intelligence Loop):
            1. Parse investigation goal ("why did X happen?", "who funds Y?", "what's behind Z?")
            2. Map timeline and find first articles (establish cutoff date)
            3. Extract entities (people, organizations, events)
            4. RECURSIVE INVESTIGATION LOOP:
               - Strategic Intelligence Analyzer (THE BRAIN):
                 * Analyzes current knowledge
                 * Detects suspicious patterns (rapid mobilization, questionable backers, contradictions)
                 * Identifies knowledge gaps
                 * Generates new investigative questions
                 * Forms hypotheses to test
                 * Prioritizes investigation targets
               - Entity Investigator:
                 * Tries 8 different investigation strategies per entity
                 * Direct search, quotes, associations, controversies, public records, etc.
                 * Doesn't give up if one method fails - tries alternatives
                 * Extracts facts and new entities recursively
               - Funding Tracer (FOLLOW THE MONEY):
                 * Investigates funding sources for organizations
                 * Identifies suspicious backers (arms dealers, corruption charges)
                 * Maps funding networks
                 * Detects shared funders (possible coordination)
               - Loop back to Strategic Analyzer (continuous reassessment)
            5. Generate visual artifacts (causal diagram + network graph)
            
            KEY FEATURES (What Makes It "Persistent"):
            - Multi-strategy investigation: 8 methods per entity (quotes, associations, funding, controversies, etc.)
            - Recursive exploration: Every entity mentioned gets investigated
            - Pattern detection: Identifies suspicious connections (shared funding, rapid mobilization, contradictions)
            - Question generation: Continuously asks "what don't we know?" and "what's suspicious?"
            - Hypothesis formation: Tests theories (organic movement vs foreign orchestration vs hybrid)
            - Funding tracing: Always "follows the money"
            - Alternative fallbacks: When blocked, tries different approaches
            
            OUTPUT ARTIFACTS:
            1. Spider Web Network Graph (Interactive visualization):
               - Nodes: Entities (people, orgs, funders) sized by importance
               - Edges: Connections (relationships, funding flows)
               - Colors: Red for suspicious entities, orange for funders
               - JSON format for D3.js visualization
            
            2. Causal Diagram (Mermaid flowchart):
               - Root causes → Intermediate causes → Triggers → Final events
               - Evidence-based confidence scores
               - Visual flow showing "why" chains
            
            3. HTML Report (Standalone file):
               - Both visualizations embedded
               - Interactive network graph (drag nodes)
               - Investigation summary with findings
            
            4. Investigation Summary (JSON):
               - Key entities identified
               - Funding network mapped
               - Suspicious patterns found
               - Top hypotheses with confidence scores
               - Unanswered questions
            
            INPUT PARAMETERS:
            - query (required): Investigation question (e.g., "Why did Nepal revolution happen?", "Who funds Hami Nepal?")
            - cutoff_date (optional): Only use information before this date (for real-time analysis)
            - max_depth (optional): Maximum investigation depth (default: 5, range: 3-8)
            
            WHEN TO USE:
            - User asks "why did X happen?" (causal analysis)
            - User asks "who funds Y?" or "where does money come from?" (funding investigation)
            - User wants to understand "actors behind" or "network of" (network mapping)
            - User wants "investigative analysis" or "deep dive into connections"
            - Need to trace ownership, funding, or influence networks
            - Event happened recently and need to understand causes before mainstream analysis
            
            USE CASES:
            - "Why did Nepal revolution happen?" → Traces: corruption scandals → nepo kids → social media ban → protests → funding sources
            - "Who funds protests in Country X?" → Maps: Organizations → Backers → Foreign funding → Training programs → Network
            - "What's behind Organization Y?" → Investigates: Leadership → Business interests → Corruption → Connections → Motivations
            
            EXAMPLE FINDINGS (Nepal Revolution):
            - Discovered: Hami Nepal funded by arms dealer with corruption charges
            - Traced: NED $20K grant for "digital security training" months before protests
            - Identified: Shared funding pattern (Coca-Cola, Viber support = corporate interests)
            - Mapped: Network of 30+ entities with 50+ connections
            - Hypothesis: Hybrid (genuine anger + professional mobilization infrastructure)
            
            INVESTIGATION STRATEGY:
            - Starts broad → narrows based on patterns
            - Tries 8 strategies before giving up on entity
            - Cross-verifies claims across sources
            - Builds confidence scores (stops at 85% confidence or max depth)
            - Generates 10+ investigative questions per iteration
            - Recursive depth 5 = ~100+ entities investigated
            
            EXECUTION TIME: 2-5 minutes (depends on max_depth)
            - Depth 3: ~1-2 minutes, ~30 entities
            - Depth 5: ~3-4 minutes, ~80 entities
            - Depth 8: ~5-8 minutes, ~150+ entities
            
            BEST PRACTICE:
            - Use depth 3-5 for most investigations
            - Set cutoff_date when analyzing "as it happened" (before retrospective analysis)
            - Perfect for "follow the money" investigations
            - Use when you need visual network graphs or causal diagrams
            
            OUTPUT FORMAT:
            Returns dict with:
            - artifacts: List of 4 artifacts (network graph, causal diagram, HTML, summary)
            - Each artifact has: type, title, format, data, description
            """,
            "use_for": ["causal analysis", "why questions", "funding investigation", "network mapping", "investigative journalism", "follow the money", "actor analysis", "hidden connections", "ownership tracing"]
        },
        "media_bias_detector_agent": {
            "description": """
            Multi-source media bias analysis comparing how different news outlets cover the same topic.
            Features:
            - Political lean classification (-1.0 far left to +1.0 far right)
            - Loaded language detection (8 categories: emotionally_charged, sensationalist, fear_based, etc.)
            - Framing analysis (conflict, human interest, economic, morality, responsibility, etc.)
            - Bias technique identification (spin, selective quoting, labeling, omission, etc.)
            - Comparison matrix across sources
            - Consensus vs divergence analysis
            - Interactive visualizations (bias spectrum, heatmap, framing chart)
            
            Use for:
            - "Compare media bias on [topic]"
            - "How do different news sources cover [event]"
            - "Analyze CNN vs Fox News coverage of [issue]"
            - "Show me bias spectrum for [topic]"
            - "What's the media framing of [event]"
            - "Detect loaded language in [topic] reporting"
            """,
            "use_for": ["media bias", "source comparison", "framing analysis", "loaded language", "political lean", "news coverage"]
        },
        "investigative_journalist": {
            "description": """
            Deep investigative journalist agent for evidence-based reporting with hypothesis-driven research.
            
            PURPOSE: Conduct multi-iteration investigative research similar to professional journalism. 
            Gathers evidence, discovers entities, maps connections, identifies anomalies, and produces 
            publication-ready articles with full source attribution.
            
            WHAT IT DOES (Investigative Loop):
            1. STRATEGIST - Generates hypotheses and decides next action (search vs extract vs analyze)
            2. SEARCHER - Finds relevant articles using Tavily search
            3. EXTRACTOR - Gets full article content (free methods first, Tavily fallback)
            4. ANALYZER - Extracts entities, facts, connections, anomalies, insights
            5. SYNTHESIZER - Produces publication-ready investigative article
            6. Loop continues until max iterations or investigation complete
            
            KEY FEATURES:
            - Evidence-based: Every claim cited with source URLs
            - Cost-optimized: 91% cheaper than baseline (uses free extraction methods)
            - MongoDB persistence: Resume investigations, share evidence repository
            - Hypothesis-driven: Tests theories, identifies suspicious patterns
            - Entity tracking: People, organizations, locations extracted automatically
            - Network mapping: Connections between entities identified
            
            INPUT PARAMETERS:
            - query (required): Investigation topic (e.g., "India cough syrup deaths")
            - max_iterations (optional): Number of research cycles (3-100, default: 20)
            - resume_from (optional): Investigation ID to continue previous investigation
            
            OUTPUT (Two Artifacts):
            1. Publication-Ready Article:
               - Headline
               - Executive Summary
               - Key Findings (5-7 points)
               - Analysis & Insights (novel insights, alternative hypotheses, network of actors)
               - Suspicious Patterns & Anomalies
               - Timeline Analysis
               - Unanswered Questions
               - Full Source Citations
            
            2. Evidence Repository (MongoDB):
               - All entities discovered (people, orgs, locations, companies)
               - All facts collected with confidence scores
               - All connections mapped between entities
               - All anomalies identified
               - Full extracted articles cached
               - Resumable for continued investigation
            
            WHEN TO USE:
            - User asks to "investigate" or "deep dive into" a topic
            - Need comprehensive, evidence-based analysis
            - Want publication-ready article with full citations
            - Investigating scandals, controversies, policy failures
            - Need to identify suspicious patterns or anomalies
            - Want to resume investigation later
            
            USE CASES:
            - "Investigate India cough syrup deaths" → Comprehensive report on contamination crisis
            - "Deep dive into regulatory failures in pharmaceutical industry" → Multi-source analysis
            - "Investigate the actors behind X event" → Entity mapping and connection analysis
            
            COST (Cost-Optimized):
            - 3 iterations: ~$0.06 (5 entities, 3-5 facts)
            - 10 iterations: ~$0.18 (20 entities, 15-20 facts)
            - 20 iterations: ~$0.36 (40 entities, 30-40 facts)
            - Uses free extraction (Jina AI, Trafilatura, BeautifulSoup) = 91% savings
            
            EXECUTION TIME:
            - 3 iterations: ~45 seconds
            - 10 iterations: ~2-3 minutes
            - 20 iterations: ~5-6 minutes
            
            BEST PRACTICE:
            - Start with 3 iterations for initial understanding
            - Continue with 10-20 more iterations for deep dive
            - Use resume_from to continue investigation across sessions
            - Perfect for stories that need detailed evidence and source attribution
            
            SAVES TO MONGODB:
            - Collection: `investigations`
            - Fields: investigation_id, query, entities, facts, connections, status, cost
            - Resumable: Pass investigation_id to continue
            """,
            "use_for": ["investigations", "deep dive", "evidence gathering", "scandal analysis", "regulatory failures", "comprehensive reporting", "source attribution", "entity discovery"]
        },
        "government_intelligence": {
            "description": """
            Government information discovery and analysis agent specializing in official sources.
            
            PURPOSE: Discover, crawl, and analyze government websites, regulatory actions, official statements,
            and policy documents. Provides RAG-based answers using crawled government content.
            
            WHAT IT DOES (3 Workflows):
            1. DISCOVER: Find relevant government/news portals using Tavily search
            2. CRAWL: Extract content from discovered URLs (Crawl4AI + Tavily fallback)
            3. QUERY: RAG search on stored documents with vector similarity
            
            KEY FEATURES:
            - Government-focused: Specializes in .gov domains, regulatory bodies, official statements
            - Free crawling: Uses Crawl4AI (free) with Tavily Extract fallback
            - Vector storage: All crawled content stored as embeddings for RAG
            - RAG queries: Ask questions about crawled content with vector search
            - MongoDB persistence: Session-based document storage
            
            INPUT PARAMETERS:
            - query (required): Natural language query about government info
            - action (required): "discover", "crawl", or "query"
            - sources (optional): List of domains to focus on
            - listing_pages (optional): For "crawl" action, URLs to crawl
            - thread_id (optional): Session ID for MongoDB filtering
            
            OUTPUT (Depends on action):
            1. Discover action:
               - portals_discovered: List of government/news portals (5-10)
               - listing_pages: URLs identified for crawling (20-100)
            
            2. Crawl action:
               - documents_stored: Number of documents extracted and stored
               - embeddings_generated: Number of vectors created
            
            3. Query action:
               - relevant_documents: Top 3 matching documents with similarity scores
               - summary: LLM-generated answer based on documents
               - key_findings: Bullet points extracted from documents
               - recommendations: Suggested actions based on content
               - confidence: 0-1 confidence score
            
            WHEN TO USE:
            - User asks about "government response" or "official statement"
            - Need to analyze regulatory actions or policy documents
            - Investigating government websites or agency reports
            - Want to ask questions about official government content
            - Need verified information from .gov sources
            
            USE CASES:
            - "What is the government response to X?" → discover → crawl → query workflow
            - "Analyze FDA regulatory actions on Y" → discover FDA pages → crawl → RAG query
            - "What did officials say about Z?" → find official statements → extract → answer
            
            COST:
            - Discover: ~$0.01 (1 Tavily search)
            - Crawl: ~$0.00-0.10 (free Crawl4AI, fallback to Tavily if needed)
            - Query: ~$0.00 (vector search in MongoDB, no API calls)
            - Total workflow: ~$0.02-0.15
            
            EXECUTION TIME:
            - Discover: ~15 seconds
            - Crawl: ~45 seconds (20 pages)
            - Query: ~2 seconds
            - Full workflow: ~60-90 seconds
            
            BEST PRACTICE:
            - Run discover first to find sources
            - Then crawl top 20 URLs
            - Finally use query action for specific questions
            - Store results by thread_id for session-based RAG
            
            SAVES TO MONGODB:
            - Collection: `tender_vectors` (reused collection name)
            - Fields: url, content, embedding, metadata, thread_id
            - Vector search enabled via MongoDB Atlas
            """,
            "use_for": ["government information", "official statements", "regulatory analysis", "policy documents", ".gov sources", "government response", "official reports"]
        }
    }
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY not found in environment")
        
        return True


# Validate on import
MasterAgentConfig.validate_config()

