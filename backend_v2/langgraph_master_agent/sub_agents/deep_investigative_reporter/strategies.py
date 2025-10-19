"""
Investigation strategies for the Deep Investigative Reporter.

8 different methods to investigate entities, each optimized for different scenarios.
"""

from typing import Dict, List, Optional, Any
from shared.tavily_client import TavilyClient
import os


class InvestigationStrategies:
    """
    Multi-method investigation strategies.
    
    When one method is blocked or fails, try another approach.
    """
    
    def __init__(self):
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    async def direct_search(self, entity: str, context: str = "") -> Dict[str, Any]:
        """
        Strategy 1: Direct search
        
        Basic search: "{entity} {context}"
        Use for: Initial discovery
        """
        query = f"{entity} {context}".strip()
        
        result = await self.tavily.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            include_raw_content=True
        )
        
        return result
    
    async def quotes_search(self, entity: str, keywords: List[str]) -> Dict[str, Any]:
        """
        Strategy 2: Quotes search
        
        Find entity being quoted or interviewed in news
        Use for: Getting person's views, statements, ideology
        """
        query = f'"{entity}" ' + " ".join(keywords)
        
        result = await self.tavily.search(
            query=query,
            search_depth="advanced",
            max_results=8,
            topic="news"
        )
        
        return result
    
    async def association_search(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """
        Strategy 3: Association search
        
        Find entity's business/organizational associations
        Use for: Mapping networks
        """
        if entity_type == "person":
            query = f"{entity} company board director CEO chairman member position"
        elif entity_type == "organization":
            query = f"{entity} ownership founders leadership management board"
        else:
            query = f"{entity} associated with connected to"
        
        result = await self.tavily.search(
            query=query,
            search_depth="advanced",
            max_results=10
        )
        
        return result
    
    async def funding_search(self, entity: str) -> Dict[str, Any]:
        """
        Strategy 4: Funding search
        
        Investigate funding sources (FOLLOW THE MONEY)
        Use for: Organizations, NGOs, movements
        """
        result = await self.tavily.search(
            query=f"{entity} funding donors sponsors grants revenue budget financial support",
            search_depth="advanced",
            max_results=15,
            include_raw_content=True
        )
        
        return result
    
    async def controversy_search(self, entity: str) -> Dict[str, Any]:
        """
        Strategy 5: Controversy search
        
        Find scandals, criticisms, allegations
        Use for: Detecting red flags
        """
        result = await self.tavily.search(
            query=f"{entity} scandal controversy criticism allegations corruption charges",
            search_depth="advanced",
            max_results=10
        )
        
        return result
    
    async def network_search(self, entity_a: str, entity_b: str) -> Dict[str, Any]:
        """
        Strategy 6: Network search
        
        Investigate relationship between two entities
        Use for: Verifying connections
        """
        result = await self.tavily.search(
            query=f"{entity_a} {entity_b} connection relationship ties",
            search_depth="advanced",
            max_results=8
        )
        
        return result
    
    async def public_records_search(self, entity: str, entity_type: str) -> Dict[str, Any]:
        """
        Strategy 7: Public records search
        
        Find official government records
        Use for: Verification, legal status
        """
        if entity_type == "organization":
            query = f"{entity} registration government official records certificate"
        elif entity_type == "person":
            query = f"{entity} government position appointment official role"
        else:
            query = f"{entity} official records"
        
        # Prioritize .gov domains
        result = await self.tavily.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            include_domains=["gov"]
        )
        
        return result
    
    async def temporal_search(self, entity: str, date_range: str) -> Dict[str, Any]:
        """
        Strategy 8: Temporal search
        
        Search entity within specific time period
        Use for: Understanding entity behavior at specific time
        """
        result = await self.tavily.search(
            query=f"{entity} {date_range}",
            search_depth="advanced",
            max_results=10,
            days=365  # Search last year
        )
        
        return result
    
    async def extract_deep_content(self, urls: List[str]) -> Dict[str, Any]:
        """
        Extract full content from critical sources
        
        Use when: Found important article but need full text
        """
        # Limit to top 3 URLs
        urls = urls[:3]
        
        result = await self.tavily.extract(
            urls=urls,
            extract_depth="advanced",
            format="markdown"
        )
        
        return result
    
    async def ned_grants_search(self, country: str) -> Dict[str, Any]:
        """
        Specialized: Search for NED grants to a country
        
        Use for: Foreign funding investigation
        """
        result = await self.tavily.search(
            query=f"National Endowment Democracy NED {country} grants recipients organizations",
            search_depth="advanced",
            max_results=15,
            include_domains=["ned.org"]
        )
        
        return result
    
    async def training_programs_search(self, org_name: str, country: str) -> Dict[str, Any]:
        """
        Specialized: Search for training programs
        
        Use for: Detecting capacity building, activist training
        """
        result = await self.tavily.search(
            query=f"{org_name} {country} training workshop digital security activists capacity building",
            search_depth="advanced",
            max_results=10
        )
        
        return result


