import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import csv
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditStage(Enum):
    FOUNDATION = "Foundation"
    BUILDING = "Building"
    SCALING = "Scaling"
    ADVANCED = "Advanced"

@dataclass
class BusinessInfo:
    legal_name: str
    dba_name: str = None
    entity_type: str = None
    ein: str = None
    years_in_business: float = 0
    industry: str = None
    annual_revenue: float = 0
    has_business_bank_account: bool = False
    has_business_address: bool = False
    has_business_phone: bool = False
    has_business_website: bool = False
    has_duns_number: bool = False

@dataclass
class CreditStep:
    name: str
    description: str
    priority: int
    stage: CreditStage
    estimated_time: str
    requirements: List[str]
    completed: bool = False
    completion_date: datetime = None

class BusinessCreditAgent:
    def __init__(self):
        self.business_info = None
        self.current_stage = CreditStage.FOUNDATION
        self.credit_steps = self._initialize_credit_steps()
        
    def _initialize_credit_steps(self) -> List[CreditStep]:
        """Initialize all credit building steps"""
        return [
            # Foundation Stage
            CreditStep(
                name="Register Business Entity",
                description="Register your business as an LLC, Corporation, or other legal entity",
                priority=1,
                stage=CreditStage.FOUNDATION,
                estimated_time="1-2 weeks",
                requirements=["Business name", "State filing fee", "Business address"]
            ),
            CreditStep(
                name="Obtain EIN",
                description="Get your Employer Identification Number from the IRS",
                priority=1,
                stage=CreditStage.FOUNDATION,
                estimated_time="1-2 days",
                requirements=["Legal business name", "Business type", "SSN of owner"]
            ),
            CreditStep(
                name="Open Business Bank Account",
                description="Open a dedicated business checking account",
                priority=1,
                stage=CreditStage.FOUNDATION,
                estimated_time="1 day",
                requirements=["EIN", "Business registration documents", "Initial deposit"]
            ),
            CreditStep(
                name="Get DUNS Number",
                description="Register for a free D-U-N-S Number from Dun & Bradstreet",
                priority=1,
                stage=CreditStage.FOUNDATION,
                estimated_time="1-2 weeks",
                requirements=["Business name", "Business address", "Phone number"]
            ),
            
            # Building Stage
            CreditStep(
                name="Set Up Business Credit File",
                description="Establish credit files with major business credit bureaus",
                priority=2,
                stage=CreditStage.BUILDING,
                estimated_time="1-2 weeks",
                requirements=["DUNS number", "Business information"]
            ),
            CreditStep(
                name="Apply for Net 30 Accounts",
                description="Open accounts with net-30 vendors that report to credit bureaus",
                priority=2,
                stage=CreditStage.BUILDING,
                estimated_time="1-2 weeks",
                requirements=["Business bank account", "EIN", "DUNS number"]
            ),
            CreditStep(
                name="Get Business Phone & Website",
                description="Set up a dedicated business phone line and professional website",
                priority=2,
                stage=CreditStage.BUILDING,
                estimated_time="1 week",
                requirements=["Business address", "Funding for setup"]
            ),
            
            # Scaling Stage
            CreditStep(
                name="Apply for Business Credit Card",
                description="Apply for a small business credit card that reports to bureaus",
                priority=3,
                stage=CreditStage.SCALING,
                estimated_time="1-2 weeks",
                requirements=["6+ months business history", "Good payment history", "Revenue"]
            ),
            CreditStep(
                name="Establish Trade Lines",
                description="Set up vendor trade lines and maintain positive payment history",
                priority=3,
                stage=CreditStage.SCALING,
                estimated_time="3-6 months",
                requirements=["Business credit file", "Active business operations"]
            ),
            
            # Advanced Stage
            CreditStep(
                name="Monitor Credit Reports",
                description="Regularly monitor and maintain business credit reports",
                priority=4,
                stage=CreditStage.ADVANCED,
                estimated_time="Ongoing",
                requirements=["Active credit accounts", "Credit monitoring service"]
            ),
            CreditStep(
                name="Apply for Credit Line Increase",
                description="Request credit line increases on existing accounts",
                priority=4,
                stage=CreditStage.ADVANCED,
                estimated_time="Ongoing",
                requirements=["12+ months good payment history", "Increased revenue"]
            )
        ]

    def set_business_info(self, info: BusinessInfo):
        """Set or update business information"""
        self.business_info = info
        logger.info(f"Updated business information for {info.legal_name}")

    def get_current_stage_steps(self) -> List[CreditStep]:
        """Get steps for current credit building stage"""
        return [step for step in self.credit_steps if step.stage == self.current_stage]

    def get_next_steps(self, limit: int = 3) -> List[CreditStep]:
        """Get next incomplete steps across all stages"""
        incomplete_steps = [step for step in self.credit_steps if not step.completed]
        return sorted(incomplete_steps, key=lambda x: x.priority)[:limit]

    def mark_step_complete(self, step_name: str):
        """Mark a credit building step as complete"""
        for step in self.credit_steps:
            if step.name == step_name:
                step.completed = True
                step.completion_date = datetime.now()
                logger.info(f"Marked step '{step_name}' as complete")
                self._check_stage_progression()
                break

    def _check_stage_progression(self):
        """Check if we can progress to next stage"""
        current_stage_steps = self.get_current_stage_steps()
        if all(step.completed for step in current_stage_steps):
            if self.current_stage == CreditStage.FOUNDATION:
                self.current_stage = CreditStage.BUILDING
            elif self.current_stage == CreditStage.BUILDING:
                self.current_stage = CreditStage.SCALING
            elif self.current_stage == CreditStage.SCALING:
                self.current_stage = CreditStage.ADVANCED
            logger.info(f"Progressed to {self.current_stage.value} stage")

    def get_vendor_recommendations(self) -> List[Dict]:
        """Get recommended vendors based on current stage"""
        vendors = {
            CreditStage.FOUNDATION: [
                {
                    "name": "Uline",
                    "website": "https://www.uline.com",
                    "terms": "Net 30",
                    "requirements": ["Business entity", "EIN"]
                },
                {
                    "name": "Grainger",
                    "website": "https://www.grainger.com",
                    "terms": "Net 30",
                    "requirements": ["Business entity", "EIN", "D&B number"]
                }
            ],
            CreditStage.BUILDING: [
                {
                    "name": "Quill",
                    "website": "https://www.quill.com",
                    "terms": "Net 30",
                    "requirements": ["Business entity", "EIN"]
                },
                {
                    "name": "Crown Office Supplies",
                    "website": "https://www.crownofficefurniture.com",
                    "terms": "Net 30",
                    "requirements": ["Business entity", "EIN"]
                }
            ]
        }
        return vendors.get(self.current_stage, [])

    def generate_credit_building_plan(self) -> str:
        """Generate a detailed credit building plan"""
        if not self.business_info:
            return "Please set business information first."

        plan = f"Business Credit Building Plan for {self.business_info.legal_name}\n"
        plan += f"Current Stage: {self.current_stage.value}\n\n"

        plan += "Next Steps:\n"
        for step in self.get_next_steps():
            plan += f"\n{step.name}\n"
            plan += f"Description: {step.description}\n"
            plan += f"Estimated Time: {step.estimated_time}\n"
            plan += "Requirements:\n"
            for req in step.requirements:
                plan += f"- {req}\n"
            plan += "\n"

        if self.current_stage in [CreditStage.FOUNDATION, CreditStage.BUILDING]:
            plan += "\nRecommended Vendors:\n"
            for vendor in self.get_vendor_recommendations():
                plan += f"\n{vendor['name']}\n"
                plan += f"Website: {vendor['website']}\n"
                plan += f"Terms: {vendor['terms']}\n"
                plan += "Requirements:\n"
                for req in vendor['requirements']:
                    plan += f"- {req}\n"

        return plan

    def export_progress_report(self):
        """Export progress report to CSV"""
        filename = "business_credit_progress.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Stage", "Status", "Completion Date"])
            
            for step in self.credit_steps:
                writer.writerow([
                    step.name,
                    step.stage.value,
                    "Completed" if step.completed else "Pending",
                    step.completion_date.strftime("%Y-%m-%d") if step.completion_date else "N/A"
                ])
        logger.info(f"Progress report exported to {filename}")

def main():
    # Create the agent
    agent = BusinessCreditAgent()
    
    # Set business information
    business_info = BusinessInfo(
        legal_name="Jordan German Salon, LLC",
        entity_type="LLC (Dissolved)",
        industry="Beauty/Salon",
        years_in_business=8,
        has_business_bank_account=False,  # Need to verify
        has_business_address=True,
        has_business_phone=False,  # Need to verify
        has_business_website=False,  # Need to verify
        has_duns_number=True,
        ein=None  # Need to verify
    )
    agent.set_business_info(business_info)
    
    # Generate and print credit building plan
    plan = agent.generate_credit_building_plan()
    print(plan)
    
    # Export progress report
    agent.export_progress_report()

if __name__ == "__main__":
    main() 