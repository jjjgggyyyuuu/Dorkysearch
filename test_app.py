from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '')
    search_type = request.form.get('type', 'general')
    
    print(f"Search request: query='{query}', type='{search_type}'")
    
    if not query:
        return render_template('index.html', 
                             results={'error': 'Please enter a search query'})
    
    # Simple mock results to avoid API calls
    dork_query = f"Sample dork query for: {query}"
    
    # Sample results
    results = {
        'query': query,
        'dork_query': dork_query,
        'type': search_type,
        'items': [
            {
                'title': f'Sample Result 1 for {query}',
                'link': 'https://example.com/1',
                'snippet': f'This is a sample search result for {query}...'
            },
            {
                'title': f'Sample Result 2 for {query}',
                'link': 'https://example.com/2',
                'snippet': f'Another sample search result for {query}...'
            }
        ],
        'analytics': {
            'total_results': 2,
            'insights': 'Sample analytics data for testing.'
        }
    }
    
    if search_type == 'phone':
        # Mock phone results
        results = {
            'query': query,
            'type': 'phone',
            'basic_info': {
                'format': {
                    'international': f'+1 {query}',
                    'national': query,
                    'e164': f'+1{query.replace("-", "").replace(" ", "")}'
                },
                'country': {
                    'name': 'United States',
                    'code': 'US'
                },
                'carrier': 'Sample Carrier',
                'timezone': ['America/New_York'],
                'line_type': 'mobile'
            },
            'scan_results': {
                'owner_info': {
                    'possible_names': ['John Doe', 'Jane Smith'],
                    'possible_addresses': ['123 Sample St, New York, NY'],
                    'email_addresses': ['example@email.com']
                }
            }
        }
    
    return render_template('index.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5001) 