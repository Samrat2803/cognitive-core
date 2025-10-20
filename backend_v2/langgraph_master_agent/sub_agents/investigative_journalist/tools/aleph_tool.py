"""
OCCRP Aleph Tool for Investigative Journalist
Search leaked documents, sanctions lists, company registries
"""
import requests
from typing import List, Dict, Optional


class AlephTool:
    """
    Tool for searching OCCRP Aleph database
    
    Contains:
    - Panama Papers, Paradise Papers, Pandora Papers
    - Sanctions lists (OFAC, UN, EU)
    - Company registries worldwide
    - Court documents, procurement records
    - PEPs (Politically Exposed Persons)
    """
    
    API_BASE = "https://aleph.occrp.org/api/2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'InvestigativeJournalistBot/1.0 (Educational Research)'
        })
    
    def search(
        self,
        query: str,
        schema: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """
        Search Aleph for entities matching query
        
        Args:
            query: Search query (company name, person name, etc.)
            schema: Entity type filter (Company, Person, Organization)
            limit: Max results
            
        Returns:
            Search results with entities
        """
        print(f"\n🔍 Aleph Search: {query}")
        if schema:
            print(f"   Filter: {schema}")
        
        params = {
            'q': query,
            'limit': limit
        }
        
        if schema:
            params['filter:schema'] = schema
        
        try:
            response = self.session.get(
                f"{self.API_BASE}/search",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            print(f"   ✅ Found {len(results)} results")
            
            parsed_results = []
            for result in results:
                parsed_results.append(self._parse_entity(result))
            
            return {
                'status': 'success',
                'query': query,
                'total': data.get('total', 0),
                'results': parsed_results
            }
        
        except requests.Timeout:
            print(f"   ⚠️  Aleph timeout")
            return {'status': 'timeout', 'query': query, 'results': []}
        except Exception as e:
            print(f"   ❌ Aleph error: {e}")
            return {'status': 'error', 'query': query, 'results': [], 'error': str(e)}
    
    def search_company(self, company_name: str) -> Dict:
        """
        Search for a specific company
        Finds: Registrations, officers, addresses, leaked documents
        """
        return self.search(company_name, schema='Company')
    
    def search_person(self, person_name: str) -> Dict:
        """
        Search for a specific person
        Finds: Sanctions, PEP status, company connections
        """
        return self.search(person_name, schema='Person')
    
    def check_sanctions(self, name: str) -> Dict:
        """
        Check if entity is sanctioned
        Searches sanctions lists from OFAC, UN, EU, etc.
        """
        print(f"\n🚨 Sanctions Check: {name}")
        
        # Search with sanctions-specific query
        result = self.search(f"{name} sanctions", limit=5)
        
        # Filter for actual sanction entities
        sanctioned = []
        for entity in result.get('results', []):
            datasets = entity.get('datasets', [])
            properties = entity.get('properties', {})
            
            # Check if from sanctions dataset
            is_sanctions = any('sanction' in d.lower() for d in datasets)
            
            if is_sanctions:
                sanctioned.append({
                    'name': properties.get('name', ['Unknown'])[0],
                    'datasets': datasets,
                    'summary': properties.get('summary', [''])[0],
                    'countries': properties.get('country', []),
                    'programs': properties.get('program', [])
                })
        
        return {
            'status': 'success',
            'name': name,
            'sanctioned': len(sanctioned) > 0,
            'sanction_records': sanctioned,
            'summary': f"{'SANCTIONED' if sanctioned else 'Not sanctioned'} - {len(sanctioned)} records found"
        }
    
    def _parse_entity(self, raw_entity: Dict) -> Dict:
        """Parse Aleph entity into clean format"""
        properties = raw_entity.get('properties', {})
        
        # Helper to get first value from list
        def first(prop_list):
            return prop_list[0] if isinstance(prop_list, list) and prop_list else None
        
        parsed = {
            'id': raw_entity.get('id'),
            'schema': raw_entity.get('schema'),
            'name': first(properties.get('name')),
            'summary': first(properties.get('summary')),
            'datasets': raw_entity.get('collection', {}).get('label', 'Unknown'),
            'countries': properties.get('country', []),
            'addresses': properties.get('address', []),
            'properties': {}
        }
        
        # Schema-specific parsing
        if parsed['schema'] == 'Company':
            parsed['properties'] = {
                'jurisdiction': first(properties.get('jurisdiction')),
                'registration_number': first(properties.get('registrationNumber')),
                'incorporation_date': first(properties.get('incorporationDate')),
                'status': first(properties.get('status')),
                'directors': properties.get('director', []),
            }
        elif parsed['schema'] == 'Person':
            parsed['properties'] = {
                'nationality': properties.get('nationality', []),
                'birth_date': first(properties.get('birthDate')),
                'position': first(properties.get('position')),
                'notes': first(properties.get('notes'))
            }
        
        return parsed
    
    def format_for_llm(self, search_result: Dict) -> str:
        """
        Format Aleph results for LLM consumption
        Returns clean, structured text
        """
        if search_result.get('status') != 'success':
            return f"Aleph search failed: {search_result.get('error', 'Unknown error')}"
        
        results = search_result.get('results', [])
        
        if not results:
            return f"No results found in Aleph for: {search_result.get('query')}"
        
        output_lines = [
            f"ALEPH INTELLIGENCE REPORT",
            f"Query: {search_result.get('query')}",
            f"Total Results: {search_result.get('total', 0)}",
            "",
            "FINDINGS:",
            ""
        ]
        
        for i, result in enumerate(results[:5], 1):  # Top 5
            output_lines.append(f"{i}. {result.get('name', 'Unknown')}")
            output_lines.append(f"   Type: {result.get('schema', 'Unknown')}")
            output_lines.append(f"   Source: {result.get('datasets', 'Unknown')}")
            
            if result.get('summary'):
                output_lines.append(f"   Summary: {result['summary']}")
            
            if result.get('countries'):
                output_lines.append(f"   Countries: {', '.join(result['countries'][:3])}")
            
            # Schema-specific details
            props = result.get('properties', {})
            if result['schema'] == 'Company':
                if props.get('jurisdiction'):
                    output_lines.append(f"   Jurisdiction: {props['jurisdiction']}")
                if props.get('registration_number'):
                    output_lines.append(f"   Registration: {props['registration_number']}")
                if props.get('directors'):
                    directors = props['directors'][:3]
                    output_lines.append(f"   Directors: {', '.join(directors)}")
            elif result['schema'] == 'Person':
                if props.get('position'):
                    output_lines.append(f"   Position: {props['position']}")
                if props.get('nationality'):
                    output_lines.append(f"   Nationality: {', '.join(props['nationality'][:2])}")
            
            output_lines.append("")
        
        return "\n".join(output_lines)


if __name__ == "__main__":
    # Test with Indian pharma companies
    tool = AlephTool()
    
    print("="*80)
    print("TESTING ALEPH TOOL")
    print("="*80)
    
    # Test 1: Company search
    result1 = tool.search_company("Maiden Pharmaceuticals")
    print("\n" + tool.format_for_llm(result1))
    
    # Test 2: Sanctions check
    result2 = tool.check_sanctions("Maiden Pharmaceuticals")
    print("\n" + "="*80)
    print(f"Sanctions: {result2['summary']}")

