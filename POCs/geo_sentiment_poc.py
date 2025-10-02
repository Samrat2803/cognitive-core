import asyncio
import os
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
# from tavily import TavilyClient  # Replaced with async HTTP calls
import httpx


# ---------------------------
# Configuration (hard-coded)
# ---------------------------
QUERY_TERM = "Hamas"
COUNTRIES = [
    # Test with 3 countries for agent development
    "United States", "Iran", "Israel"
]
RESULTS_PER_COUNTRY = 20
CONCURRENCY_LIMIT = 3
BATCH_SIZE = 8  # LLM analysis chunk size to avoid truncation


@dataclass
class Article:
    country: str
    title: str
    url: str
    content: str
    sentiment: float | None = None
    reasoning: str | None = None
    source_type: str | None = None  # govt, media, political_party, encyclopedia, other
    date_published: str | None = None
    credibility_score: float | None = None
    # Bias analysis
    bias_type: List[str] | None = None
    bias_severity: float | None = None
    bias_notes: str | None = None


def load_keys() -> Tuple[str, str]:
    load_dotenv()
    tavily_key = os.getenv("TAVILY_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    if not tavily_key:
        raise RuntimeError("Missing TAVILY_API_KEY in environment/.env")
    if not openai_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment/.env")
    return tavily_key, openai_key


async def fetch_country_articles_async(tavily_key: str, country: str, term: str, results: int, 
                                      include_domains: List[str] = None, exclude_domains: List[str] = None,
                                      days: int = None, topic: str | None = "news") -> List[Article]:
    """Fully async Tavily search via HTTP API"""
    async with httpx.AsyncClient(timeout=60) as client:
        headers = {"Content-Type": "application/json"}
        
        # Build search payload
        payload = {
            "api_key": tavily_key,
            "query": term,
            "search_depth": "advanced",
            "include_images": False,
            "include_answer": False,
            "max_results": results,
            "country": country
        }
        
        # Add optional parameters for bias mitigation
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        if days:
            payload["days"] = days
        if topic:
            payload["topic"] = topic
            
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            search_data = response.json()
            
            articles: List[Article] = []
            for result in search_data.get("results", []):
                url = result.get("url", "")
                title = result.get("title", "")
                content = result.get("content", "")
                published = result.get("published_date") or result.get("publishedDate")
                print(f"Found for {country}: {title[:50]}... Content length: {len(content)}")
                if url and title:
                    articles.append(Article(country=country, title=title, url=url, content=content, date_published=published))
            return articles
            
        except Exception as e:
            print(f"Error fetching articles for {country}: {e}")
            return []


async def add_metadata_and_sentiment_openai(openai_key: str, articles: List[Article]) -> None:
    if not articles:
        return
    
    # Filter articles with actual content
    valid_articles = [a for a in articles if a.content and len(a.content.strip()) > 50]
    if not valid_articles:
        print(f"No valid articles with content for sentiment scoring")
        return

    async def analyze_chunk(chunk: List[Article]) -> None:
        system = (
            "You are an expert media analyst. For EACH article, provide: "
            "1. SENTIMENT score (-1 to 1): emotional tone toward Hamas (positive/negative/neutral) "
            "2. SOURCE_TYPE: 'media', 'govt', 'political_party', 'encyclopedia', or 'other' "
            "3. CREDIBILITY_SCORE (0-1): source reliability "
            "4. DATE_PUBLISHED: YYYY-MM-DD or 'unknown' "
            "5. BIAS analysis (methodological issues, NOT sentiment): "
            "   - bias_type: array from ['source_bias','selection_bias','framing_bias','language_bias','citation_bias','temporal_bias','geographic_bias'] "
            "   - bias_severity (0-1): how much methodological issues affect reporting quality "
            "   - bias_notes: explain the methodological problems found "
            "Output JSON: {\"results\":[{\"score\":-0.5,\"reasoning\":\"explains sentiment\",\"source_type\":\"media\",\"date_published\":\"2024-01-15\",\"credibility_score\":0.8,\"bias_type\":[\"selection_bias\"],\"bias_severity\":0.3,\"bias_notes\":\"explains methodological issues\"}]}"
        )
        user_chunks = [
            f"Title: {a.title}\nContent:\n{a.content[:1800]}" for a in chunk
        ]
        prompt = "\n\n---\n\n".join(user_chunks)

        async with httpx.AsyncClient(timeout=90) as http:
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "gpt-4o-mini",
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            for attempt in range(2):
                try:
                    resp = await http.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=body
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    text = data["choices"][0]["message"]["content"].strip()
                    obj = json.loads(text)
                    results = obj.get("results", [])
                    if not isinstance(results, list):
                        results = []
                    # Align lengths
                    n = min(len(results), len(chunk))
                    for art, result in zip(chunk[:n], results[:n]):
                        try:
                            score = result.get("score") if isinstance(result, dict) else None
                            reasoning = result.get("reasoning", "") if isinstance(result, dict) else ""
                            source_type = result.get("source_type", "other") if isinstance(result, dict) else "other"
                            date_published = result.get("date_published") if isinstance(result, dict) else None
                            credibility_score = result.get("credibility_score") if isinstance(result, dict) else None
                            bias_type = result.get("bias_type") if isinstance(result, dict) else None
                            bias_severity = result.get("bias_severity") if isinstance(result, dict) else None
                            bias_notes = result.get("bias_notes") if isinstance(result, dict) else None

                            if score is not None:
                                s = float(score)
                                s = max(-1.0, min(1.0, s))
                                art.sentiment = s
                            art.reasoning = reasoning or art.reasoning
                            art.source_type = source_type or art.source_type
                            if date_published and date_published != "unknown":
                                art.date_published = date_published
                            if credibility_score is not None:
                                c = float(credibility_score)
                                art.credibility_score = max(0.0, min(1.0, c))
                            if isinstance(bias_type, list):
                                art.bias_type = [str(x) for x in bias_type]
                            if bias_severity is not None:
                                art.bias_severity = max(0.0, min(1.0, float(bias_severity)))
                            if bias_notes:
                                art.bias_notes = str(bias_notes)
                        except Exception as e:
                            print(f"Result mapping error: {e}")
                    break
                except Exception as e:
                    if attempt == 0:
                        print(f"LLM call failed, retrying: {e}")
                        continue
                    else:
                        print(f"LLM call failed: {e}")

    # Process in batches
    for i in range(0, len(valid_articles), BATCH_SIZE):
        chunk = valid_articles[i:i+BATCH_SIZE]
        await analyze_chunk(chunk)


def trimmed_mean(values: List[float], trim_ratio: float = 0.2) -> float | None:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    vals.sort()
    k = int(len(vals) * trim_ratio)
    core = vals[k: len(vals) - k] if len(vals) - k > k else vals
    if not core:
        return None
    return sum(core) / len(core)


async def main(query_term: str = QUERY_TERM, countries: List[str] = None, 
               include_domains: List[str] = None, exclude_domains: List[str] = None,
               days: int = None, topic: str | None = "news") -> Dict[str, Any]:
    """Main function with configurable parameters for agent use"""
    tavily_key, openai_key = load_keys()
    
    if countries is None:
        countries = COUNTRIES
    
    print(f"🔍 Query sent to Tavily: '{query_term}'")
    print(f"📊 Fetching {RESULTS_PER_COUNTRY} articles per country from {len(countries)} countries")
    print(f"🌍 Countries: {', '.join(countries)}")
    if include_domains:
        print(f"📰 Include domains: {', '.join(include_domains[:3])}{'...' if len(include_domains) > 3 else ''}")
    if exclude_domains:
        print(f"🚫 Exclude domains: {', '.join(exclude_domains[:3])}{'...' if len(exclude_domains) > 3 else ''}")
    if days:
        print(f"📅 Time filter: last {days} days")
    if topic:
        print(f"🧵 Topic: {topic}")
    print(f"🤖 GPT-4o will analyze: sentiment, source type, date, credibility\n")

    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def gather_country(country: str) -> Tuple[str, List[Article]]:
        async with sem:
            arts = await fetch_country_articles_async(
                tavily_key, country, query_term, RESULTS_PER_COUNTRY,
                include_domains, exclude_domains, days, topic
            )
            await add_metadata_and_sentiment_openai(openai_key, arts)
            return country, arts

    results: List[Tuple[str, List[Article]]] = await asyncio.gather(
        *[gather_country(c) for c in countries]
    )

    # Aggregate per-country
    country_rows = []
    for country, articles in results:
        scores = [a.sentiment for a in articles if a.sentiment is not None]
        agg = trimmed_mean(scores)
        country_rows.append({
            "country": country,
            "articles": len(articles),
            "scored": len(scores),
            "sentiment": agg
        })

    # Recent-only aggregation helper
    def is_within_days(date_str: str | None, days_window: int = 30) -> bool:
        if not date_str:
            return False
        try:
            dt = datetime.fromisoformat(date_str)
            return dt >= datetime.utcnow() - timedelta(days=days_window)
        except Exception:
            return False

    # Save outputs
    out_json = {
        "query": query_term,
        "countries": country_rows,
        "countries_recent_30d": [
            {
                "country": country,
                "articles": len(arts),
                "recent_count": sum(1 for a in arts if is_within_days(a.date_published, 30)),
                "recent_sentiment_30d": trimmed_mean([
                    a.sentiment for a in arts if a.sentiment is not None and is_within_days(a.date_published, 30)
                ])
            }
            for (country, arts) in results
        ],
        "articles": [
            {
                "country": a.country,
                "title": a.title,
                "url": a.url,
                "sentiment": a.sentiment,
                "reasoning": a.reasoning,
                "source_type": a.source_type,
                "date_published": a.date_published,
                "credibility_score": a.credibility_score,
                "bias_type": a.bias_type,
                "bias_severity": a.bias_severity,
                "bias_notes": a.bias_notes
            }
            for _, arts in results for a in arts
        ]
    }
    os.makedirs("POCs", exist_ok=True)
    with open("POCs/geo_sentiment_poc_output.json", "w", encoding="utf-8") as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(country_rows)
    df.to_csv("POCs/geo_sentiment_poc_output.csv", index=False)

    # Print concise summary
    print("\nCountry sentiment summary (trimmed mean):")
    for row in sorted(country_rows, key=lambda r: (r["sentiment"] is None, r["sentiment"])):
        print(f"{row['country']}: {row['sentiment'] if row['sentiment'] is not None else 'NA'} (n={row['scored']}/{row['articles']})")
    
    # Print detailed analysis for debugging
    print("\nDetailed analysis with metadata:")
    for country, articles in results:
        print(f"\n{country}:")
        for i, art in enumerate(articles, 1):
            if art.sentiment is not None and art.reasoning:
                print(f"  {i}. {art.title[:60]}...")
                print(f"     Score: {art.sentiment} | Type: {art.source_type} | Credibility: {art.credibility_score}")
                print(f"     Date: {art.date_published or 'Unknown'}")
                print(f"     Reasoning: {art.reasoning}")
            else:
                print(f"  {i}. {art.title[:60]}... [No analysis]")

    return out_json


if __name__ == "__main__":
    asyncio.run(main())


