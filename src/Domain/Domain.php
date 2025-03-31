<?php

namespace DorkySearch\Domain;

class Domain
{
    private string $name;
    private array $whoisData;
    private array $dnsRecords;
    private float $valueScore;
    private bool $isAvailable;

    public function __construct(string $name)
    {
        $this->name = strtolower(trim($name));
        $this->whoisData = [];
        $this->dnsRecords = [];
        $this->valueScore = 0.0;
        $this->isAvailable = false;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function setWhoisData(array $whoisData): void
    {
        $this->whoisData = $whoisData;
    }

    public function getWhoisData(): array
    {
        return $this->whoisData;
    }

    public function setDnsRecords(array $dnsRecords): void
    {
        $this->dnsRecords = $dnsRecords;
    }

    public function getDnsRecords(): array
    {
        return $this->dnsRecords;
    }

    public function setValueScore(float $score): void
    {
        $this->valueScore = $score;
    }

    public function getValueScore(): float
    {
        return $this->valueScore;
    }

    public function setAvailable(bool $isAvailable): void
    {
        $this->isAvailable = $isAvailable;
    }

    public function isAvailable(): bool
    {
        return $this->isAvailable;
    }

    public function calculateValueScore(): float
    {
        $score = 0;
        
        // Length factor
        $length = strlen(explode('.', $this->name)[0]);
        if ($length <= 4) $score += 20;
        elseif ($length <= 8) $score += 15;
        elseif ($length <= 12) $score += 10;
        
        // Check for numbers
        if (!preg_match('/\d/', $this->name)) $score += 10;
        
        // Check for hyphens
        if (!strpos($this->name, '-')) $score += 10;
        
        // TLD value
        $tld = strtolower(pathinfo($this->name, PATHINFO_EXTENSION));
        $valuableTlds = ['com' => 20, 'org' => 15, 'net' => 15, 'io' => 15];
        $score += $valuableTlds[$tld] ?? 5;

        $this->valueScore = $score;
        return $score;
    }

    public function toArray(): array
    {
        return [
            'domain' => $this->name,
            'available' => $this->isAvailable,
            'value_score' => [
                'score' => $this->valueScore,
                'factors' => $this->getValueFactors()
            ],
            'whois_data' => $this->whoisData,
            'dns_records' => $this->dnsRecords
        ];
    }

    private function getValueFactors(): array
    {
        $length = strlen(explode('.', $this->name)[0]);
        $tld = strtolower(pathinfo($this->name, PATHINFO_EXTENSION));
        
        return [
            'length' => $length,
            'no_numbers' => !preg_match('/\d/', $this->name),
            'no_hyphens' => !strpos($this->name, '-'),
            'tld' => $tld
        ];
    }
} 