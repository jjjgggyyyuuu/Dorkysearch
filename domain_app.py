from flask import Flask, jsonify, render_template, request, send_from_directory
import os
import json
import time
import traceback
import threading
from datetime import datetime
from agents.domain_research_agent import DomainResearchAgent

app = Flask(__name__, template_folder='templates', static_folder='static')

# Global user authentication - in a real app, this would use a proper auth system
ADMIN_KEY = 'admin123'  # A simple API key for demo purposes

# Cache configuration
CACHE_FILE = "valuable_domains.json"
CACHE_DURATION = 86400  # 24 hours

# Background task flag
is_domain_refresh_running = False

@app.route('/')
def index():
    """Home page"""
    return render_template('domain_index.html')

@app.route('/domains/valuable', methods=['GET'])
def find_valuable_domains():
    """Find potentially valuable domains under $10"""
    try:
        # Simple API key auth
        api_key = request.args.get('key', '')
        if api_key != ADMIN_KEY:
            # Still show the page but with a message about authentication
            return render_template(
                'valuable_domains.html',
                error="Please provide a valid API key to view valuable domains",
                domains=[],
                count=0
            )
        
        domains = []
        refresh_date = None
        is_refreshing = is_domain_refresh_running
        
        # Check if we have cached results
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                domains = data.get('domains', [])
                refresh_date = data.get('timestamp')
                
                # Format the timestamp for display
                if refresh_date:
                    refresh_date = datetime.fromtimestamp(refresh_date).strftime('%Y-%m-%d %H:%M:%S')
                
                # Check if cache is older than 24 hours and auto-refresh if needed
                if data.get('timestamp', 0) < time.time() - CACHE_DURATION and not is_refreshing:
                    # Start refresh in background
                    threading.Thread(target=run_domain_research_bg).start()
                    is_refreshing = True
        
        # If no domains found and not already refreshing, start a refresh
        if not domains and not is_refreshing:
            threading.Thread(target=run_domain_research_bg).start()
            is_refreshing = True
        
        return render_template(
            'valuable_domains.html',
            domains=domains,
            refresh_date=refresh_date,
            is_refreshing=is_refreshing
        )
    except Exception as e:
        print(f"Error finding valuable domains: {str(e)}")
        traceback.print_exc()
        return render_template(
            'valuable_domains.html',
            error=f"An error occurred: {str(e)}",
            domains=[],
            count=0
        )

def run_domain_research_bg():
    """Run domain research in the background"""
    global is_domain_refresh_running
    
    if is_domain_refresh_running:
        return
    
    is_domain_refresh_running = True
    
    try:
        print("Starting background domain research...")
        agent = DomainResearchAgent()
        results = agent.find_valuable_domains(max_price=10.0, min_investment_potential=7)
        
        # Format the results
        domains = []
        for domain in results:
            # Format each domain entry
            domains.append({
                'name': domain.get('domain', ''),
                'price': domain.get('price', 0),
                'investment_potential': domain.get('score', 0) / 10,  # Scale to 0-10
                'projected_value': domain.get('investment_potential', {}).get('estimated_resale', '$0').replace('$', ''),
                'category': domain.get('investment_potential', {}).get('primary_industry', 'General')
            })
            
        # Save to cache file
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                'domains': domains,
                'timestamp': time.time()
            }, f, indent=2)
            
        print("Background domain research completed and saved")
    except Exception as e:
        print(f"Error in background domain research: {str(e)}")
        traceback.print_exc()
    finally:
        is_domain_refresh_running = False

@app.route('/api/domains/refresh')
def refresh_domains():
    # Simple API key authentication
    api_key = request.args.get('key')
    if api_key != ADMIN_KEY:
        return jsonify({"success": False, "error": "Unauthorized - Invalid API key"}), 401
    
    # Start the background task if not already running
    if not is_domain_refresh_running:
        threading.Thread(target=run_domain_research_bg).start()
        return jsonify({"success": True, "message": "Domain refresh started"})
    else:
        return jsonify({"success": False, "error": "Refresh already in progress"})

@app.route('/api/domains/list')
def list_domains():
    # Simple API key authentication
    api_key = request.args.get('key')
    if api_key != ADMIN_KEY:
        return jsonify({"success": False, "error": "Unauthorized - Invalid API key"}), 401
    
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                return jsonify({
                    "success": True,
                    "domains": data.get('domains', []),
                    "refresh_date": data.get('timestamp')
                })
        else:
            return jsonify({"success": False, "error": "No domain data available yet"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Optional: Run the domain research at startup
    # thread = threading.Thread(target=run_domain_research_bg)
    # thread.daemon = True
    # thread.start()
    
    # Start the Flask app
    app.run(debug=True, port=5001) 