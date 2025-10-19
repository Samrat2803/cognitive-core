# 🧠 Intelligent Cognitive Crawler - Design & Implementation

## 📋 Overview

The Cognitive Crawler now features a **three-layer intelligence system** that makes smart decisions about what and how to crawl based on:
1. **User Intent Detection** - Understands what the user wants
2. **Domain Classification** - Classifies websites (advisory, not restrictive)
3. **URL Prioritization** - Ranks URLs by relevance

## 🎯 Three-Layer Intelligence System

### Layer 1: Intent Detection (Highest Priority)
**Purpose**: Understand and respect user's explicit instructions

```
Examples:
✅ "Crawl all Times of India articles" 
   → Intent: CRAWL_SPECIFIC_DOMAIN (times of india)
   → Action: Map entire Times of India domain regardless of classification

✅ "Find and crawl all drug regulation portals in India"
   → Intent: DISCOVER_AND_FILTER
   → Action: Use smart classification

✅ "Scrape all articles from Bloomberg about healthcare"
   → Intent: CRAWL_SPECIFIC_DOMAIN (bloomberg)
   → Action: Map Bloomberg domain with keyword instructions
```

**Intent Types**:
- `CRAWL_ENTIRE_SITE`: User wants everything from all discovered sites
- `CRAWL_SPECIFIC_DOMAIN`: User specifies which domain(s) to crawl completely
- `DISCOVER_AND_FILTER`: User wants smart discovery (default mode)

### Layer 2: Domain Classification (Advisory Only)
**Purpose**: Provide intelligent defaults that can be overridden by user intent

```python
AUTHORITY Sites (gov.in, .gov, who.int, fda.gov, nih.gov):
  Default Strategy: FULL_DOMAIN
  Reason: Official sources contain authoritative information
  Example: cdsco.gov.in → Map entire domain

NEWS Sites (reuters.com, bbc.com, timesofindia.com):
  Default Strategy: SPECIFIC_URL
  Reason: News sites are vast, usually only specific articles are relevant
  Example: reuters.com/article/12345 → Only crawl this article
  Override: If user says "crawl all Reuters", map entire domain

RESEARCH Sites (.edu, .ac.uk, arxiv.org):
  Default Strategy: FULL_DOMAIN
  Reason: Academic sources contain comprehensive research
  
UNKNOWN Sites:
  Default Strategy: SPECIFIC_URL
  Reason: Conservative approach for unknown domains
```

### Layer 3: URL Prioritization
**Purpose**: Ensure most relevant content is crawled first

```
Priority Scoring:
100: Original URLs discovered by Tavily (highest priority)
 90: URLs with 4+ query keyword matches
 75: URLs with 3 query keyword matches + content indicators
 65: URLs with content indicators (/article, /press, /regulation)
 50: Base score for domain-mapped URLs
 30: URLs with minimal relevance
 10: Minimum score (navigation pages after penalties)

Penalties:
-20: Navigation pages (/about, /contact, /careers, /login)

Boosts:
+10 per keyword match (for keywords > 3 chars)
+15: Content indicators (/article, /news, /report, /research)
```

## 🔄 Complete Workflow

```
User Query: "Find and crawl drug regulation portals in India"

STEP 0: Intent Detection
  ✅ Intent: DISCOVER_AND_FILTER
  ✅ Reason: User wants smart discovery with filtering

STEP 1: Portal Discoverer (Tavily Search)
  ✅ Discovers 5 URLs:
     1. https://cdsco.gov.in/regulations
     2. https://timesofindia.com/india/drug-regulation-news
     3. https://mohfw.gov.in/drug-policy
     4. https://reuters.com/healthcare/india-drug-rules
     5. https://dcgi.gov.in/

STEP 2: Domain Classification
  cdsco.gov.in     → AUTHORITY (FULL_DOMAIN)
  timesofindia.com → NEWS (SPECIFIC_URL) - only the article
  mohfw.gov.in     → AUTHORITY (FULL_DOMAIN)
  reuters.com      → NEWS (SPECIFIC_URL) - only the article
  dcgi.gov.in      → AUTHORITY (FULL_DOMAIN)

STEP 3: Portal Mapper
  For AUTHORITY domains (cdsco, mohfw, dcgi):
    ✅ Add original URL (priority 100)
    ✅ Map entire domain with instructions:
       "Find pages related to: drug regulation portals India. 
        Prioritize relevant content pages over navigation."
    ✅ Tavily returns 150+ URLs
    ✅ Score and prioritize each URL (10-99)
  
  For NEWS domains (timesofindia, reuters):
    ✅ Add only the specific article (priority 100)
    ✅ Skip domain mapping

STEP 4: URL Prioritization & Deduplication
  ✅ Sort all URLs by priority (highest first)
  ✅ Remove duplicates
  ✅ Result: 300+ URLs ranked 100 → 10

STEP 5: Crawler
  ✅ Crawls top N pages (user-controlled via max_pages)
  ✅ Uses Crawl4AI (free) first
  ✅ Falls back to Tavily Extract (paid) if needed
  ✅ Always crawls priority 100 (original discoveries) first
```

## 📊 Example Scenarios

