import os
import aiohttp
import whois
import dns.resolver
from typing import Dict, Optional
from datetime import datetime
import shodan
from fullcontact import FullContact # type: ignore
from truecallerpy import search_phonenumber

# Initialize API clients
shodan_api = shodan.Shodan(os.getenv("SHODAN_API_KEY"))
fullcontact_api = FullContact(os.getenv("FULLCONTACT_API_KEY"))

async def search_people(query: str, options: Optional[Dict] = None) -> Dict:
    """
    Search for information about a person using various OSINT sources
    """
    results = {
        "basic_info": {},
        "social_media": {},
        "professional": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Basic information from FullContact
        if options and options.get("fullcontact"):
            person_data = await fullcontact_api.person.enrich(query)
            results["basic_info"] = person_data
            
        # Additional sources can be added here
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

async def search_phone(query: str, options: Optional[Dict] = None) -> Dict:
    """
    Search for information about a phone number
    """
    results = {
        "basic_info": {},
        "carrier": {},
        "location": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Basic information from TrueCaller
        if options and options.get("truecaller"):
            phone_data = await search_phonenumber(query)
            results["basic_info"] = phone_data
            
        # Additional sources can be added here
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

async def search_domain(query: str, options: Optional[Dict] = None) -> Dict:
    """
    Search for information about a domain
    """
    results = {
        "whois": {},
        "dns": {},
        "security": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # WHOIS information
        if options and options.get("whois"):
            w = whois.whois(query)
            results["whois"] = {
                "registrar": w.registrar,
                "creation_date": w.creation_date,
                "expiration_date": w.expiration_date,
                "name_servers": w.name_servers
            }
        
        # DNS information
        if options and options.get("dns"):
            dns_results = {}
            for record_type in ['A', 'MX', 'NS', 'TXT']:
                try:
                    answers = dns.resolver.resolve(query, record_type)
                    dns_results[record_type] = [str(rdata) for rdata in answers]
                except dns.resolver.NoAnswer:
                    dns_results[record_type] = []
            results["dns"] = dns_results
            
        # Security information from Shodan
        if options and options.get("shodan"):
            shodan_results = shodan_api.host(query)
            results["security"] = {
                "ports": shodan_results.get("ports", []),
                "vulns": shodan_results.get("vulns", []),
                "hostnames": shodan_results.get("hostnames", [])
            }
            
    except Exception as e:
        results["error"] = str(e)
    
    return results

async def enrich_domain(query: str, options: Optional[Dict] = None) -> Dict:
    """
    Enrich domain information with additional data
    """
    results = {
        "ssl": {},
        "technologies": {},
        "subdomains": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # SSL information
        if options and options.get("ssl"):
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{query}") as response:
                    cert = response.connection.transport.get_extra_info('socket').getpeercert()
                    results["ssl"] = {
                        "issuer": dict(x[0] for x in cert['issuer']),
                        "expiry": datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z').isoformat()
                    }
        
        # Technology stack detection
        if options and options.get("technologies"):
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{query}") as response:
                    headers = response.headers
                    results["technologies"] = {
                        "server": headers.get("Server"),
                        "powered_by": headers.get("X-Powered-By"),
                        "framework": headers.get("X-Framework")
                    }
        
        # Subdomain enumeration
        if options and options.get("subdomains"):
            # This would typically use a subdomain enumeration tool
            # For now, we'll just return a placeholder
            results["subdomains"] = {
                "common": ["www", "mail", "ftp", "admin"],
                "status": "placeholder"
            }
            
    except Exception as e:
        results["error"] = str(e)
    
    return results 