import os
from app import app

if __name__ == "__main__":
    # Set environment to production
    os.environ['FLASK_ENV'] = 'production'
    
    # Get port from environment variable (default to 5000)
    port = int(os.environ.get("PORT", 5000))
    
    # Run with production settings
    app.run(host='0.0.0.0', port=port) 