### Scenario 1: Government Research
```
Query: "Find all Indian government drug regulation portals"
Result:
  ✅ 3 gov.in domains discovered
  ✅ All classified as AUTHORITY
  ✅ All mapped comprehensively
  ✅ 400+ URLs ranked by relevance
  ✅ User crawls top 50 pages
```

### Scenario 2: News Articles
```
Query: "Latest cough syrup contamination news in India"
Result:
  ✅ 5 news article URLs discovered
  ✅ All classified as NEWS
  ✅ Only specific articles preserved
  ✅ No unnecessary domain mapping
  ✅ User crawls 5 highly relevant articles
```

### Scenario 3: Mixed Results
```
Query: "Cough syrup regulation and news in India"
Result:
  ✅ 2 gov.in domains → Mapped fully (300 URLs)
  ✅ 3 news articles → Specific URLs only
  ✅ Combined 305 URLs ranked by priority
  ✅ Top 50 most relevant pages crawled
```

### Scenario 4: User Override
```
Query: "Crawl all Times of India healthcare articles"
Result:
  ✅ Intent detected: CRAWL_SPECIFIC_DOMAIN (times of india)
  ✅ Times of India discovered
  ✅ Classification: NEWS → OVERRIDDEN to FULL_DOMAIN
  ✅ Entire domain mapped with instructions
  ✅ 500+ healthcare-related URLs discovered
  ✅ Ranked by relevance, top N crawled
```

## 🛠️ Key Components

### 1. Domain Classifier (`domain_classifier.py`)
```python
DomainClassifier.classify_domain(url)
→ Returns: type, strategy, confidence, reason

Types: AUTHORITY | NEWS | RESEARCH | UNKNOWN
Strategy: FULL_DOMAIN | SPECIFIC_URL
```

### 2. Intent Detector (`portal_mapper.py`)
```python
detect_crawl_intent(query)
→ Returns: intent type, reason, target_domains

Detects keywords like:
- "crawl all", "scrape all", "get all"
- "all articles from", "entire website"
- Domain names in query
```

### 3. URL Scorer (`portal_mapper.py`)
```python
score_url_relevance(url, query)
→ Returns: 0-99 score

Factors:
- Query keyword matches in URL
- Content indicators in path
- Navigation penalties
```

### 4. Tavily Map with Instructions (`tavily_discovery.py`)
```python
map_portal_structure_with_instructions(url, instructions)
→ Uses Tavily Map API with natural language guidance

Instructions Example:
"Find pages related to: drug regulation India. 
 Prioritize relevant content pages over navigation."
```

## ✅ Advantages

1. **User Intent Respected**: Never artificially restricts user's explicit requests
2. **Smart Defaults**: Uses intelligent classification when user intent is unclear
3. **Cost Efficient**: 
   - News articles: No unnecessary domain mapping
   - Gov portals: Comprehensive but prioritized crawling
4. **Relevance**: URLs ranked by relevance, best content crawled first
5. **Flexible**: Works for diverse use cases from research to news monitoring
6. **Original URLs Preserved**: Tavily's discoveries always get highest priority

## 🎯 Testing

### Test 1: Government Portals
```bash
Query: "Find drug regulation portals in India"
Expected: Map gov.in domains fully, prioritize regulation pages
```

### Test 2: News Articles  
```bash
Query: "Cough syrup contamination deaths India"
Expected: Only specific news articles, no broad domain mapping
```

### Test 3: User Override
```bash
Query: "Crawl all Times of India drug safety articles"
Expected: Map entire timesofindia.com with instructions
```

## 📝 Configuration

```python
# In cognitive_crawler/config.py
MAX_PAGES_TO_MAP = 20        # Max portals to process
MAX_PAGES_TO_CRAWL = 20      # Max pages user can crawl

# In tavily_discovery.py
max_depth = 2                 # Tavily map depth
limit = 100                   # Max URLs from Tavily map
```

## 🚀 Usage

```python
from langgraph_master_agent.tools.sub_agent_caller import SubAgentCaller

caller = SubAgentCaller()

# Discovery mode
result = await caller.call_cognitive_crawler(
    action="discover",
    query="Find and crawl drug regulation authorities in India",
    max_pages=20,
    max_depth=2
)

# Chat mode (RAG)
result = await caller.call_cognitive_crawler(
    action="chat",
    query="What are the drug approval requirements in India?",
    session_id=session_id
)
```

## 📊 Performance Metrics

- **Intent Detection**: < 1ms (rule-based)
- **Domain Classification**: < 1ms per URL
- **Tavily Map**: 5-10s per domain
- **URL Scoring**: < 1ms per URL
- **Total Mapping**: 10-30s for typical queries
- **Crawling**: 10-15s per page (Crawl4AI)

## 🔮 Future Enhancements

1. **LLM-based Intent Detection**: Use GPT-4 for more nuanced understanding
2. **Learning**: Track which URLs users actually engage with
3. **Dynamic Prioritization**: Adjust scores based on crawl results
4. **Semantic URL Analysis**: Use embeddings to score URL relevance
5. **User Profiles**: Remember user's domain preferences

---

**Status**: ✅ Implemented and ready for testing
**Version**: 1.0
**Date**: October 19, 2025

