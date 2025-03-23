import json
import time
import random

# Sample data for domain categories
categories = [
    'Technology', 'Health', 'Finance', 'Education', 'E-commerce', 
    'AI', 'Travel', 'Gaming', 'Crypto', 'Sustainability', 'Food'
]

# Sample prefixes for domain generation
prefixes = [
    'smart', 'easy', 'quick', 'best', 'top', 'meta', 'cyber', 'web', 
    'app', 'digital', 'tech', 'ai', 'data', 'cloud', 'green', 'eco', 
    'health', 'edu', 'learn', 'crypto', 'block', 'fin', 'pay', 'invest'
]

# Sample suffixes for domain generation
suffixes = [
    'hub', 'spot', 'zone', 'center', 'space', 'place', 'point', 'base', 
    'lab', 'ware', 'works', 'tech', 'solutions', 'systems', 'app', 'apps'
]

# Sample TLDs
tlds = ['.com', '.io', '.ai', '.app', '.co', '.net', '.org', '.tech']

# Generate 20 domains
domains = []
for i in range(20):
    # Create random domain name
    prefix = random.choice(prefixes)
    if random.random() > 0.5:
        suffix = random.choice(suffixes)
        name = f"{prefix}{suffix}"
    else:
        name = prefix
    
    tld = random.choice(tlds)
    domain_name = f"{name}{tld}"
    
    # Generate price (under $10)
    price = round(random.uniform(0.99, 9.99), 2)
    
    # Generate investment potential (7-10)
    potential = round(random.uniform(7.0, 10.0), 1)
    
    # Calculate projected value (3-10x the price)
    multiplier = random.uniform(3.0, 10.0)
    projected_value = f"${round(price * multiplier, 2)}"
    
    # Select random category
    category = random.choice(categories)
    
    domains.append({
        'name': domain_name,
        'price': price,
        'investment_potential': potential,
        'projected_value': projected_value,
        'category': category
    })

# Save to file
with open('valuable_domains.json', 'w') as f:
    json.dump({
        'domains': domains,
        'timestamp': time.time()
    }, f, indent=2)

print(f"Generated {len(domains)} sample domains and saved to valuable_domains.json") 