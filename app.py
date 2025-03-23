from flask import Flask, render_template, request, jsonify, url_for, redirect
import os
from dotenv import load_dotenv
from agents.coordinator import AgentCoordinator
from agents.phone_scanner import PhoneScanner
import asyncio
import phonenumbers # type: ignore
from phonenumbers import geocoder, carrier, timezone # type: ignore
import re
import traceback
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import random
import googleapiclient.discovery
import googleapiclient.errors
import stripe
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# User search tracking
user_search_counts = {}  # In a real app, this would be in a database

def check_search_limits(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        user_id = str(current_user.id)
        if user_id not in user_search_counts:
            user_search_counts[user_id] = {
                'count': 0,
                'is_subscribed': False
            }
        
        user_data = user_search_counts[user_id]
        
        if not user_data['is_subscribed'] and user_data['count'] >= 2:
            return render_template('index.html',
                                results={'error': 'You have reached your free search limit. Please subscribe to continue searching.'},
                                current_user=current_user,
                                stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'))
        
        return f(*args, **kwargs)
    return decorated_function

# Simple User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        self.name = f"User {user_id}"
        self.email = f"user{user_id}@example.com"

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Initialize Agent Coordinator and Phone Scanner
coordinator = AgentCoordinator()
phone_scanner = PhoneScanner()

# Google Custom Search API setup
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

def generate_dork_query(query, search_type):
    """Generate a Google dork query based on search type"""
    if search_type == 'documents':
        return f'filetype:(pdf OR doc OR docx OR xls OR xlsx) {query}'
    elif search_type == 'sensitive':
        return f'(password OR username OR admin OR login) {query}'
    elif search_type == 'directories':
        return f'intitle:index.of {query}'
    elif search_type == 'technology':
        return f'site:github.com OR site:stackoverflow.com {query}'
    else:
        return query

def analyze_phone_number(phone_number):
    try:
        # Parse the phone number
        parsed = phonenumbers.parse(phone_number)
        
        # Get format information
        format_info = {
            "raw": phone_number,
            "formatted": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        }
        
        # Get location information
        location_info = {
            "country": geocoder.country_name_for_number(parsed, "en"),
            "region": geocoder.description_for_number(parsed, "en"),
            "carrier": carrier.name_for_number(parsed, "en")
        }
        
        # Generate search patterns
        search_patterns = [
            f"site:linkedin.com {format_info['formatted']}",
            f"site:facebook.com {format_info['formatted']}",
            f"site:whitepages.com {format_info['formatted']}",
            f"site:truepeoplesearch.com {format_info['formatted']}"
        ]
        
        # Potential data source websites
        potential_sources = [
            "LinkedIn",
            "Facebook",
            "WhitePages",
            "TruePeopleSearch",
            "Spokeo",
            "BeenVerified"
        ]
        
        return {
            "valid": True,
            "analysis": {
                "format": format_info,
                "location": location_info
            },
            "search_results": {
                "search_patterns": search_patterns,
                "potential_sources": potential_sources
            }
        }
        
    except phonenumbers.phonenumberutil.NumberParseException:
        return {
            "valid": False,
            "error": "Invalid phone number format. Please try a different format."
        }

def perform_google_search(query, num_results=10):
    """Perform a Google search using the Custom Search API and return real results"""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("Error: Google API keys not configured in .env file.")
        return []

    try:
        service = googleapiclient.discovery.build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        cse = service.cse()
        res = cse.list(q=query, cx=GOOGLE_CSE_ID, num=num_results).execute()

        search_results = []
        if 'items' in res:
            for item in res['items']:
                title = item.get('title', '')
                link = item.get('link', '')
                snippet = item.get('snippet', '')

                search_results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet
                })
        
        print(f"Found {len(search_results)} results for query: {query}")
        return search_results

    except googleapiclient.errors.HttpError as e:
        print(f"Google Custom Search API error: {e}")
        if hasattr(e, 'resp') and e.resp.status == 429:
            print("Google Custom Search API rate limit reached.")
        return []
    except Exception as e:
        print(f"Error during Google Custom Search API call: {e}")
        traceback.print_exc()
        return []

@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)

@app.route('/search', methods=['POST'])
@check_search_limits
def search():
    """Synchronous wrapper for the async search function"""
    return asyncio.run(async_search())

