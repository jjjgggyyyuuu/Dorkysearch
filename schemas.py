from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Subscription schemas
class SubscriptionBase(BaseModel):
    plan_type: str
    status: str

class SubscriptionCreate(SubscriptionBase):
    user_id: int
    stripe_customer_id: str
    stripe_subscription_id: str
    current_period_start: datetime
    current_period_end: datetime

class Subscription(SubscriptionBase):
    id: int
    user_id: int
    stripe_customer_id: str
    stripe_subscription_id: str
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Dork schemas
class DorkBase(BaseModel):
    title: str
    description: str
    dork_query: str
    category: str
    tags: List[str]

class DorkCreate(DorkBase):
    user_id: int

class Dork(DorkBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# OSINT schemas
class OSINTQuery(BaseModel):
    query_type: str  # people, phone, domain
    query: str
    options: Optional[Dict] = None

class OSINTResult(BaseModel):
    query_type: str
    query: str
    results: Dict
    timestamp: datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Search History schemas
class SearchHistoryBase(BaseModel):
    search_type: str
    query: str
    results: Dict

class SearchHistoryCreate(SearchHistoryBase):
    user_id: int

class SearchHistory(SearchHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 