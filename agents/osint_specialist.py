from typing import Dict, List, Any
import re
from datetime import datetime

class OSINTSpecialist:
    def __init__(self):
        self.dork_patterns = self.initialize_dork_patterns()
        self.search_history = []
        
    def initialize_dork_patterns(self) -> Dict[str, List[str]]:
        """Initialize advanced Google dork patterns"""
        return {
            'sensitive_files': [
                'filetype:pdf intext:"confidential"',
                'filetype:xlsx intext:"internal use only"',
                'filetype:doc intext:"proprietary"',
                'filetype:txt intext:"password" OR intext:"username"'
            ],
            'exposed_directories': [
                'intitle:"Index of /" "parent directory"',
                'intitle:"Index of /" site:{domain}',
                'intitle:"Index of /" intext:"backup"'
            ],
            'config_files': [
                'filetype:env OR filetype:cfg OR filetype:conf',
                'filetype:xml intext:"password"',
                'filetype:ini intext:"credentials"'
            ],
            'database_files': [
                'filetype:sql "INSERT INTO" -git',
                'filetype:db OR filetype:sqlite OR filetype:mdb',
                'filetype:csv intext:"email" intext:"password"'
            ],
            'exposed_panels': [
                'inurl:admin OR inurl:login OR inurl:portal',
                'intitle:"Dashboard" intext:"Welcome"',
                'inurl:phpmyadmin OR inurl:cpanel'
            ],
            'phone_numbers': [
                'intext:"phone" OR intext:"mobile" OR intext:"cell"',
                'intext:"contact us" AND intext:"phone"',
                'filetype:pdf OR filetype:doc intext:"phone directory"',
                'site:linkedin.com OR site:facebook.com intext:"phone"'
            ]
        }

    def create_advanced_dork(self, target: str, search_type: str) -> str:
        """Create advanced Google dork query"""
        base_patterns = self.dork_patterns.get(search_type, [])
        if not base_patterns:
            return target

        selected_pattern = base_patterns[0]  # Choose appropriate pattern based on context
        return f"{selected_pattern} site:{target}" if target else selected_pattern

    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive domain analysis"""
        return {
            'domain': domain,
            'search_patterns': [
                self.create_advanced_dork(domain, 'sensitive_files'),
                self.create_advanced_dork(domain, 'exposed_directories'),
                self.create_advanced_dork(domain, 'config_files')
            ],
            'timestamp': datetime.now().isoformat()
        }

    def search_people(self, name: str) -> Dict[str, List[str]]:
        """Perform advanced people search"""
        dorks = [
            f'intext:"{name}" site:linkedin.com',
            f'intext:"{name}" site:twitter.com OR site:facebook.com',
            f'intext:"{name}" filetype:pdf OR filetype:doc'
        ]
        return {
            'name': name,
            'search_patterns': dorks,
            'timestamp': datetime.now().isoformat()
        }

    def find_exposed_data(self, target: str) -> Dict[str, Any]:
        """Find potentially exposed sensitive data"""
        patterns = {
            'api_keys': [
                'intext:"api_key" OR intext:"apikey"',
                'intext:"api_secret" OR intext:"apisecret"'
            ],
            'credentials': [
                'intext:"password" OR intext:"passwd"',
                'intext:"username" AND intext:"password"'
            ],
            'tokens': [
                'intext:"access_token" OR intext:"bearer"',
                'intext:"oauth" AND intext:"secret"'
            ]
        }
        
        return {
            'target': target,
            'patterns': patterns,
            'timestamp': datetime.now().isoformat()
        }

    def generate_dork_report(self) -> Dict[str, Any]:
        """Generate report of all dork patterns"""
        return {
            'total_patterns': sum(len(patterns) for patterns in self.dork_patterns.values()),
            'categories': list(self.dork_patterns.keys()),
            'sample_dorks': {
                category: patterns[0] 
                for category, patterns in self.dork_patterns.items()
            },
            'timestamp': datetime.now().isoformat()
        }

    def analyze_security_risks(self, dork_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze security risks in search results"""
        risk_levels = {
            'high': [],
            'medium': [],
            'low': []
        }

        for result in dork_results:
            risk_level = self.assess_risk_level(result)
            risk_levels[risk_level].append(result)

        return {
            'risk_summary': {
                level: len(items) 
                for level, items in risk_levels.items()
            },
            'timestamp': datetime.now().isoformat()
        }

    def assess_risk_level(self, result: Dict[str, Any]) -> str:
        """Assess risk level of a search result"""
        high_risk_patterns = [
            r'password',
            r'api[_]?key',
            r'secret',
            r'token',
            r'credential'
        ]

        medium_risk_patterns = [
            r'internal',
            r'confidential',
            r'private'
        ]

        content = str(result.get('content', '')).lower()
        
        if any(re.search(pattern, content) for pattern in high_risk_patterns):
            return 'high'
        elif any(re.search(pattern, content) for pattern in medium_risk_patterns):
            return 'medium'
        return 'low'

    def report_findings(self) -> Dict[str, Any]:
        """Report findings to Project Manager"""
        return {
            'dork_patterns': self.generate_dork_report(),
            'search_history': self.search_history,
            'timestamp': datetime.now().isoformat()
        }

    def search_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Search for information related to a phone number"""
        # Clean the phone number to handle different formats
        cleaned_number = re.sub(r'[^\d+]', '', phone_number)
        
        search_patterns = [
            f'intext:"{cleaned_number}"',
            f'intext:"{cleaned_number}" site:linkedin.com OR site:facebook.com',
            f'intext:"{cleaned_number}" site:whitepages.com OR site:truepeoplesearch.com',
            f'intext:"{cleaned_number}" filetype:pdf OR filetype:doc OR filetype:xlsx'
        ]

        # Add phone number specific patterns
        area_code = cleaned_number[:3] if len(cleaned_number) >= 3 else ''
        if area_code:
            search_patterns.append(f'intext:"({area_code})" site:yellowpages.com')

        return {
            'phone_number': cleaned_number,
            'area_code': area_code,
            'search_patterns': search_patterns,
            'potential_sources': [
                'Social Media Profiles',
                'Business Directories',
                'Public Records',
                'Contact Lists'
            ],
            'timestamp': datetime.now().isoformat()
        }

    def analyze_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Analyze a phone number for additional information"""
        cleaned_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Basic phone number analysis
        analysis = {
            'format': self._analyze_phone_format(cleaned_number),
            'type': self._determine_phone_type(cleaned_number),
            'location': self._get_number_location(cleaned_number),
            'risk_level': 'low',  # Default risk level
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis

    def _analyze_phone_format(self, number: str) -> Dict[str, str]:
        """Analyze phone number format"""
        formats = {
            'raw': number,
            'formatted': self._format_phone_number(number),
            'international': self._format_international(number),
            'valid': self._is_valid_number(number)
        }
        return formats

    def _determine_phone_type(self, number: str) -> str:
        """Determine type of phone number (mobile, landline, etc.)"""
        # This would typically use a phone number database or API
        # For now, return a placeholder
        return "Unknown"

    def _get_number_location(self, number: str) -> Dict[str, str]:
        """Get location information for a phone number"""
        # This would typically use a phone number database or API
        return {
            'country': 'Unknown',
            'region': 'Unknown',
            'carrier': 'Unknown'
        }

    def _format_phone_number(self, number: str) -> str:
        """Format phone number in standard format"""
        if len(number) == 10:
            return f"({number[:3]}) {number[3:6]}-{number[6:]}"
        return number

    def _format_international(self, number: str) -> str:
        """Format phone number in international format"""
        if len(number) == 10:
            return f"+1 {number[:3]} {number[3:6]} {number[6:]}"
        return number

    def _is_valid_number(self, number: str) -> bool:
        """Check if phone number is valid"""
        return len(number) >= 10 and number.isdigit() 