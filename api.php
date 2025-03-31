<?php
require_once __DIR__ . '/vendor/autoload.php';

use DorkySearch\Service\DomainAnalyzer;

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

try {
    $analyzer = new DomainAnalyzer();

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);

        if (!isset($data['domain'])) {
            throw new Exception('No domain provided');
        }

        $domain = filter_var($data['domain'], FILTER_SANITIZE_STRING);
        $result = $analyzer->analyze($domain);
        
        // Add domain suggestions
        $suggestions = $analyzer->generateSuggestions($domain);
        $response = $result->toArray();
        $response['suggestions'] = $suggestions;

        echo json_encode($response);
    } elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
        if (!isset($_GET['domain'])) {
            throw new Exception('No domain provided');
        }

        $domain = filter_var($_GET['domain'], FILTER_SANITIZE_STRING);
        $result = $analyzer->analyze($domain);
        
        // Add domain suggestions
        $suggestions = $analyzer->generateSuggestions($domain);
        $response = $result->toArray();
        $response['suggestions'] = $suggestions;

        echo json_encode($response);
    } else {
        throw new Exception('Method not allowed');
    }
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode(['error' => $e->getMessage()]);
} 