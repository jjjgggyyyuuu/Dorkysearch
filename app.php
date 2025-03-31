<?php
// index.php
session_start();

// Database connection
$db_host = 'localhost';
$db_name = 'u892824626_dorkysearch';
$db_user = 'u892824626_dorkysearch';
$db_pass = 'YOUR_PASSWORD'; // You'll need to set this

try {
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}

// Handle domain search
function analyzeDomain($domain) {
    // Add your domain analysis logic here
    return [
        'domain' => $domain,
        'available' => true,
        'value' => rand(1, 100),
        'score' => rand(1, 10)
    ];
}

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $domain = $_POST['domain'] ?? '';
    if ($domain) {
        $result = analyzeDomain($domain);
        $json_result = json_encode($result);
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DorkySearch - Domain Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center mb-8">DorkySearch</h1>
        
        <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
            <form method="POST" action="" class="space-y-4">
                <div>
                    <label for="domain" class="block text-sm font-medium text-gray-700">Enter Domain Name</label>
                    <input type="text" name="domain" id="domain" required
                           class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                </div>
                <button type="submit" class="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600">
                    Analyze Domain
                </button>
            </form>

            <?php if (isset($result)): ?>
            <div class="mt-6 p-4 bg-gray-50 rounded-md">
                <h2 class="text-xl font-semibold mb-4">Results for <?php echo htmlspecialchars($domain); ?></h2>
                <div class="space-y-2">
                    <p>Available: <?php echo $result['available'] ? 'Yes' : 'No'; ?></p>
                    <p>Value Score: <?php echo $result['value']; ?></p>
                    <p>Investment Score: <?php echo $result['score']; ?>/10</p>
                </div>
            </div>
            <?php endif; ?>
        </div>
    </div>

    <script>
        // Add any JavaScript functionality here
    </script>
</body>
</html> 
