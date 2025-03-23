# DorkySearch

An advanced OSINT search platform for comprehensive digital investigations.

## Features

- **Advanced OSINT Search**: Powerful search capabilities with multiple data sources
- **Search History**: Track and manage your search history
- **Secure & Private**: Your searches are encrypted and private
- **Analytics**: Detailed analytics and insights from your searches
- **Multiple Search Types**: General, sensitive files, documents, technology, and directory searches

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: React with TypeScript
- **UI Framework**: Material-UI (MUI)
- **Authentication**: Flask-Login
- **Payment Processing**: Stripe
- **Search API**: Google Custom Search

## Installation

### Prerequisites

- Python 3.7+
- Node.js 14+
- npm or yarn
- Stripe account (for subscription features)
- Google Custom Search API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/jjjgggyyyuuu/DorkySearch.git
   cd DorkySearch
   ```

2. Set up the backend:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```
   cd frontend
   npm install
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   SECRET_KEY=your_secret_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   STRIPE_PRICE_ID=your_stripe_price_id
   ```

## Running the Application

### Development

1. Start the backend server:
   ```
   python app.py
   ```

2. In a separate terminal, start the frontend development server:
   ```
   cd frontend
   npm start
   ```

3. Open your browser and navigate to http://localhost:3000

### Production Deployment

#### Local Production Build

1. Set up environment variables for production in `.env.production`
2. Run the build script:
   ```
   chmod +x build.sh
   ./build.sh
   ```
3. Start the production server:
   ```
   gunicorn wsgi:app
   ```

#### Docker Deployment

1. Make sure Docker and Docker Compose are installed on your system
2. Set up environment variables in `.env`
3. Build and run the containers:
   ```
   docker-compose up -d
   ```
4. Access the application at http://localhost:5000

#### Heroku Deployment

1. Install the Heroku CLI
2. Login to Heroku:
   ```
   heroku login
   ```
3. Create a new Heroku app:
   ```
   heroku create dorkysearch
   ```
4. Add Heroku PostgreSQL addon:
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```
5. Add Heroku Redis addon (if needed):
   ```
   heroku addons:create heroku-redis:hobby-dev
   ```
6. Configure environment variables:
   ```
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set GOOGLE_API_KEY=your_google_api_key
   heroku config:set GOOGLE_CSE_ID=your_google_cse_id
   heroku config:set STRIPE_SECRET_KEY=your_stripe_secret_key
   heroku config:set STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   heroku config:set STRIPE_PRICE_ID=your_stripe_price_id
   ```
7. Deploy the application:
   ```
   git push heroku main
   ```
8. Open the deployed application:
   ```
   heroku open
   ```

## Subscription Features

- **Free Tier**: 2 free searches
- **Premium Tier**: Unlimited searches and additional features

## License

MIT 
