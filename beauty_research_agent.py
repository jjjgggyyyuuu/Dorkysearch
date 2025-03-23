import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import csv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BeautyCompany:
    name: str
    website: str
    payment_terms: List[str]
    contact_info: str
    products: List[str]
    verified: bool
    last_updated: datetime

class BeautyResearchAgent:
    def __init__(self):
        self.companies: List[BeautyCompany] = []
        # List of major beauty supply directories and wholesalers
        self.target_sites = [
            "https://www.beautysupplylist.com",
            "https://www.cosmeticindex.com",
            "https://www.beautyindustrydirectory.com",
            "https://www.wholesalecentral.com/Beauty_and_Personal_Care_Supplies/",
            "https://www.beautyproductwholesalers.com"
        ]
        
        # Known wholesalers with net terms/COD
        self.known_wholesalers = [
            {
                "name": "Beauty Express",
                "url": "https://www.beautyexpress.com",
                "terms": ["Net 30", "COD"]
            },
            {
                "name": "CosmoProf",
                "url": "https://www.cosmoprofbeauty.com",
                "terms": ["Net 30", "Net 60"]
            },
            {
                "name": "State Beauty Supply",
                "url": "https://www.statebeauty.com",
                "terms": ["Net Terms", "COD"]
            }
        ]

    async def scrape_website(self, url: str) -> Dict:
        """Scrape website for company information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract company info
                        company_info = {
                            "name": self._extract_company_name(soup),
                            "website": url,
                            "payment_terms": self._extract_payment_terms(soup),
                            "contact": self._extract_contact_info(soup),
                            "products": self._extract_products(soup)
                        }
                        return company_info
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
        return None

    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """Extract company name from website"""
        title = soup.find('title')
        if title:
            return title.text.split('|')[0].strip()
        return "Unknown Company"

    def _extract_payment_terms(self, soup: BeautifulSoup) -> List[str]:
        """Extract payment terms from website"""
        terms = []
        terms_keywords = ['payment terms', 'net terms', 'cod', 'payment options']
        for keyword in terms_keywords:
            elements = soup.find_all(text=lambda text: keyword.lower() in text.lower() if text else False)
            for element in elements:
                terms.append(element.strip())
        return list(set(terms))

    def _extract_contact_info(self, soup: BeautifulSoup) -> str:
        """Extract contact information"""
        contact_info = []
        contact_elements = soup.find_all(['a', 'p'], text=lambda text: 'contact' in text.lower() if text else False)
        for element in contact_elements[:1]:  # Just get the first contact info
            contact_info.append(element.get_text().strip())
        return ' '.join(contact_info) if contact_info else "Contact information not found"

    def _extract_products(self, soup: BeautifulSoup) -> List[str]:
        """Extract product categories"""
        products = []
        product_elements = soup.find_all(['a', 'h2', 'h3'], text=lambda text: any(keyword in text.lower() for keyword in ['product', 'category', 'collection']) if text else False)
        for element in product_elements[:5]:  # Limit to 5 product categories
            products.append(element.get_text().strip())
        return products

    async def research(self) -> List[BeautyCompany]:
        """Main research function"""
        results = []
        
        # First, add known wholesalers
        for wholesaler in self.known_wholesalers:
            company = BeautyCompany(
                name=wholesaler["name"],
                website=wholesaler["url"],
                payment_terms=wholesaler["terms"],
                contact_info="Contact via website",
                products=[],
                verified=True,
                last_updated=datetime.now()
            )
            results.append(company)
            logger.info(f"Added known wholesaler: {wholesaler['name']}")

        # Then scrape additional companies
        for site in self.target_sites:
            try:
                company_data = await self.scrape_website(site)
                if company_data and company_data.get("payment_terms"):
                    company = BeautyCompany(
                        name=company_data["name"],
                        website=company_data["website"],
                        payment_terms=company_data["payment_terms"],
                        contact_info=company_data["contact"],
                        products=company_data["products"],
                        verified=False,
                        last_updated=datetime.now()
                    )
                    results.append(company)
                    logger.info(f"Found company with payment terms: {company.name}")
            except Exception as e:
                logger.error(f"Error processing {site}: {str(e)}")

        self.companies = results
        return results

    def export_results(self) -> None:
        """Export results to CSV"""
        filename = "beauty_companies_results.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Company Name", "Website", "Payment Terms", "Contact Info", "Products", "Verified"])
            
            for company in self.companies:
                writer.writerow([
                    company.name,
                    company.website,
                    ", ".join(company.payment_terms),
                    company.contact_info,
                    ", ".join(company.products),
                    "✓" if company.verified else "✗"
                ])
        logger.info(f"Results exported to {filename}")

async def main():
    agent = BeautyResearchAgent()
    companies = await agent.research()
    
    print("\nFound Beauty Companies with Net Terms/COD:")
    print("==========================================")
    
    for company in companies:
        print(f"\nCompany: {company.name}")
        print(f"Website: {company.website}")
        print(f"Payment Terms: {', '.join(company.payment_terms)}")
        print(f"Contact: {company.contact_info}")
        print(f"Products: {', '.join(company.products)}")
        print(f"Verified: {'✓' if company.verified else '✗'}")
        print("-" * 50)

    # Export results
    agent.export_results()
    print(f"\nResults have been exported to beauty_companies_results.csv")

if __name__ == "__main__":
    asyncio.run(main()) 