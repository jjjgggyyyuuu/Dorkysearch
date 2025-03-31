<?php
session_start();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DorkySearch - Advanced Domain Analysis Tool</title>
    
    <!-- CSS -->
    <link rel="stylesheet" href="/assets/css/style.css">
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/assets/images/favicon.png">
    
    <!-- Meta tags -->
    <meta name="description" content="DorkySearch - Advanced domain analysis and OSINT tool">
    <meta name="keywords" content="domain analysis, OSINT, domain research, domain value">
    
    <!-- Open Graph -->
    <meta property="og:title" content="DorkySearch - Domain Analysis Tool">
    <meta property="og:description" content="Advanced domain analysis and OSINT tool">
    <meta property="og:image" content="/assets/images/og-image.png">
    <meta property="og:url" content="https://dorkysearch.org">
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">DorkySearch</a>
            <nav class="main-nav">
                <button id="darkModeToggle" class="btn" data-tooltip="Toggle Dark Mode">🌙</button>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <h1>Advanced Domain Analysis</h1>
            <p>Analyze domains, check availability, and discover valuable opportunities</p>
        </section>

        <form id="searchForm" class="search-form">
            <div class="input-group">
                <label for="domainInput" class="input-label">Enter Domain Name</label>
                <input type="text" id="domainInput" class="input-field" 
                       placeholder="example.com" required
                       pattern="^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$"
                       title="Please enter a valid domain name">
            </div>
            <button type="submit" class="btn btn-primary">Analyze Domain</button>
        </form>

        <div id="loadingSpinner" class="loading hidden">
            <div class="loading-spinner"></div>
        </div>

        <section id="resultsSection" class="results-section">
            <!-- Results will be dynamically inserted here -->
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; <?php echo date('Y'); ?> DorkySearch. All rights reserved.</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script type="module" src="/assets/js/utils.js"></script>
    <script type="module" src="/assets/js/api-client.js"></script>
    <script type="module" src="/assets/js/main.js"></script>
</body>
</html> 