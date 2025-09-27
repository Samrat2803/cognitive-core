#!/usr/bin/env python3
"""
Tavily Security Query Temporal Volatility Analyzer
Analyzes how quickly Tavily search results change for security-related queries
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import statistics
from collections import defaultdict
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TavilyVolatilityAnalyzer:
    """Analyzes temporal volatility of Tavily search results"""
    
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.base_url = "https://api.tavily.com/search"
        self.results_dir = "volatility_results"
        self.ensure_results_dir()
        
        # Security queries to test
        self.security_queries = [
            "AI generated code security vulnerability",
            "ChatGPT code generation security issue", 
            "Lovable Bolt.new security vulnerability",
            "AI coding assistant security flaw",
            "automated code generation security risk",
            "LLM generated code vulnerability",
            "AI assistant code security problem",
            "machine learning code generation security",
            "AI tool security vulnerability",
            "generated code security best practices"
        ]
        
        # Results storage
        self.daily_results = {}
        self.volatility_metrics = {}
    
    def ensure_results_dir(self):
        """Create results directory if it doesn't exist"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def search_tavily(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """Perform a Tavily search"""
        try:
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
                "include_answer": False,
                "include_raw_content": False
            }
            
            response = requests.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Error searching Tavily: {e}")
            return {"results": [], "error": str(e)}
    
    def collect_daily_data(self, days: int = 30) -> Dict[str, Any]:
        """Collect data for specified number of days"""
        print(f"🔍 Starting data collection for {days} days...")
        print(f"📊 Testing {len(self.security_queries)} security queries")
        
        all_results = {}
        
        for day in range(1, days + 1):
            print(f"\n📅 Day {day}/{days}")
            day_results = {}
            
            for i, query in enumerate(self.security_queries):
                print(f"  🔍 Query {i+1}/{len(self.security_queries)}: {query[:50]}...")
                
                # Perform search
                search_results = self.search_tavily(query)
                
                # Extract key information
                results = search_results.get("results", [])
                processed_results = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "day": day,
                    "result_count": len(results),
                    "results": results,
                    "top_urls": [r.get("url", "") for r in results[:10]],
                    "top_titles": [r.get("title", "") for r in results[:10]],
                    "top_content": [r.get("content", "")[:200] for r in results[:10]]
                }
                
                day_results[query] = processed_results
                
                # Small delay to avoid rate limiting
                time.sleep(1)
            
            all_results[f"day_{day}"] = day_results
            
            # Save intermediate results
            self.save_results(all_results, f"day_{day}_results.json")
            
            print(f"✅ Day {day} completed")
        
        return all_results
    
    def save_results(self, data: Dict[str, Any], filename: str):
        """Save results to JSON file"""
        filepath = os.path.join(self.results_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Results saved to {filepath}")
    
    def load_results(self, filename: str) -> Dict[str, Any]:
        """Load results from JSON file"""
        filepath = os.path.join(self.results_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def calculate_stability_metrics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate stability metrics for each query"""
        print("\n📊 Calculating stability metrics...")
        
        stability_metrics = {}
        
        for query in self.security_queries:
            print(f"  🔍 Analyzing: {query[:50]}...")
            
            # Collect daily results for this query
            daily_urls = []
            daily_counts = []
            daily_titles = []
            
            for day_key, day_data in all_results.items():
                if query in day_data:
                    query_data = day_data[query]
                    daily_urls.append(set(query_data["top_urls"]))
                    daily_counts.append(query_data["result_count"])
                    daily_titles.append(query_data["top_titles"])
            
            # Calculate stability metrics
            metrics = self.calculate_query_stability(daily_urls, daily_counts, daily_titles)
            stability_metrics[query] = metrics
        
        return stability_metrics
    
    def calculate_query_stability(self, daily_urls: List[set], daily_counts: List[int], daily_titles: List[List[str]]) -> Dict[str, Any]:
        """Calculate stability metrics for a single query"""
        
        # 1. URL Stability (Jaccard similarity)
        url_similarities = []
        for i in range(1, len(daily_urls)):
            if daily_urls[i-1] and daily_urls[i]:
                intersection = len(daily_urls[i-1] & daily_urls[i])
                union = len(daily_urls[i-1] | daily_urls[i])
                jaccard = intersection / union if union > 0 else 0
                url_similarities.append(jaccard)
        
        # 2. Result Count Stability
        count_variance = statistics.variance(daily_counts) if len(daily_counts) > 1 else 0
        count_mean = statistics.mean(daily_counts) if daily_counts else 0
        
        # 3. Title Stability (content change detection)
        title_changes = 0
        for i in range(1, len(daily_titles)):
            if daily_titles[i-1] != daily_titles[i]:
                title_changes += 1
        
        # 4. Overall Stability Score
        avg_url_similarity = statistics.mean(url_similarities) if url_similarities else 0
        title_change_rate = title_changes / (len(daily_titles) - 1) if len(daily_titles) > 1 else 0
        
        # Stability score (0-1, higher = more stable)
        stability_score = (avg_url_similarity + (1 - title_change_rate)) / 2
        
        return {
            "avg_url_similarity": avg_url_similarity,
            "url_similarity_variance": statistics.variance(url_similarities) if len(url_similarities) > 1 else 0,
            "result_count_mean": count_mean,
            "result_count_variance": count_variance,
            "title_change_rate": title_change_rate,
            "overall_stability_score": stability_score,
            "volatility_level": self.classify_volatility(stability_score)
        }
    
    def classify_volatility(self, stability_score: float) -> str:
        """Classify volatility level based on stability score"""
        if stability_score >= 0.8:
            return "LOW"
        elif stability_score >= 0.5:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def analyze_temporal_patterns(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal patterns in the data"""
        print("\n📈 Analyzing temporal patterns...")
        
        patterns = {
            "weekly_trends": {},
            "query_performance": {},
            "change_frequency": {}
        }
        
        # Analyze weekly trends
        for query in self.security_queries:
            weekly_changes = defaultdict(int)
            
            for day_key, day_data in all_results.items():
                if query in day_data:
                    day_num = int(day_key.split("_")[1])
                    week = (day_num - 1) // 7 + 1
                    
                    # Count changes (simplified)
                    if day_num > 1:
                        prev_day_key = f"day_{day_num - 1}"
                        if prev_day_key in all_results and query in all_results[prev_day_key]:
                            prev_urls = set(all_results[prev_day_key][query]["top_urls"])
                            curr_urls = set(day_data[query]["top_urls"])
                            
                            if prev_urls != curr_urls:
                                weekly_changes[week] += 1
            
            patterns["weekly_trends"][query] = dict(weekly_changes)
        
        return patterns
    
    def generate_report(self, stability_metrics: Dict[str, Any], temporal_patterns: Dict[str, Any]) -> str:
        """Generate a comprehensive analysis report"""
        print("\n📋 Generating analysis report...")
        
        report = []
        report.append("# Tavily Security Query Temporal Volatility Analysis Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Queries analyzed: {len(self.security_queries)}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        
        volatility_counts = defaultdict(int)
        for query, metrics in stability_metrics.items():
            volatility_counts[metrics["volatility_level"]] += 1
        
        report.append(f"- **High Volatility Queries**: {volatility_counts['HIGH']}")
        report.append(f"- **Medium Volatility Queries**: {volatility_counts['MEDIUM']}")
        report.append(f"- **Low Volatility Queries**: {volatility_counts['LOW']}")
        report.append("")
        
        # Detailed Analysis
        report.append("## Detailed Query Analysis")
        
        for query, metrics in stability_metrics.items():
            report.append(f"### {query}")
            report.append(f"- **Volatility Level**: {metrics['volatility_level']}")
            report.append(f"- **Overall Stability Score**: {metrics['overall_stability_score']:.3f}")
            report.append(f"- **URL Similarity**: {metrics['avg_url_similarity']:.3f}")
            report.append(f"- **Title Change Rate**: {metrics['title_change_rate']:.3f}")
            report.append(f"- **Result Count Variance**: {metrics['result_count_variance']:.3f}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        
        high_volatility_queries = [q for q, m in stability_metrics.items() if m["volatility_level"] == "HIGH"]
        medium_volatility_queries = [q for q, m in stability_metrics.items() if m["volatility_level"] == "MEDIUM"]
        low_volatility_queries = [q for q, m in stability_metrics.items() if m["volatility_level"] == "LOW"]
        
        if high_volatility_queries:
            report.append("### High Volatility Queries (Real-time monitoring recommended)")
            for query in high_volatility_queries:
                report.append(f"- {query}")
            report.append("")
        
        if medium_volatility_queries:
            report.append("### Medium Volatility Queries (Daily monitoring recommended)")
            for query in medium_volatility_queries:
                report.append(f"- {query}")
            report.append("")
        
        if low_volatility_queries:
            report.append("### Low Volatility Queries (Weekly monitoring sufficient)")
            for query in low_volatility_queries:
                report.append(f"- {query}")
            report.append("")
        
        return "\n".join(report)
    
    def run_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Run the complete volatility analysis"""
        print("🚀 Starting Tavily Volatility Analysis")
        print("=" * 50)
        
        # Step 1: Collect data
        all_results = self.collect_daily_data(days)
        
        # Step 2: Calculate stability metrics
        stability_metrics = self.calculate_stability_metrics(all_results)
        
        # Step 3: Analyze temporal patterns
        temporal_patterns = self.analyze_temporal_patterns(all_results)
        
        # Step 4: Generate report
        report = self.generate_report(stability_metrics, temporal_patterns)
        
        # Step 5: Save results
        final_results = {
            "analysis_date": datetime.now().isoformat(),
            "days_analyzed": days,
            "queries_analyzed": len(self.security_queries),
            "stability_metrics": stability_metrics,
            "temporal_patterns": temporal_patterns,
            "report": report
        }
        
        self.save_results(final_results, "volatility_analysis_results.json")
        
        # Save report as markdown
        report_path = os.path.join(self.results_dir, "volatility_analysis_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n✅ Analysis completed!")
        print(f"📊 Results saved to: {self.results_dir}/volatility_analysis_results.json")
        print(f"📋 Report saved to: {report_path}")
        
        return final_results

def main():
    """Main function to run the analysis"""
    try:
        analyzer = TavilyVolatilityAnalyzer()
        
        # Run analysis for 7 days (can be increased)
        results = analyzer.run_analysis(days=7)
        
        # Print summary
        print("\n" + "="*50)
        print("📊 ANALYSIS SUMMARY")
        print("="*50)
        
        volatility_counts = defaultdict(int)
        for query, metrics in results["stability_metrics"].items():
            volatility_counts[metrics["volatility_level"]] += 1
        
        print(f"High Volatility Queries: {volatility_counts['HIGH']}")
        print(f"Medium Volatility Queries: {volatility_counts['MEDIUM']}")
        print(f"Low Volatility Queries: {volatility_counts['LOW']}")
        
        # Print top 3 most volatile queries
        sorted_queries = sorted(
            results["stability_metrics"].items(),
            key=lambda x: x[1]["overall_stability_score"]
        )
        
        print("\n🔴 Most Volatile Queries:")
        for query, metrics in sorted_queries[:3]:
            print(f"  - {query[:60]}... (Stability: {metrics['overall_stability_score']:.3f})")
        
        print("\n🟢 Most Stable Queries:")
        for query, metrics in sorted_queries[-3:]:
            print(f"  - {query[:60]}... (Stability: {metrics['overall_stability_score']:.3f})")
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
