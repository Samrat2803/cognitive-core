"""
Quick test script to demonstrate artifact generation
Run this to see Entity Network, Timeline, and Evidence Chain artifacts
"""

import asyncio
import sys
from pathlib import Path

# Add current dir to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from tools.artifact_generator import generate_all_artifacts


async def main():
    """Test artifact generation with rich sample data"""
    
    print("="*80)
    print("🧪 TESTING INVESTIGATIVE JOURNALIST ARTIFACTS")
    print("="*80)
    
    # Realistic investigation state (simulating completed investigation)
    test_state = {
        "investigation_id": "demo_investigation_001",
        "initial_query": "Investigate the root cause of deaths related to cough syrups in India",
        "iteration": 8,
        "max_iterations": 10,
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # ENTITIES (people, organizations, substances)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        "entities": {
            "Maiden Pharmaceuticals": {
                "type": "organization",
                "role": "Manufacturer of contaminated cough syrups",
                "importance": 0.95,
                "investigated": True
            },
            "Diethylene Glycol (DEG)": {
                "type": "substance",
                "role": "Toxic contaminant found in syrups",
                "importance": 0.90,
                "investigated": True
            },
            "Central Drugs Standard Control Organisation (CDSCO)": {
                "type": "organization",
                "role": "Indian drug regulatory authority",
                "importance": 0.85,
                "investigated": True
            },
            "World Health Organization (WHO)": {
                "type": "organization",
                "role": "Issued global alert on contaminated products",
                "importance": 0.80,
                "investigated": True
            },
            "Gambia": {
                "type": "location",
                "role": "Country where 70 children died",
                "importance": 0.88,
                "investigated": True
            },
            "Uzbekistan": {
                "type": "location",
                "role": "Country with 18 deaths reported",
                "importance": 0.75,
                "investigated": True
            },
            "Dr. Rajeev Singh Raghuvanshi": {
                "type": "person",
                "role": "Drug Controller General of India",
                "importance": 0.70,
                "investigated": False
            },
            "Marion Biotech": {
                "type": "organization",
                "role": "Manufacturer linked to Uzbekistan deaths",
                "importance": 0.82,
                "investigated": True
            },
            "Propylene Glycol": {
                "type": "substance",
                "role": "Safe ingredient that should have been used",
                "importance": 0.65,
                "investigated": True
            }
        },
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # CONNECTIONS (relationships between entities)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        "connections": [
            {
                "from": "Maiden Pharmaceuticals",
                "to": "Diethylene Glycol (DEG)",
                "type": "manufactured products containing"
            },
            {
                "from": "Maiden Pharmaceuticals",
                "to": "Gambia",
                "type": "exported contaminated products to"
            },
            {
                "from": "Marion Biotech",
                "to": "Uzbekistan",
                "type": "exported contaminated products to"
            },
            {
                "from": "WHO",
                "to": "Maiden Pharmaceuticals",
                "type": "issued alert about"
            },
            {
                "from": "CDSCO",
                "to": "Maiden Pharmaceuticals",
                "type": "regulated by (failed inspection)"
            },
            {
                "from": "CDSCO",
                "to": "Marion Biotech",
                "type": "regulated by"
            },
            {
                "from": "Dr. Rajeev Singh Raghuvanshi",
                "to": "CDSCO",
                "type": "leads"
            },
            {
                "from": "Diethylene Glycol (DEG)",
                "to": "Propylene Glycol",
                "type": "substituted for (should have been)"
            }
        ],
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # FACTS (discovered during investigation)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        "facts": [
            "70 children died in Gambia between July and October 2022 from acute kidney injury",
            "WHO issued global alert in October 2022 linking deaths to contaminated cough syrups",
            "Four cough syrups manufactured by Maiden Pharmaceuticals contained toxic levels of DEG",
            "DEG levels in syrups were 300-500 times higher than safe limits",
            "18 children died in Uzbekistan in December 2022 from similar contaminated products",
            "Marion Biotech produced the syrups linked to Uzbekistan deaths",
            "CDSCO suspended manufacturing licenses of both Maiden and Marion",
            "India is the world's largest exporter of generic medicines",
            "DEG is used as industrial solvent and antifreeze, never for human consumption",
            "Propylene Glycol is the safe pharmaceutical-grade alternative that should have been used",
            "Laboratory tests confirmed presence of DEG and Ethylene Glycol in samples",
            "WHO recommended member states detect and remove contaminated products",
            "Criminal investigations launched against both companies",
            "Similar incidents occurred in Panama (2006) and Haiti (1995) with DEG contamination"
        ],
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # HYPOTHESES (tested explanations)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        "hypotheses": [
            {
                "id": "h1",
                "statement": "Cost-cutting led manufacturers to substitute industrial-grade DEG for pharmaceutical-grade Propylene Glycol",
                "status": "proven",
                "confidence": 0.92,
                "importance": 0.95,
                "priority": 1,
                "questions": [
                    {
                        "q": "What is the price difference between DEG and Propylene Glycol?",
                        "a": "DEG costs approximately 50% less than pharmaceutical-grade Propylene Glycol",
                        "src": "https://example.com/price-analysis",
                        "status": "answered",
                        "iteration": 3
                    },
                    {
                        "q": "Were there financial pressures on the manufacturers?",
                        "a": "Both companies were competing for export contracts with thin profit margins",
                        "src": "https://example.com/financial-records",
                        "status": "answered",
                        "iteration": 4
                    },
                    {
                        "q": "Did quality control detect the substitution?",
                        "a": "No, quality control tests were inadequate to detect DEG contamination",
                        "src": "https://example.com/qc-report",
                        "status": "answered",
                        "iteration": 5
                    }
                ]
            },
            {
                "id": "h2",
                "statement": "Regulatory oversight failures allowed contaminated products to be exported",
                "status": "proven",
                "confidence": 0.88,
                "importance": 0.90,
                "priority": 2,
                "questions": [
                    {
                        "q": "How often were manufacturing facilities inspected?",
                        "a": "Last CDSCO inspection was 18 months before the contamination was discovered",
                        "src": "https://example.com/inspection-logs",
                        "status": "answered",
                        "iteration": 6
                    },
                    {
                        "q": "What were the gaps in the regulatory framework?",
                        "a": "No mandatory testing for DEG contamination in export products, relied on manufacturer self-certification",
                        "src": "https://example.com/regulatory-gaps",
                        "status": "answered",
                        "iteration": 6
                    }
                ]
            },
            {
                "id": "h3",
                "statement": "This was an isolated incident limited to two manufacturers",
                "status": "disproven",
                "confidence": 0.25,
                "importance": 0.75,
                "priority": 3,
                "questions": [
                    {
                        "q": "Were other manufacturers found with similar violations?",
                        "a": "Subsequent WHO investigation found 6 additional manufacturers with quality control issues",
                        "src": "https://example.com/who-investigation",
                        "status": "answered",
                        "iteration": 7
                    },
                    {
                        "q": "Have similar incidents occurred before?",
                        "a": "Yes, Panama 2006 (93 deaths) and Haiti 1995 (88 deaths) from DEG contamination",
                        "src": "https://example.com/historical-incidents",
                        "status": "answered",
                        "iteration": 7
                    }
                ]
            },
            {
                "id": "h4",
                "statement": "Supply chain opacity enabled procurement of industrial-grade chemicals without detection",
                "status": "exploring",
                "confidence": 0.65,
                "importance": 0.80,
                "priority": 4,
                "questions": [
                    {
                        "q": "Where did the manufacturers source their DEG?",
                        "a": "Investigation ongoing, preliminary findings suggest chemical traders in Gujarat",
                        "src": None,
                        "status": "exploring",
                        "iteration": 8
                    },
                    {
                        "q": "Was there a documented chain of custody?",
                        "a": None,
                        "src": None,
                        "status": "unanswered",
                        "iteration": None
                    }
                ]
            }
        ],
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # ANOMALIES (suspicious patterns)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        "anomalies": [
            "CDSCO cleared Maiden Pharmaceuticals for export 6 months before WHO alert despite documented quality issues",
            "Marion Biotech continued operations for weeks after Uzbekistan deaths before license suspension",
            "No criminal charges filed against any individuals despite 88 child deaths",
            "Export approval process took only 3 days - suspiciously fast for pharmaceutical products",
            "Both manufacturers had history of minor violations that were not escalated"
        ]
    }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GENERATE ARTIFACTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    artifacts = await generate_all_artifacts(test_state, output_dir="demo_artifacts")
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETE - Generated {len(artifacts)} artifacts:")
    print(f"{'='*80}")
    
    for artifact in artifacts:
        print(f"\n📦 {artifact['name']}")
        print(f"   Type: {artifact['type']}")
        print(f"   Path: {artifact['path']}")
        print(f"   View: file://{Path(artifact['path']).absolute()}")
    
    print(f"\n{'='*80}")
    print(f"🎉 Open the artifacts in your browser to see:")
    print(f"{'='*80}")
    print(f"1. 🕸️  Entity Network Graph - Interactive network showing relationships")
    print(f"2. 📅 Timeline - Facts discovered across iterations")
    print(f"3. 🔗 Evidence Chain - Flow from investigation to hypotheses to conclusions")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())