async def async_search():
    """Async implementation of the search functionality"""
    query = request.form.get('query', '')
    search_type = request.form.get('type', 'general')
    
    # Increment search count for non-subscribed users
    user_id = str(current_user.id)
    if not user_search_counts[user_id]['is_subscribed']:
        user_search_counts[user_id]['count'] += 1
    
    print(f"Search request: query='{query}', type='{search_type}'")
    
    if not query:
        return render_template('index.html', 
                             results={'error': 'Please enter a search query', 'search_items': []}, 
                             current_user=current_user)
    
    # Handle phone search separately
    if search_type == 'phone':
    try:
            cleaned_number = re.sub(r'[^\d+]', '', query)
            if not cleaned_number.startswith('+'):
                cleaned_number = '+1' + cleaned_number
            
            # Directly await the async function
            phone_results = await phone_scanner.scan_number(cleaned_number)
            
            # If the phone_results contains 'scan_results' which is a coroutine, await it
            if (isinstance(phone_results, dict) and 'scan_results' in phone_results and 
                asyncio.iscoroutine(phone_results['scan_results'])):
                phone_results['scan_results'] = await phone_results['scan_results']
            
            # Ensure scan_results is a dictionary with all required fields for the template
            if isinstance(phone_results, dict):
                if 'scan_results' not in phone_results or not isinstance(phone_results['scan_results'], dict):
                    phone_results['scan_results'] = {}
                
                # Ensure scan_results has the required basic_info field
                if 'scan_results' in phone_results and isinstance(phone_results['scan_results'], dict):
                    scan_results = phone_results['scan_results']
                    
                    # Ensure basic_info exists
                    if 'basic_info' not in scan_results:
                        scan_results['basic_info'] = {
                            "raw": cleaned_number,
                            "formatted": cleaned_number,
                            "international": cleaned_number,
                            "e164": cleaned_number,
                            "country": "Unknown",
                            "region": "Unknown",
                            "carrier": "Unknown",
                            "timezone": [],
                            "is_valid": False,
                            "is_possible": False
                        }
                    
                    # Ensure metadata exists
                    if 'metadata' not in scan_results:
                        scan_results['metadata'] = {
                            "number_type": "Unknown",
                            "area_code": cleaned_number[-10:-7] if len(cleaned_number) >= 10 else "Unknown",
                            "is_toll_free": False,
                            "is_voip": False,
                            "registration_date": "Unknown"
                        }
                    
                    # Ensure data_sources exists
                    if 'data_sources' not in scan_results:
                        scan_results['data_sources'] = {
                            "numverify": False,
                            "googleSearch": False,
                            "ovhScan": False,
                            "footprints": False,
                            "reputationChecks": False
                        }
                    
                    # Ensure social_media exists
                    if 'social_media' not in scan_results:
                        scan_results['social_media'] = {
                            "platforms_found": [],
                            "total_platforms_checked": 0,
                            "platform_data": {},
                            "search_patterns": {},
                            "online_presence_score": 0,
                            "privacy_risk": "Unknown"
                        }
                    
                    # Ensure reputation exists
                    if 'reputation' not in scan_results:
                        scan_results['reputation'] = {
                            "spam_risk": "Unknown",
                            "fraud_reports": 0,
                            "spam_reports": 0,
                            "reported_as_spam": False,
                            "reported_as_fraud": False,
                            "last_reported": "N/A",
                            "confidence": "Low"
                        }
                    
                    # Ensure recommendations exists
                    if 'recommendations' not in scan_results:
                        scan_results['recommendations'] = ["Error occurred during scanning. Please try again."]
            
            if isinstance(phone_results, dict) and 'error' in phone_results:
                return render_template('index.html',
                                    query=query,
                                       results={'error': phone_results['error'], 'search_items': []}, 
                                       current_user=current_user)
            
            # Create a results structure that includes items
            results = {
                'type': 'phone',
                'query': query,
                'search_items': [],  # Initialize empty list for template compatibility
                'phone_data': phone_results  # Store phone-specific data
            }
            
            return render_template('index.html', 
                                 query=query,
                                   results=results, 
                                   current_user=current_user)
        except Exception as e:
            print(f"Phone search error: {str(e)}")
            traceback.print_exc()
            
            # Create complete structure for error case to avoid template errors
            error_results = {
                'type': 'phone',
                'query': query,
                'search_items': [],
                'phone_data': {
                    'success': False,
                    'error': str(e),
                    'scan_results': {
                        'number': cleaned_number,
                        'basic_info': {
                            "raw": cleaned_number,
                            "formatted": cleaned_number,
                            "international": cleaned_number,
                            "e164": cleaned_number,
                            "country": "Unknown",
                            "region": "Unknown",
                            "carrier": "Unknown",
                            "timezone": [],
                            "is_valid": False,
                            "is_possible": False
                        },
                        'metadata': {
                            "number_type": "Unknown",
                            "area_code": cleaned_number[-10:-7] if len(cleaned_number) >= 10 else "Unknown",
                            "is_toll_free": False,
                            "is_voip": False
                        },
                        'data_sources': {
                            "numverify": False,
                            "googleSearch": False,
                            "ovhScan": False,
                            "footprints": False,
                            "reputationChecks": False
                        },
                        'social_media': {
                            "platforms_found": [],
                            "total_platforms_checked": 0,
                            "platform_data": {},
                            "search_patterns": {},
                            "online_presence_score": 0,
                            "privacy_risk": "Unknown"
                        },
                        'reputation': {
                            "spam_risk": "Unknown",
                            "fraud_reports": 0,
                            "spam_reports": 0,
                            "reported_as_spam": False,
                            "reported_as_fraud": False,
                            "last_reported": "N/A",
                            "confidence": "Low"
                        },
                        'recommendations': ["Error occurred during scanning. Please try again."]
                    },
                    'phoneinfoga': True
                }
            }
            
            return render_template('index.html', 
                                   results=error_results, 
                                   current_user=current_user)
    
    # Handle all other search types
    try:
        # Generate dork query
        dork_query = generate_dork_query(query, search_type)
        print(f"Generated dork query: {dork_query}")
        
        # Get insights as a string
        insights = get_insights_for_search_type(search_type)
        if callable(insights):
            insights = str(insights())  # Convert callable result to string
        
        # Perform actual Google search with dork query
        search_items = perform_google_search(dork_query)
        
        # Add delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        # Fallback: if no results and search_type is one of the specialized types, try the base query
        if not search_items and search_type in ['documents', 'sensitive', 'directories', 'technology']:
            print("No results for dork query; falling back to base query search.")
            fallback_search_items = perform_google_search(query)
            if fallback_search_items:
                search_items = fallback_search_items
                dork_query = query
        
        # Create a response structure with real search results
        results = {
            'query': query,
            'dork_query': dork_query,
            'type': search_type,
            'search_items': search_items,
            'analytics': {
                'total_results': len(search_items),
                'insights': str(insights)  # Ensure insights is a string
            }
        }
        
        return render_template('index.html', 
                             query=query,
                             results=results,
                             stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'),
                             current_user=current_user)
    except Exception as e:
        print(f"Search error: {str(e)}")
        traceback.print_exc()
        return render_template('index.html', 
                             results={'error': f'An error occurred: {str(e)}', 'search_items': []},
                             stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'),
                             current_user=current_user)

