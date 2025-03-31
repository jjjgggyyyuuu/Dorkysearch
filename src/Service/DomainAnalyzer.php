<?php

namespace DorkySearch\Service;

use DorkySearch\Domain\Domain;
use GuzzleHttp\Client;
use PHPWhois\Whois;

class DomainAnalyzer
{
    private Client $httpClient;
    private Whois $whois;

    public function __construct()
    {
        $this->httpClient = new Client();
        $this->whois = new Whois();
    }

    public function analyze(string $domainName): Domain
    {
        $domain = new Domain($domainName);
        
        // Check availability
        $whoisData = $this->checkWhois($domain);
        $domain->setWhoisData($whoisData);
        $domain->setAvailable($this->interpretWhoisAvailability($whoisData));
        
        // Get DNS records
        $dnsRecords = $this->getDnsRecords($domain->getName());
        $domain->setDnsRecords($dnsRecords);
        
        // Calculate value score
        $domain->calculateValueScore();
        
        return $domain;
    }

    private function checkWhois(Domain $domain): array
    {
        try {
            $result = $this->whois->lookup($domain->getName());
            return $result['rawdata'] ?? [];
        } catch (\Exception $e) {
            return ['error' => $e->getMessage()];
        }
    }

    private function interpretWhoisAvailability(array $whoisData): bool
    {
        $whoisStr = strtolower(implode(' ', $whoisData));
        return strpos($whoisStr, 'no match') !== false || 
               strpos($whoisStr, 'not found') !== false ||
               strpos($whoisStr, 'available') !== false;
    }

    private function getDnsRecords(string $domain): array
    {
        $records = [];
        $types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT'];
        
        foreach ($types as $type) {
            $result = dns_get_record($domain, constant("DNS_$type"));
            if ($result) {
                $records[$type] = $result;
            }
        }
        
        return $records;
    }

    public function generateSuggestions(string $domain): array
    {
        $name = explode('.', $domain)[0];
        $tld = pathinfo($domain, PATHINFO_EXTENSION);
        $suggestions = [];
        
        // TLD variations
        $tlds = ['com', 'net', 'org', 'io'];
        foreach ($tlds as $newTld) {
            if ($newTld !== $tld) {
                $suggestions[] = "$name.$newTld";
            }
        }
        
        // Prefix variations
        $prefixes = ['get', 'my', 'the'];
        foreach ($prefixes as $prefix) {
            $suggestions[] = "$prefix$name.$tld";
        }
        
        // Suffix variations
        $suffixes = ['app', 'site', 'web'];
        foreach ($suffixes as $suffix) {
            $suggestions[] = "$name$suffix.$tld";
        }
        
        return array_slice($suggestions, 0, 5);
    }

    public function batchAnalyze(array $domains): array
    {
        $results = [];
        foreach ($domains as $domain) {
            $results[] = $this->analyze($domain)->toArray();
        }
        return $results;
    }
} 