# -*- coding: utf-8 -*-
import re
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
from .phoneinfoga_wrapper import PhoneInfogaWrapper
import random

load_dotenv()

class PhoneScanner:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.phoneinfoga = PhoneInfogaWrapper()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scan_number(self, phone_number: str) -> Dict[str, Any]:
        """Scan phone number primarily using PhoneInfoga"""
        try:
            # Clean phone number format
            if not phone_number.startswith('+'):
                if phone_number.startswith('1'):
                    phone_number = '+' + phone_number
                else:
                    phone_number = '+1' + phone_number
            
            # Get results from PhoneInfoga
            phoneinfoga_result = await self.phoneinfoga.scan_number(phone_number)
            
            if not phoneinfoga_result or "error" in phoneinfoga_result:
                return {
                    "success": False,
                    "error": phoneinfoga_result.get("error", "Failed to scan phone number"),
                    "scan_results": {
                        "metadata": {
                            "number_type": "Unknown",
                            "area_code": "Unknown",
                            "is_toll_free": False,
                            "is_voip": False
                        }
                    }
                }
            
            # If successful, the phoneinfoga_result should contain all necessary data
            # Pass it directly to the template
            return {
                "success": True,
                "scan_results": phoneinfoga_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error scanning phone number: {str(e)}"
            }

    def _clean_number(self, number: str) -> str:
        """Clean and format phone number"""
        cleaned = re.sub(r'[^\d+]', '', number)
        if not cleaned.startswith('+'):
            cleaned = '+1' + cleaned  # Default to US format
        return cleaned

    def _get_line_type(self, parsed_number: phonenumbers.PhoneNumber) -> str:
        """Determine the type of phone line"""
        try:
            if phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE:
                return "Mobile"
            elif phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.FIXED_LINE:
                return "Landline"
            elif phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.VOIP:
                return "VoIP"
            else:
                return "Unknown"
        except:
            return "Unknown"

    async def _scan_numverify(self, session: aiohttp.ClientSession, number: str) -> Dict[str, Any]:
        """Scan using NumVerify API"""
        try:
            # Remove the '+' for the API request
            clean_number = number.replace('+', '')
            
            # This would typically use the NumVerify API
            # For demo, returning placeholder data
            return {
                'valid': True,
                'line_type': self._get_line_type(phonenumbers.parse(number)),
                'carrier': carrier.name_for_number(phonenumbers.parse(number), "en") or "Unknown",
                'location': geocoder.description_for_number(phonenumbers.parse(number), "en") or "Unknown"
            }
        except Exception:
            return {
                'valid': False,
                'error': 'Unable to verify number'
            }

    async def _scan_owner_info(self, session: aiohttp.ClientSession, number: str) -> Dict[str, Any]:
        """Scan for owner information"""
        clean_number = number.replace('+1', '').replace('-', '')
        owner_info = {
            'possible_names': [],
            'possible_addresses': [],
            'age_range': None,
            'email_addresses': [],
            'associated_numbers': []
        }

        # Search various people search engines
        for search_url in self.search_engines:
            try:
                formatted_url = search_url.format(number=clean_number)
                async with session.get(formatted_url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Extract information from the response
                        # This is a simplified example - in reality, you'd need to parse the HTML properly
                        soup = BeautifulSoup(text, 'html.parser')
                        
                        # Look for common patterns in people search sites
                        names = soup.find_all(class_=re.compile(r'name|person|owner|subscriber'))
                        addresses = soup.find_all(class_=re.compile(r'address|location|residence'))
                        emails = soup.find_all(class_=re.compile(r'email|contact'))
                        
                        for name in names:
                            if name.text.strip() and len(name.text.strip()) > 5:
                                owner_info['possible_names'].append(name.text.strip())
                        
                        for addr in addresses:
                            if addr.text.strip() and len(addr.text.strip()) > 10:
                                owner_info['possible_addresses'].append(addr.text.strip())
                        
                        for email in emails:
                            if email.text.strip() and '@' in email.text:
                                owner_info['email_addresses'].append(email.text.strip())
                                
            except Exception:
                continue

        # Remove duplicates
        owner_info['possible_names'] = list(set(owner_info['possible_names']))
        owner_info['possible_addresses'] = list(set(owner_info['possible_addresses']))
        owner_info['email_addresses'] = list(set(owner_info['email_addresses']))

        return owner_info

    async def _scan_social_media(self, session: aiohttp.ClientSession, number: str) -> Dict[str, List[str]]:
        """Search for social media profiles"""
        clean_number = number.replace('+1', '').replace('-', '')
        platforms = {
            'facebook': f'https://www.facebook.com/search/top/?q={clean_number}',
            'linkedin': f'https://www.linkedin.com/search/results/all/?keywords={clean_number}',
            'twitter': f'https://twitter.com/search?q={clean_number}',
            'instagram': f'https://www.instagram.com/explore/tags/{clean_number}/',
            'tiktok': f'https://www.tiktok.com/search?q={clean_number}',
            'telegram': f'https://t.me/{clean_number}'
        }
        
        profiles = []
        for platform, url in platforms.items():
            try:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    if response.status == 200:
                        profiles.append({
                            'platform': platform,
                            'url': url,
                            'found': True
                        })
            except Exception:
                continue

        return {'profiles': profiles}

    async def _scan_data_breaches(self, session: aiohttp.ClientSession, number: str) -> Dict[str, Any]:
        """Check for the number in known data breaches"""
        # This would typically integrate with breach databases
        # For demo purposes, returning placeholder data
        return {
            'breaches_found': 0,
            'last_breach': None,
            'exposed_data_types': [],
            'breach_details': []
        }

    async def _check_reputation(self, phone_number: str) -> Dict[str, Any]:
        """Check reputation databases for the phone number"""
        # In a real implementation, this would query reputation databases
        # For the demo, we'll generate some plausible data
        risk_level = random.choice(["Low", "Medium", "High"])
        fraud_reports = random.randint(0, 5) if risk_level != "Low" else 0
        spam_reports = random.randint(0, 10) if risk_level != "Low" else 0
        
        return {
            "spam_risk": risk_level,
            "fraud_reports": fraud_reports,
            "spam_reports": spam_reports,
            "reported_as_spam": spam_reports > 0,
            "reported_as_fraud": fraud_reports > 0,
            "spam_categories": random.sample(["Telemarketing", "Scam", "Robocall", "Political", "Charity"], 
                                            k=min(2, 1 if risk_level == "Low" else 2)),
            "last_reported": "2023-12-01" if spam_reports > 0 or fraud_reports > 0 else None,
            "confidence": random.choice(["Low", "Medium", "High"])
        }

    async def _get_owner_info(self, phone_number: str) -> Dict[str, Any]:
        """Get detailed owner information"""
        # In a real implementation, this would query people search databases
        # For the demo, we'll generate some plausible data
        owner_types = ["Individual", "Business"]
        owner_type = random.choice(owner_types)
        
        if owner_type == "Individual":
            # Generate plausible individual owner data
            genders = ["Male", "Female"]
            age_ranges = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
            
            possible_cities = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", 
                              "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA"]
            
            owner_data = {
                "type": "Individual",
                "name": "Name withheld for privacy",  # In a real implementation, this would be the actual name
                "age_range": random.choice(age_ranges),
                "gender": random.choice(genders),
                "possible_locations": random.sample(possible_cities, k=min(3, random.randint(1, 3))),
                "possible_relatives": random.randint(0, 5),
                "education": random.choice(["High School", "Some College", "Bachelor's Degree", "Master's Degree", None]),
                "occupation": random.choice(["Professional", "Service", "Student", "Retired", None]),
                "public_records": {
                    "property_records": random.choice([True, False]),
                    "court_records": random.choice([True, False]),
                    "bankruptcy_filings": random.choice([True, False]),
                    "marriage_records": random.choice([True, False]),
                    "voter_registration": random.choice([True, False])
                }
            }
        else:
            # Generate plausible business owner data
            business_types = ["Retail", "Service", "Healthcare", "Technology", "Finance", "Education", "Manufacturing"]
            business_sizes = ["Small", "Medium", "Large", "Enterprise"]
            
            owner_data = {
                "type": "Business",
                "business_name": "Name withheld for privacy",  # In a real implementation, this would be the actual name
                "industry": random.choice(business_types),
                "size": random.choice(business_sizes),
                "year_established": random.randint(1980, 2023),
                "business_records": {
                    "bbb_rating": random.choice(["A+", "A", "A-", "B+", "B", "B-", "C+", "C", None]),
                    "is_publicly_traded": random.choice([True, False]),
                    "has_website": random.choice([True, False]),
                    "customer_reviews": random.randint(0, 1000),
                    "average_rating": round(random.uniform(2.5, 5.0), 1)
                }
            }
            
        return owner_data
    
    async def _check_social_media(self, phone_number: str) -> Dict[str, Any]:
        """Check for social media accounts linked to the phone number"""
        # In a real implementation, this would query social media platforms
        # For the demo, we'll generate some plausible data
        all_platforms = ["Facebook", "Twitter", "LinkedIn", "Instagram", "TikTok", "Pinterest", "Snapchat", "Reddit", "YouTube"]
        professional_platforms = ["LinkedIn", "GitHub", "Stack Overflow", "Quora", "Medium"]
        
        # Randomly select some platforms where the number might be found
        found_count = random.randint(0, 5)
        found_platforms = random.sample(all_platforms, k=min(found_count, len(all_platforms)))
        
        # Randomly select some professional platforms
        prof_found_count = random.randint(0, 2)
        found_prof_platforms = random.sample(professional_platforms, k=min(prof_found_count, len(professional_platforms)))
        
        # Generate platform-specific data
        platform_data = {}
        for platform in found_platforms:
            platform_data[platform] = {
                "associated": True,
                "profile_name": f"Username withheld for privacy",  # In a real implementation, this would be the actual username
                "last_active": random.choice(["Recently", "Within month", "Within year", "Inactive", None]),
                "account_type": random.choice(["Personal", "Business", "Unknown"]),
                "public": random.choice([True, False]),
                "followers": random.randint(0, 5000) if random.choice([True, False]) else None
            }
        
        for platform in found_prof_platforms:
            platform_data[platform] = {
                "associated": True,
                "profile_name": f"Username withheld for privacy",  # In a real implementation, this would be the actual username
                "last_active": random.choice(["Recently", "Within month", "Within year", "Inactive", None]),
                "account_type": "Professional",
                "public": random.choice([True, False]),
                "connections": random.randint(0, 1000) if random.choice([True, False]) else None
            }
        
        # Generate some search patterns for each platform
        search_patterns = {
            platform: f"site:{platform.lower()}.com {phone_number}" 
            for platform in found_platforms + found_prof_platforms
        }
        
        return {
            "platforms_found": list(platform_data.keys()),
            "total_platforms_checked": len(all_platforms) + len(professional_platforms),
            "platform_data": platform_data,
            "search_patterns": search_patterns,
            "online_presence_score": random.randint(1, 10),
            "privacy_risk": random.choice(["Low", "Medium", "High"])
        } 