def get_insights_for_search_type(search_type):
    """Generate insights based on search type"""
    if search_type == 'sensitive':
        return '⚠️ Found potentially sensitive information. Review carefully.'
    elif search_type == 'documents':
        return '📄 Found document results. Check file types before downloading.'
    elif search_type == 'technology':
        return '🔧 Found technology-related results. Review for security implications.'
    elif search_type == 'directories':
        return '📁 Found directory listings. These may contain accessible files.'
    else:
        return 'Sample results for demonstration purposes.'

@app.route('/status')
def project_status():
    """Get current project status"""
    status = coordinator.get_project_status()
    return jsonify(status)

@app.route('/report')
def generate_report():
    """Generate comprehensive project report"""
    report = coordinator.generate_report()
    return jsonify(report)

@app.route('/initialize', methods=['POST'])
def initialize_project():
    """Initialize or reset project"""
    result = coordinator.initialize_project()
    return jsonify(result)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    # In a real application, you would validate credentials against a database
    # For now, we'll just create a dummy user
    user = User("1")
    login_user(user)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
        
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    # In a real application, you would store user data in a database
    # For now, we'll just create a dummy user
    user = User("1")
    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.getenv('STRIPE_PRICE_ID'),  # Your subscription price ID from Stripe
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'cancelled',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@app.route('/success')
@login_required
def success():
    session_id = request.args.get('session_id')
    if session_id:
        try:
            # Verify the session and update user's subscription status
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                user_id = str(current_user.id)
                if user_id in user_search_counts:
                    user_search_counts[user_id]['is_subscribed'] = True
                else:
                    user_search_counts[user_id] = {
                        'count': 0,
                        'is_subscribed': True
                    }
                return render_template('success.html')
        except Exception as e:
            print(f"Error verifying subscription: {str(e)}")
    return redirect(url_for('index'))

