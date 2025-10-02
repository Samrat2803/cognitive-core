# Political Intelligence Gathering POCs

This directory contains proof-of-concept implementations for the Political Intelligence & Narrative Management Platform.

## Completed POCs

### 1. Geographical Sentiment Analyzer (`geo_sentiment_poc.py`)

**Purpose**: Live geographical sentiment analysis for political terms across geopolitically important countries.

**Features**:
- Real-time news/opinion gathering via Tavily Search API with country targeting
- GPT-4o-mini sentiment scoring (temperature=0) with scores in [-1, 1] range
- Async processing with concurrency limits for rate management
- Trimmed mean aggregation to reduce outlier impact
- Output in both JSON and CSV formats

**Test Results** (for "Hamas"):
- Successfully analyzed sentiment across 29 countries (full geopolitical coverage)
- Sentiment scores ranged from -0.43 (UK, Canada, India, Nigeria) to ~0.0 (Germany, France, Japan, etc.)
- All countries returned valid results with 3 articles each
- Processing completed without API errors
- **NEW**: GPT-4o reasoning provided for each sentiment score for debugging and transparency

**Key Components**:
- **Intelligence Gathering**: Tavily country-specific search with advanced depth
- **Sentiment Analysis**: GPT-4o-mini with structured JSON output and reasoning
- **Data Aggregation**: Trimmed mean calculation for robust country-level scores
- **Output Generation**: JSON (detailed with reasoning) and CSV (summary) formats
- **Debug Support**: Detailed reasoning for each sentiment score for transparency

**Configuration**:
- Hard-coded inputs (no arg parsing per user rules)
- Secrets loaded from `.env` file only
- Async implementation for performance
- Temperature=0 for consistent LLM outputs

**Files Generated**:
- `geo_sentiment_poc_output.json` - Detailed results with all articles
- `geo_sentiment_poc_output.csv` - Country-level summary

## Usage

```bash
# Ensure API keys are in .env file:
# TAVILY_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here

# Run the geographical sentiment analyzer
python POCs/geo_sentiment_poc.py
```

## Next Steps

Potential expansions for the political intelligence platform:
1. **Crisis Detection**: Real-time monitoring with alert thresholds
2. **Trend Analysis**: Historical sentiment tracking over time
3. **Influence Mapping**: Network analysis of key opinion leaders
4. **Multi-language Support**: Sentiment analysis in native languages
5. **Predictive Modeling**: Sentiment forecasting based on trends

## Technical Architecture

- **Tavily API**: Real-time web intelligence and country-specific search
- **OpenAI GPT-4o-mini**: Sentiment classification with temperature=0
- **Async Processing**: Concurrent API calls with semaphore-based rate limiting
- **Robust Aggregation**: Trimmed mean to handle outliers and edge cases
