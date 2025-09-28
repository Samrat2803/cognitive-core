## Tavily Web API Features (POC Reference)

This document summarizes Tavily's Web APIs relevant for political intelligence gathering POCs.

### Search API
- **Real-time Web Search**: Live retrieval of current information from the web.
- **Search Depth**: `basic` and `advanced` modes to control breadth/depth.
- **Auto-Parameters (Beta)**: Automatically tunes search settings based on query intent.
- **Country Parameter**: Prioritizes results for a specified country.
- **Domain Targeting**: Focus searches on specific domains or exclude domains.
- **Include Media**: Optionally include images and favicons in results.

### Extract API
- **Content Extraction**: Fetches raw page content for given URLs.
- **Extraction Depth**: `basic` and `advanced` extraction options.
- **Output Formats**: `markdown` or `text` content outputs.
- **Image/Favicon Inclusion**: Optionally include page images and favicon metadata.
- **Batch Extraction**: Extract multiple URLs in a single request.

### Crawl API
- **Website Crawling**: Follows internal links to collect site-wide content.
- **Configurable Depth/Breadth**: Control crawl scope and limits.
- **Integrated Extraction**: Apply extract options during the crawl.
- **Filtering/Scoping**: Restrict by path prefixes, file types, or robots-aware settings.

### Common Capabilities
- **Rate/Usage Monitoring**: Manage credits via the Tavily usage dashboard.
- **SDKs**: Official Python and JavaScript SDKs for quick integration.
- **Security**: API key authentication; use environment variables for secrets.

### Quickstart (Python SDK)
```python
from tavily import TavilyClient
import os

api_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key)

# Real-time search
search = tavily.search("Latest political news", search_depth="advanced")

# Extract content
extract = tavily.extract(urls=["https://example.com"], format="markdown")

# Crawl a site
crawl = tavily.crawl(url="https://example.com", max_depth=2)
```

Notes:
- Store secrets in `.env` (e.g., `TAVILY_API_KEY`), load via dotenv in app runtime.
- Prefer async wrappers for throughput when building production collectors.

