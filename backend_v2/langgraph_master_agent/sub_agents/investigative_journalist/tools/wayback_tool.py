"""
Wayback Machine Tool for Investigative Journalist
Detects cover-ups by comparing historical website versions
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class WaybackMachineTool:
    """
    Tool for accessing Internet Archive Wayback Machine
    Use for: Cover-up detection, historical comparison, deleted content
    """
    
    CDX_API = "http://web.archive.org/cdx/search/cdx"
    WAYBACK_BASE = "https://web.archive.org/web"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'InvestigativeJournalistBot/1.0 (Educational Research)'
        })
    
    def search_snapshots(
        self, 
        url: str, 
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        Find archived snapshots of a URL
        
        Args:
            url: Target URL to search
            from_date: Start date (YYYYMMDD format)
            to_date: End date (YYYYMMDD format)
            limit: Max snapshots to return
            
        Returns:
            List of snapshot info dicts with timestamp and URL
        """
        # Default: last 2 years
        if not to_date:
            to_date = datetime.now().strftime('%Y%m%d')
        if not from_date:
            two_years_ago = datetime.now() - timedelta(days=730)
            from_date = two_years_ago.strftime('%Y%m%d')
        
        params = {
            'url': url,
            'output': 'json',
            'from': from_date,
            'to': to_date,
            'filter': 'statuscode:200',  # Only successful captures
            'collapse': 'timestamp:8',    # One per day
            'limit': limit
        }
        
        try:
            response = self.session.get(self.CDX_API, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # First row is headers
            if len(data) <= 1:
                return []
            
            headers = data[0]
            snapshots = []
            
            for row in data[1:]:
                snapshot_dict = dict(zip(headers, row))
                timestamp = snapshot_dict.get('timestamp', '')
                
                # Parse timestamp
                try:
                    dt = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
                    formatted_date = dt.strftime('%Y-%m-%d')
                except:
                    formatted_date = timestamp[:8]
                
                snapshots.append({
                    'timestamp': timestamp,
                    'date': formatted_date,
                    'url': f"{self.WAYBACK_BASE}/{timestamp}/{url}",
                    'original_url': url,
                    'statuscode': snapshot_dict.get('statuscode', '200')
                })
            
            return snapshots
        
        except requests.Timeout:
            print(f"⚠️  Wayback Machine timeout for {url}")
            return []
        except Exception as e:
            print(f"❌ Wayback Machine error: {e}")
            return []
    
    def get_snapshot_content(self, snapshot_url: str) -> Optional[str]:
        """
        Retrieve content from a specific snapshot
        
        Args:
            snapshot_url: Full Wayback Machine URL
            
        Returns:
            Text content or None
        """
        try:
            response = self.session.get(snapshot_url, timeout=20)
            response.raise_for_status()
            
            # Basic text extraction from HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts, styles
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            return text
        
        except Exception as e:
            print(f"❌ Could not fetch snapshot content: {e}")
            return None
    
    def compare_versions(
        self, 
        url: str,
        significant_change_threshold: int = 500
    ) -> Dict:
        """
        Compare current version with historical versions
        Detects: Content removal, significant changes, potential cover-ups
        
        Args:
            url: URL to investigate
            significant_change_threshold: Minimum character difference to flag
            
        Returns:
            Dict with comparison results
        """
        print(f"\n🔍 Wayback Machine: Investigating {url}")
        
        # Get snapshots
        snapshots = self.search_snapshots(url, limit=10)
        
        if not snapshots:
            return {
                'status': 'no_snapshots',
                'message': 'No archived versions found',
                'url': url
            }
        
        print(f"   Found {len(snapshots)} snapshots")
        
        # Get current version
        try:
            current_response = self.session.get(url, timeout=15)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(current_response.content, 'html.parser')
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            current_text = soup.get_text(separator=' ', strip=True)
        except:
            current_text = None
        
        # Compare with oldest and newest snapshots
        comparisons = []
        
        for snapshot in [snapshots[0], snapshots[-1]]:  # First and last
            snapshot_content = self.get_snapshot_content(snapshot['url'])
            
            if snapshot_content and current_text:
                old_len = len(snapshot_content)
                new_len = len(current_text)
                diff = abs(new_len - old_len)
                
                change_type = "unknown"
                if new_len < old_len - significant_change_threshold:
                    change_type = "major_deletion"
                elif new_len > old_len + significant_change_threshold:
                    change_type = "major_addition"
                elif diff < significant_change_threshold:
                    change_type = "minor_changes"
                
                comparisons.append({
                    'snapshot_date': snapshot['date'],
                    'snapshot_url': snapshot['url'],
                    'old_length': old_len,
                    'current_length': new_len,
                    'difference': diff,
                    'change_type': change_type,
                    'percentage_change': round((diff / old_len) * 100, 1) if old_len > 0 else 0
                })
                
                # Small delay between requests
                time.sleep(0.5)
        
        # Determine if suspicious
        suspicious = any(c['change_type'] == 'major_deletion' for c in comparisons)
        
        return {
            'status': 'success',
            'url': url,
            'current_available': current_text is not None,
            'total_snapshots': len(snapshots),
            'snapshots_checked': comparisons,
            'suspicious_activity': suspicious,
            'earliest_snapshot': snapshots[0]['date'],
            'latest_snapshot': snapshots[-1]['date'],
            'summary': self._generate_summary(comparisons, suspicious)
        }
    
    def _generate_summary(self, comparisons: List[Dict], suspicious: bool) -> str:
        """Generate human-readable summary"""
        if not comparisons:
            return "No comparison data available"
        
        summary_parts = []
        
        for comp in comparisons:
            change = comp['change_type']
            date = comp['snapshot_date']
            pct = comp['percentage_change']
            
            if change == 'major_deletion':
                summary_parts.append(
                    f"🚨 MAJOR DELETION detected since {date}: "
                    f"{comp['difference']:,} characters removed ({pct}% reduction)"
                )
            elif change == 'major_addition':
                summary_parts.append(
                    f"📈 Major content addition since {date}: "
                    f"{comp['difference']:,} characters added ({pct}% increase)"
                )
            else:
                summary_parts.append(
                    f"✓ Minor changes since {date} ({pct}% change)"
                )
        
        if suspicious:
            summary_parts.append("\n⚠️  POSSIBLE COVER-UP: Significant content removal detected")
        
        return "\n".join(summary_parts)


if __name__ == "__main__":
    # Test with CDSCO (Indian drug regulator)
    tool = WaybackMachineTool()
    
    test_url = "https://cdsco.gov.in"
    result = tool.compare_versions(test_url)
    
    print("\n" + "="*80)
    print("WAYBACK MACHINE ANALYSIS")
    print("="*80)
    print(f"URL: {result['url']}")
    print(f"Status: {result['status']}")
    print(f"Total snapshots: {result.get('total_snapshots', 0)}")
    print(f"Suspicious activity: {result.get('suspicious_activity', False)}")
    print("\nSummary:")
    print(result.get('summary', 'N/A'))

