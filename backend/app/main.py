from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import stripe
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="DorkySearch API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Models
class User(BaseModel):
    username: str
    email: str
    subscription_status: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Routes
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implement user authentication
    pass

@app.post("/register")
async def register_user(username: str, email: str, password: str):
    # Implement user registration
    pass

@app.post("/subscribe")
async def create_subscription(plan: str, user: User = Depends(oauth2_scheme)):
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.getenv(f"STRIPE_PRICE_ID_{plan.upper()}"),
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://dorkysearch.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://dorkysearch.com/cancel',
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/search/osint")
async def osint_search(query: str, user: User = Depends(oauth2_scheme)):
    # Implement OSINT search using the Swarm agents
    pass

@app.post("/search/domain")
async def domain_search(domain: str, user: User = Depends(oauth2_scheme)):
    # Implement domain intelligence search
    pass

@app.post("/search/people")
async def people_search(query: str, user: User = Depends(oauth2_scheme)):
    # Implement people search
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 