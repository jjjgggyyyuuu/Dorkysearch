from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin
from .database import Base

class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    saved_dorks = relationship("SavedDork", back_populates="user")

    @staticmethod
    def get(user_id):
        # This method is required by Flask-Login
        # In a real application, this would load from the database
        if user_id:
            return User.query.get(int(user_id))
        return None

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    plan_type = Column(String)  # basic, pro, enterprise
    status = Column(String)  # active, canceled, past_due
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="subscription")

class SavedDork(Base):
    __tablename__ = "saved_dorks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    dork_query = Column(Text)
    category = Column(String)
    tags = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="saved_dorks")

class DorkCategory(Base):
    __tablename__ = "dork_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    search_type = Column(String)  # dork, osint, people, phone, domain
    query = Column(Text)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