@app.route('/cancelled')
def cancelled():
    return render_template('cancelled.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for the React frontend to perform searches"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    try:
        # Check search limits for API users
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_id = str(current_user.id)
            if user_id in user_search_counts:
                if not user_search_counts[user_id].get('is_subscribed', False) and user_search_counts[user_id]['count'] >= 2:
                    return jsonify({
                        "error": "Search limit reached. Please subscribe for unlimited searches.",
                        "limit_reached": True,
                        "results": []
                    }), 403
                user_search_counts[user_id]['count'] += 1
            else:
                user_search_counts[user_id] = {'count': 1, 'is_subscribed': False}
        else:
            # User not authenticated
            return jsonify({
                "error": "You need to log in to perform searches.",
                "requires_auth": True,
                "results": []
            }), 401
        
        # Process the search query
        search_type = data.get('search_type', 'general')
        
        # Create a dork query based on the search type
        if search_type == 'sensitive':
            dork_query = f"{query} filetype:pdf OR filetype:doc OR filetype:xlsx OR filetype:txt intext:confidential OR intext:private OR intext:secret"
        elif search_type == 'documents':
            dork_query = f"{query} filetype:pdf OR filetype:doc OR filetype:docx OR filetype:ppt OR filetype:pptx OR filetype:xlsx OR filetype:xls"
        elif search_type == 'technology':
            dork_query = f"{query} intext:technology OR intext:server OR intext:software OR intext:hardware OR intext:version"
        elif search_type == 'directories':
            dork_query = f"{query} intitle:index.of"
        else:
            dork_query = query
            
        search_items = perform_google_search(dork_query)
        
        # Add delay to avoid rate limiting
        time.sleep(random.uniform(0.5, 1.5))
        
        # Format results for the frontend
        results = []
        for item in search_items:
            results.append({
                "title": item.get('title', 'No title'),
                "url": item.get('link', '#'),
                "description": item.get('snippet', 'No description available'),
                "type": search_type,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
            
        # Get insights for the search type
        insights = get_insights_for_search_type(search_type)
        
        # Get remaining searches for this user
        remaining_searches = float('inf')
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_id = str(current_user.id)
            if user_id in user_search_counts:
                is_subscribed = user_search_counts[user_id].get('is_subscribed', False)
                searches_used = user_search_counts[user_id].get('count', 0)
                if not is_subscribed:
                    remaining_searches = max(0, 2 - searches_used)
        
        return jsonify({
            "results": results,
            "query": query,
            "dork_query": dork_query,
            "insights": insights,
            "total_results": len(results),
            "remainingSearches": -1 if remaining_searches == float('inf') else remaining_searches
        })
    except Exception as e:
        print(f"API search error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": f"An error occurred: {str(e)}",
            "results": []
        }), 500

@app.route('/api/subscription/status', methods=['GET'])
def subscription_status():
    """API endpoint to check subscription status for the React frontend"""
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        user_id = str(current_user.id)
        if user_id in user_search_counts:
            user_data = user_search_counts[user_id]
            # Calculate searches remaining (default is 2 for non-subscribers)
            searches_used = user_data.get('count', 0)
            is_subscribed = user_data.get('is_subscribed', False)
            searches_remaining = float('inf') if is_subscribed else max(0, 2 - searches_used)
            
            return jsonify({
                "isSubscribed": is_subscribed,
                "searchesRemaining": searches_remaining if searches_remaining != float('inf') else -1,
                "searchesUsed": searches_used
            })
        else:
            # New user, no searches yet
            return jsonify({
                "isSubscribed": False,
                "searchesRemaining": 2,
                "searchesUsed": 0
            })
    else:
        # Not logged in
        return jsonify({
            "error": "Not authenticated",
            "isSubscribed": False,
            "searchesRemaining": 0
        }), 401

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """API endpoint to check authentication status for the React frontend"""
    is_authenticated = hasattr(current_user, 'is_authenticated') and current_user.is_authenticated
    
    if is_authenticated:
        user_id = str(current_user.id)
        return jsonify({
            "isAuthenticated": True,
            "userId": user_id,
            "username": current_user.name if hasattr(current_user, 'name') else f"User {user_id}"
        })
    else:
        return jsonify({
            "isAuthenticated": False,
            "message": "User not authenticated"
        })

if __name__ == '__main__':
    # Initialize the project
    coordinator.initialize_project()
    
    # Start the Flask app
    app.run() 
