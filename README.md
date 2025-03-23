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
   git clone https://github.com/yourusername/DorkySearch.git
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

## Subscription Features

- **Free Tier**: 2 free searches
- **Premium Tier**: Unlimited searches and additional features

## License

MIT 