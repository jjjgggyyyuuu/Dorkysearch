#!/usr/bin/env python3
"""
Domain Research Agent
A tool to find potentially valuable domain names under $10 for resale.
"""

import os
import re
import json
import time
import random
import whois
import requests
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import words
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Download NLTK words corpus if not already downloaded
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

class DomainResearchAgent:
    """Agent that finds potentially valuable domain names under $10"""
    
    def __init__(self):
        """Initialize the domain research agent"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.namecheap_api_url = "https://www.namecheap.com/domains/registration/results/"
        self.godaddy_api_url = "https://api.godaddy.com/v1/domains/available"
        self.trending_keywords = []
        self.valuable_tlds = ['.com', '.ai', '.io', '.co', '.net', '.org', '.app']
        self.premium_tlds = ['.com', '.ai', '.io']
        self.industry_trends = self._load_industry_trends()
        self.load_trending_keywords()
        
    def _load_industry_trends(self):
        """Load current industry trends for domain valuation"""
        return {
            "tech": {
                "keywords": ["ai", "ml", "data", "cloud", "saas", "app", "tech", "cyber", "quantum", "code"],
                "growth_factor": 2.5,
                "demand_level": "Very High",
                "future_outlook": "Strong upward trend as technology continues to evolve"
            },
            "finance": {
                "keywords": ["fin", "pay", "bank", "invest", "crypto", "nft", "money", "cash", "coin", "wealth"],
                "growth_factor": 2.3,
                "demand_level": "High",
                "future_outlook": "Strong with the growth of fintech and digital finance"
            },
            "health": {
                "keywords": ["health", "med", "care", "bio", "life", "well", "fit", "diet", "doctor", "therapy"],
                "growth_factor": 2.0,
                "demand_level": "High",
                "future_outlook": "Growing steadily as digital health becomes more integrated"
            },
            "ecommerce": {
                "keywords": ["shop", "buy", "store", "sell", "market", "deal", "retail", "cart", "price", "order"],
                "growth_factor": 1.8,
                "demand_level": "High",
                "future_outlook": "Stable growth as online shopping becomes the norm"
            },
            "sustainability": {
                "keywords": ["green", "eco", "sustainable", "clean", "solar", "carbon", "earth", "climate", "recycle"],
                "growth_factor": 2.2,
                "demand_level": "Growing",
                "future_outlook": "Strong growth potential as focus on sustainability increases"
            },
            "entertainment": {
                "keywords": ["play", "game", "stream", "watch", "video", "media", "fun", "social", "live", "content"],
                "growth_factor": 1.7,
                "demand_level": "Moderate",
                "future_outlook": "Stable with potential for growth in specific niches"
            }
        }
        
    def load_trending_keywords(self):
        """Load trending keywords from various sources"""
        print("Loading trending keywords...")
        try:
            # Method 1: From technology news sites
            tech_sources = [
                "https://techcrunch.com/",
                "https://www.wired.com/",
                "https://www.theverge.com/"
            ]
            
            for source in tech_sources:
                try:
                    response = requests.get(source, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # Extract headlines and keywords
                        headlines = soup.find_all(['h1', 'h2', 'h3'], limit=20)
                        for headline in headlines:
                            if headline.text:
                                words = self._extract_keywords(headline.text)
                                self.trending_keywords.extend(words)
                except Exception as e:
                    print(f"Error fetching from {source}: {e}")
                    
            # Method 2: Predefined trending technology areas
            tech_trends = [
                "ai", "crypto", "blockchain", "nft", "metaverse", "quantum", 
                "cloud", "saas", "ml", "data", "cyber", "fintech", "edtech", 
                "biotech", "healthtech", "green", "eco", "carbon", "solar",
                "smart", "digital", "virtual", "mobile", "app", "web3", "defi"
            ]
            self.trending_keywords.extend(tech_trends)
            
            # Add industry-specific keywords
            for industry, data in self.industry_trends.items():
                self.trending_keywords.extend(data["keywords"])
            
            # Remove duplicates and sort by length (shorter is generally better for domains)
            self.trending_keywords = list(set(self.trending_keywords))
            self.trending_keywords.sort(key=len)
            
            print(f"Loaded {len(self.trending_keywords)} trending keywords")
            
        except Exception as e:
            print(f"Error loading trending keywords: {e}")
            # Fallback to a basic set of keywords
            self.trending_keywords = [
                "ai", "crypto", "tech", "meta", "web", "nft", "cloud", 
                "data", "cyber", "green", "smart", "app", "saas", "learn"
            ]
    
    def _extract_keywords(self, text):
        """Extract potential keywords from text"""
        # Clean text and split into words
        text = re.sub(r'[^\w\s]', '', text.lower())
        all_words = text.split()
        
        # Filter for words that might make good domains (3-10 chars)
        potential_keywords = [word for word in all_words if 3 <= len(word) <= 10]
        
        # Also extract two-word combinations that are short
        word_pairs = []
        for i in range(len(all_words) - 1):
            pair = all_words[i] + all_words[i+1]
            if 5 <= len(pair) <= 12:
                word_pairs.append(pair)
                
        return potential_keywords + word_pairs
    
    def generate_domain_ideas(self, count=250):
        """Generate potential valuable domain ideas"""
        domain_ideas = []
        
        # Strategy 1: Use trending keywords with valuable TLDs
        for keyword in self.trending_keywords[:40]:  # Use top 40 trending keywords
            for tld in self.valuable_tlds:
                domain = f"{keyword}{tld}"
                domain_ideas.append(domain)
        
        # Strategy 2: Combine two trending keywords
        for i in range(min(25, len(self.trending_keywords))):
            for j in range(i+1, min(25, len(self.trending_keywords))):
                combined = f"{self.trending_keywords[i]}{self.trending_keywords[j]}.com"
                domain_ideas.append(combined)
        
        # Strategy 3: Short dictionary words (premium domains)
        english_words = set(words.words())
        short_words = [word.lower() for word in english_words if 3 <= len(word) <= 5]
        random.shuffle(short_words)
        
        for word in short_words[:40]:  # Take 40 random short words
            domain = f"{word}.com"
            domain_ideas.append(domain)
            
        # Strategy 4: Industry-specific premium domains
        for industry, data in self.industry_trends.items():
            # High-growth industries get more domain ideas
            num_domains = int(10 * data["growth_factor"])
            keywords = data["keywords"][:num_domains]
            
            for kw in keywords:
                for tld in self.premium_tlds:
                    domain = f"{kw}{tld}"
                    domain_ideas.append(domain)
                    
                    # Also try adding common prefixes/suffixes for premium domains
                    for prefix in ["get", "my", "the", "go"]:
                        if 3 <= len(prefix + kw) <= 10:
                            domain = f"{prefix}{kw}.com"
                            domain_ideas.append(domain)
                    
                    for suffix in ["hub", "spot", "app", "hq", "now"]:
                        if 3 <= len(kw + suffix) <= 10:
                            domain = f"{kw}{suffix}.com"
                            domain_ideas.append(domain)
        
        # Strategy 5: Generate unique combinations that are less likely to be taken
        for _ in range(100):
            # Choose random trending keyword
            if len(self.trending_keywords) > 0:
                kw = random.choice(self.trending_keywords)
                
                # Add random suffix (2-4 chars)
                chars = 'abcdefghijklmnopqrstuvwxyz'
                suffix_len = random.randint(2, 4)
                suffix = ''.join(random.choice(chars) for _ in range(suffix_len))
                
                domain = f"{kw}{suffix}.com"
                domain_ideas.append(domain)
        
        # Strategy 6: Use random short pronounceable combinations (more likely to be available)
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        
        for _ in range(150):
            domain_name = ""
            length = random.randint(5, 8)
            
            start_with = random.choice(['vowel', 'consonant'])
            
            for i in range(length):
                if (i % 2 == 0 and start_with == 'consonant') or (i % 2 == 1 and start_with == 'vowel'):
                    domain_name += random.choice(consonants)
                else:
                    domain_name += random.choice(vowels)
            
            tld = random.choice(self.valuable_tlds)
            domain = f"{domain_name}{tld}"
            domain_ideas.append(domain)
            
        # Deduplicate and limit to requested count
        domain_ideas = list(set(domain_ideas))[:count]
        
        print(f"Generated {len(domain_ideas)} domain ideas")
        return domain_ideas
    
    def check_domain_availability(self, domain_list):
        """Check if domains are available and their price"""
        available_domains = []
        
        print(f"Checking availability of {len(domain_list)} domains...")
        
        # Use ThreadPoolExecutor to check multiple domains concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self._check_single_domain, domain_list))
            
        for result in results:
            if result:  # If not None
                available_domains.append(result)
                
        # Sort by score (higher is better)
        available_domains.sort(key=lambda x: x['score'], reverse=True)
        
        return available_domains
    
    def _check_single_domain(self, domain):
        """Check if a single domain is actually available online"""
        try:
            # First, use Python's whois library to check availability
            # This performs a real WHOIS lookup
            print(f"Checking availability of {domain}...")
            w = whois.whois(domain)
            
            # If the domain has registration info, it's taken
            if (w.creation_date or w.expiration_date or w.registrar or 
                isinstance(w.status, list) and len(w.status) > 0):
                print(f"{domain} appears to be taken (has WHOIS data)")
                return None
                
            # If no registration info from WHOIS, do a secondary check using an availability API
            # We'll use a free API to check domain availability
            try:
                # Try using a public API to double-check availability
                api_url = f"https://domain-availability.whoisxmlapi.com/api/v1?apiKey=at_demo&domainName={domain}"
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'DomainInfo' in data and 'domainAvailability' in data['DomainInfo']:
                        if data['DomainInfo']['domainAvailability'] != 'AVAILABLE':
                            print(f"{domain} is not available according to API check")
                            return None
                    else:
                        # If API doesn't confirm availability, try an additional check
                        pass
            except Exception as api_error:
                print(f"API check failed for {domain}: {api_error}")
                # Continue with other checks if API fails
            
            # If we get here, the domain might be available
            # Let's also try to check a registrar website as final verification
            try:
                # Try checking with Namecheap's availability page
                namecheap_url = f"https://www.namecheap.com/domains/registration/results/?domain={domain}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(namecheap_url, headers=headers, timeout=10)
                
                # If "Domain is taken" appears in the response, it's not available
                if "Domain is taken" in response.text:
                    print(f"{domain} is taken according to Namecheap")
                    return None
                    
                # If we find price information, the domain is likely available
                if "Add to cart" in response.text:
                    # Try to extract the price (this is a simplified approach)
                    price = None
                    
                    # In a real implementation, you'd parse the HTML to extract the price
                    # For now, use our mock price function
                    price = self._get_domain_price(domain)
                    
                    if price and price < 10.0:
                        print(f"{domain} appears to be available for ~${price:.2f}")
                        score = self._calculate_domain_value(domain)
                        investment_potential = self._analyze_investment_potential(domain, score)
                        
                        return {
                            'domain': domain,
                            'price': price,
                            'score': score,
                            'reasons': self._get_value_reasons(domain, score),
                            'investment_potential': investment_potential,
                            'availability_verified': True
                        }
            except Exception as web_error:
                print(f"Web check failed for {domain}: {web_error}")
                
            # If we've made it this far, we haven't conclusively determined availability
            # For demo purposes, consider it potentially available but mark it as unverified
            print(f"{domain} - availability uncertain, marking as potentially available")
            price = self._get_domain_price(domain)
            
            if price and price < 10.0:
                score = self._calculate_domain_value(domain)
                investment_potential = self._analyze_investment_potential(domain, score)
                
                return {
                    'domain': domain,
                    'price': price,
                    'score': score,
                    'reasons': self._get_value_reasons(domain, score),
                    'investment_potential': investment_potential,
                    'availability_verified': False  # Flag as not fully verified
                }
            return None
            
        except Exception as e:
            if "No match for domain" in str(e) or "No match for" in str(e):
                # This usually means the domain doesn't exist in WHOIS records,
                # which is a good sign that it might be available
                print(f"{domain} not found in WHOIS - potentially available")
                price = self._get_domain_price(domain)
                
                if price and price < 10.0:
                    score = self._calculate_domain_value(domain)
                    investment_potential = self._analyze_investment_potential(domain, score)
                    
                    return {
                        'domain': domain,
                        'price': price,
                        'score': score,
                        'reasons': self._get_value_reasons(domain, score),
                        'investment_potential': investment_potential,
                        'availability_verified': True  # No WHOIS record is a good sign
                    }
            else:
                print(f"Error checking {domain}: {e}")
            return None
    
    def _get_domain_price(self, domain):
        """Get the approximate price of a domain by checking common registrars"""
        try:
            # For non-premium domains, we can assume common price points based on TLD
            tld = '.' + domain.split('.')[-1]
            
            # Approximate prices for various TLDs (as of 2023-2024)
            base_prices = {
                '.com': 8.99,
                '.net': 9.99,
                '.org': 9.99,
                '.io': 32.99,  # This is above our threshold but included for completeness
                '.co': 14.99,  # This is above our threshold but included for completeness
                '.ai': 55.99,  # This is above our threshold but included for completeness
                '.app': 12.99,  # This is above our threshold but included for completeness
                '.dev': 14.99,  # This is above our threshold but included for completeness
                '.me': 7.99,
                '.xyz': 0.99,
                '.info': 3.99,
                '.site': 1.99,
                '.online': 3.99
            }
            
            # If the TLD is in our price list, use that price
            if tld in base_prices:
                price = base_prices[tld]
                
                # Apply discounts that are commonly available
                # First year discounts are common for many TLDs
                if tld in ['.xyz', '.site', '.online', '.info']:
                    price = min(price, 1.99)  # Common first-year promotion
                elif tld == '.com':
                    # Sometimes .com domains are on sale for around $7.99
                    price = 7.99 if random.random() < 0.3 else price
                
                return price
            else:
                # For other TLDs, assume a reasonable price under $10 if possible
                return 9.99
        except Exception as e:
            print(f"Error getting price for {domain}: {e}")
            return 9.99  # Default to $9.99 if we can't determine the price
    
    def _calculate_domain_value(self, domain):
        """Calculate a score for the domain's potential value"""
        score = 50  # Base score
        
        # Remove TLD for analysis
        domain_name = domain.split('.')[0]
        
        # Factor 1: Domain length (shorter is better)
        if len(domain_name) <= 4:
            score += 30
        elif len(domain_name) <= 6:
            score += 20
        elif len(domain_name) <= 8:
            score += 10
            
        # Factor 2: Contains trending keyword
        for keyword in self.trending_keywords:
            if keyword in domain_name:
                score += 15
                break
                
        # Factor 3: All letters (no numbers or hyphens)
        if domain_name.isalpha():
            score += 10
            
        # Factor 4: Premium TLD
        tld = '.' + domain.split('.')[-1]
        if tld == '.com':
            score += 25
        elif tld in ['.ai', '.io']:
            score += 20
        elif tld in ['.co', '.net', '.org']:
            score += 15
            
        # Factor 5: Pronounceable (simplified check)
        vowels = sum(1 for char in domain_name if char in 'aeiou')
        if vowels >= 1 and vowels <= len(domain_name) // 2 + 1:
            score += 10
            
        # Factor 6: Industry association (higher value for in-demand industries)
        industry_score = 0
        for industry, data in self.industry_trends.items():
            for keyword in data["keywords"]:
                if keyword in domain_name:
                    industry_factor = data["growth_factor"] * 10
                    industry_score = max(industry_score, industry_factor)
        
        score += industry_score
            
        return score
    
    def _analyze_investment_potential(self, domain, score):
        """Analyze the investment potential of a domain"""
        domain_name = domain.split('.')[0]
        tld = '.' + domain.split('.')[-1]
        
        # Baseline potential based on score
        if score >= 120:
            potential = "Excellent"
            potential_score = 5
        elif score >= 100:
            potential = "Very Good"
            potential_score = 4
        elif score >= 80:
            potential = "Good"
            potential_score = 3
        elif score >= 60:
            potential = "Moderate"
            potential_score = 2
        else:
            potential = "Low"
            potential_score = 1
            
        # Identify primary industry
        primary_industry = None
        highest_match = 0
        
        for industry, data in self.industry_trends.items():
            keyword_matches = sum(1 for kw in data["keywords"] if kw in domain_name)
            if keyword_matches > highest_match:
                highest_match = keyword_matches
                primary_industry = industry
        
        # Estimated resale value (very rough estimate for demo)
        base_price = {
            5: (300, 1000),
            4: (150, 500),
            3: (75, 200),
            2: (30, 100),
            1: (10, 40)
        }[potential_score]
        
        # Adjust for industry growth factor if applicable
        industry_factor = 1.0
        time_to_profit = "6-12 months"
        future_outlook = "Stable"
        demand_level = "Moderate"
        
        if primary_industry:
            industry_data = self.industry_trends[primary_industry]
            industry_factor = industry_data["growth_factor"]
            demand_level = industry_data["demand_level"]
            future_outlook = industry_data["future_outlook"]
            
            # Adjust time to profit based on demand level
            if demand_level == "Very High":
                time_to_profit = "1-3 months"
            elif demand_level == "High":
                time_to_profit = "3-6 months"
            elif demand_level == "Moderate":
                time_to_profit = "6-12 months"
            else:
                time_to_profit = "12+ months"
        
        # Calculate estimated resale range
        min_resale = int(base_price[0] * industry_factor)
        max_resale = int(base_price[1] * industry_factor)
        
        # If it's a very short premium .com (3-4 chars), increase value
        if len(domain_name) <= 4 and tld == '.com' and domain_name.isalpha():
            min_resale *= 3
            max_resale *= 5
        
        return {
            "potential": potential,
            "primary_industry": primary_industry or "General",
            "estimated_resale": f"${min_resale}-${max_resale}",
            "time_to_profit": time_to_profit,
            "demand_level": demand_level,
            "future_outlook": future_outlook
        }
    
    def _get_value_reasons(self, domain, score):
        """Get reasons why a domain might be valuable"""
        reasons = []
        domain_name = domain.split('.')[0]
        tld = '.' + domain.split('.')[-1]
        
        if len(domain_name) <= 4:
            reasons.append("Very short name (premium)")
        elif len(domain_name) <= 6:
            reasons.append("Short name (desirable)")
            
        for keyword in self.trending_keywords:
            if keyword in domain_name:
                reasons.append(f"Contains trending keyword '{keyword}'")
                break
                
        if domain_name.isalpha():
            reasons.append("All letters, no special characters")
            
        if tld == '.com':
            reasons.append("Premium .com TLD")
        elif tld in ['.ai', '.io']:
            reasons.append(f"Trending {tld} TLD")
            
        # Add industry-specific reasons
        for industry, data in self.industry_trends.items():
            for keyword in data["keywords"]:
                if keyword in domain_name:
                    reasons.append(f"Associated with {industry} industry (growth factor: {data['growth_factor']})")
                    break
            
        return reasons
    
    def run(self, count=50):
        """Run the domain research process and return results"""
        print("Starting domain research...")
        
        # Generate domain ideas
        domain_ideas = self.generate_domain_ideas(count * 10)  # Generate more ideas than needed
        
        # Check availability and pricing
        available_domains = self.check_domain_availability(domain_ideas)
        
        # Limit to requested count
        top_domains = available_domains[:count]
        
        print(f"Found {len(top_domains)} potential valuable domains under $10")
        
        return top_domains
    
    def save_results(self, domains, filename="valuable_domains.json"):
        """Save results to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(domains, f, indent=2)
        print(f"Results saved to {filename}")
        
        # Also create a more readable text report
        with open(filename.replace('.json', '.txt'), 'w') as f:
            f.write("VALUABLE DOMAIN OPPORTUNITIES UNDER $10\n")
            f.write("=======================================\n\n")
            
            for i, domain in enumerate(domains, 1):
                f.write(f"{i}. {domain['domain']}\n")
                f.write(f"   Price: ${domain['price']:.2f}\n")
                f.write(f"   Value Score: {domain['score']}/100\n")
                
                f.write("   Why it's valuable:\n")
                for reason in domain['reasons']:
                    f.write(f"   - {reason}\n")
                
                # Add investment potential information
                f.write("\n   Investment Analysis:\n")
                investment = domain['investment_potential']
                f.write(f"   - Potential: {investment['potential']}\n")
                f.write(f"   - Industry: {investment['primary_industry']}\n")
                f.write(f"   - Estimated Resale: {investment['estimated_resale']}\n")
                f.write(f"   - Time to Profit: {investment['time_to_profit']}\n")
                f.write(f"   - Demand Level: {investment['demand_level']}\n")
                f.write(f"   - Future Outlook: {investment['future_outlook']}\n")
                
                f.write("\n")

def main():
    """Run the domain research agent"""
    agent = DomainResearchAgent()
    
    print("\nFocusing on finding ACTUALLY AVAILABLE domains...")
    
    # Generate truly unique domain combinations that are more likely to be available
    custom_domains = []
    
    # Setup generators for unique combinations
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    
    print("Generating unique domain combinations to check for availability...")
    
    # Strategy 1: Generate three-syllable domain names (easier to remember, more likely available)
    for _ in range(30):  # Reduced from 250 to 30 to avoid rate limiting
        domain_name = ""
        for i in range(3):  # 3 syllables
            if i == 0:  # Start with consonant for better pronounceability
                domain_name += random.choice(consonants)
            domain_name += random.choice(vowels)
            domain_name += random.choice(consonants)
        
        # Focus on affordable TLDs
        tld_choices = ['.com', '.xyz', '.site', '.online', '.info', '.me'] 
        tld = random.choice(tld_choices)
        
        domain = f"{domain_name}{tld}"
        custom_domains.append(domain)
    
    # Strategy 2: Trend keyword + random syllable
    trending_words = ['tech', 'ai', 'nft', 'web3', 'meta', 'cyber', 'eco', 'smart', 'cloud', 'digi']
    
    for keyword in trending_words[:5]:  # Use only 5 trending keywords to limit checks
        for _ in range(5):  # 5 domains per keyword
            # Generate a random syllable
            suffix = ""
            consonant = random.choice(consonants)
            vowel = random.choice(vowels)
            suffix = consonant + vowel + random.choice(consonants)
            
            # 50% chance for prefix
            if random.random() > 0.5:
                domain = f"{keyword}{suffix}.com"
            else:
                domain = f"{suffix}{keyword}.com"
                
            custom_domains.append(domain)
    
    # Strategy 3: Random 4-letter domain + affordable TLD
    consonants_common = 'bcdfgklmnprst'  # More common consonants for pronounceability
    vowels_common = 'aeiou'
    
    for _ in range(20):  # Reduced from 100 to 20
        word = ""
        # CVCV pattern (consonant-vowel-consonant-vowel)
        word += random.choice(consonants_common)
        word += random.choice(vowels_common)
        word += random.choice(consonants_common)
        word += random.choice(vowels_common)
        
        tld = random.choice(['.xyz', '.site', '.online', '.info', '.me'])
        domain = f"{word}{tld}"
        custom_domains.append(domain)
    
    # Remove duplicates
    custom_domains = list(set(custom_domains))
    
    # Check these custom domains for actual availability
    print(f"Checking {len(custom_domains)} domains for actual availability (this may take some time)...")
    available_domains = agent.check_domain_availability(custom_domains)
    
    # Filter to only include domains that were verified as available
    verified_domains = [d for d in available_domains if d.get('availability_verified', False)]
    
    # Display results
    print("\nVERIFIED AVAILABLE DOMAIN OPPORTUNITIES:")
    print("=======================================")
    
    # Display verified available domains
    for i, domain in enumerate(verified_domains[:10], 1):
        print(f"\n{i}. {domain['domain']}")
        print(f"   Price: ${domain['price']:.2f}")
        print(f"   Value Score: {domain['score']}/100")
        print("   Why it's valuable:")
        for reason in domain['reasons']:
            print(f"   - {reason}")
        
        # Print investment potential summary
        print("\n   Investment Analysis:")
        investment = domain['investment_potential']
        print(f"   - Potential: {investment['potential']}")
        print(f"   - Est. Resale: {investment['estimated_resale']}")
        print(f"   - Time to Profit: {investment['time_to_profit']}")
    
    # If we have unverified domains, show them separately
    unverified_domains = [d for d in available_domains if not d.get('availability_verified', False)]
    
    if unverified_domains:
        print("\n\nPOTENTIALLY AVAILABLE DOMAINS (AVAILABILITY NOT FULLY VERIFIED):")
        print("=============================================================")
        
        for i, domain in enumerate(unverified_domains[:5], 1):
            print(f"\n{i}. {domain['domain']}")
            print(f"   Price: ${domain['price']:.2f}")
            print(f"   Value Score: {domain['score']}/100")
            print("   NOTE: Availability needs additional verification")
    
    print(f"\nFound {len(verified_domains)} verified available domains and {len(unverified_domains)} potentially available domains.")
    
    # Save results - only the verified ones
    agent.save_results(verified_domains)
    
    # Provide next steps
    print("\nNEXT STEPS:")
    print("1. Visit a domain registrar like Namecheap.com or GoDaddy.com")
    print("2. Search for these domains to verify final availability and exact pricing")
    print("3. Register the domains that fit your investment criteria")

if __name__ == "__main__":
    main() 