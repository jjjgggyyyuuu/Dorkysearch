import os
from typing import Dict, List, Optional, Any, Callable
import requests
from bs4 import BeautifulSoup
import inspect

class SearchAgent:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        
    def create_dork_query(self, query: str, search_type: str) -> str:
        """Create an advanced Google dork query based on search type."""
        dorks = {
            'general': query,
            'documents': f'filetype:(pdf OR doc OR docx OR xls OR xlsx) {query}',
            'sensitive': f'intext:("password" OR "username" OR "admin") {query}',
            'directories': f'intitle:"Index of" {query}',
            'technology': f'inurl:("php" OR "asp" OR "jsp") {query}'
        }
        return dorks.get(search_type, query)

    def search(self, query: str, search_type: str = 'general') -> Dict[str, Any]:
        """Perform a search using Google Custom Search API with advanced dork queries."""
        if not self.google_api_key or not self.google_cse_id:
            return {
                'error': 'Google API credentials not configured',
                'items': [],
                'query': query,
                'type': search_type
            }

        dork_query = self.create_dork_query(query, search_type)
        
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': dork_query
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'type': search_type
                    })

            return {
                'query': query,
                'dork_query': dork_query,
                'type': search_type,
                'items': results,
                'error': None
            }

        except requests.exceptions.RequestException as e:
            return {
                'error': f'Search failed: {str(e)}',
                'items': [],
                'query': query,
                'type': search_type,
                'dork_query': dork_query
            }

    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze search results and provide insights."""
        # Check if results is a dictionary
        if not isinstance(results, dict):
            return {
                'total_results': 0,
                'insights': 'Invalid results format.'
            }
            
        # Check if items exists and is a list
        items = results.get('items')
        if items is None:
            return {
                'total_results': 0,
                'insights': 'No results found.'
            }
            
        # Check if items is a list and can be iterated
        if not isinstance(items, list):
            return {
                'total_results': 0,
                'insights': 'Results are not in the expected format.'
            }

        # Now we know items is a list and can safely get its length
        total_results = len(items)
        
        # Get search type safely
        search_type = results.get('type', 'general')
        if not isinstance(search_type, str):
            search_type = 'general'
        
        # Generate insights
        insights = []
        if search_type == 'sensitive':
            insights.append('⚠️ Found potentially sensitive information. Review carefully.')
        elif search_type == 'documents':
            insights.append('📄 Found document results. Check file types before downloading.')
        elif search_type == 'technology':
            insights.append('🔧 Found technology-related results. Review for security implications.')
        
        # Add default insight if none were added
        if not insights:
            insights.append(f'Found {total_results} results for your search.')
        
        # Return the analysis
        return {
            'total_results': total_results,
            'insights': ' '.join(insights)
        } 