<?php
// config.php
define('DB_HOST', 'localhost');
define('DB_NAME', 'u892824626_dorkysearch');
define('DB_USER', 'u892824626_dorkysearch');
define('DB_PASS', 'YOUR_PASSWORD');

// API Keys
define('GOOGLE_API_KEY', 'your_google_api_key');
define('STRIPE_KEY', 'your_stripe_key');

return [
    'app' => [
        'name' => 'DorkySearch',
        'env' => getenv('APP_ENV') ?: 'production',
        'debug' => getenv('APP_DEBUG') ?: false,
        'url' => getenv('APP_URL') ?: 'https://dorkysearch.org',
    ],
    
    'database' => [
        'driver' => 'mysql',
        'host' => getenv('DB_HOST') ?: 'localhost',
        'database' => getenv('DB_DATABASE') ?: 'dorkysearch',
        'username' => getenv('DB_USERNAME') ?: 'dorkysearch',
        'password' => getenv('DB_PASSWORD') ?: '',
        'charset' => 'utf8mb4',
        'collation' => 'utf8mb4_unicode_ci',
    ],
    
    'api' => [
        'whois' => [
            'timeout' => 30,
            'servers' => [
                'com' => 'whois.verisign-grs.com',
                'net' => 'whois.verisign-grs.com',
                'org' => 'whois.pir.org',
                'io' => 'whois.nic.io',
            ],
        ],
        'dns' => [
            'timeout' => 5,
            'types' => ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT'],
        ],
    ],
    
    'cache' => [
        'driver' => 'file',
        'path' => __DIR__ . '/storage/cache',
        'ttl' => 3600, // 1 hour
    ],
    
    'security' => [
        'rate_limit' => [
            'enabled' => true,
            'max_requests' => 60,
            'per_minutes' => 1,
        ],
        'cors' => [
            'allowed_origins' => ['*'],
            'allowed_methods' => ['GET', 'POST', 'OPTIONS'],
            'allowed_headers' => ['Content-Type'],
        ],
    ],
];