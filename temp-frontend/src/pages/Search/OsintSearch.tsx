import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Chip,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  History as HistoryIcon,
  Save as SaveIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface SearchResult {
  title: string;
  url: string;
  description: string;
  type: 'sensitive' | 'normal';
  timestamp: string;
}

const OsintSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searchHistory] = useState<string[]>([
    'inurl:admin filetype:php',
    'site:example.com password',
    'intitle:index.of ssh_key',
  ]);

  const predefinedQueries = [
    { label: 'Admin Panels', query: 'inurl:admin OR inurl:login OR inurl:wp-admin' },
    { label: 'Config Files', query: 'filetype:conf OR filetype:config OR filetype:env' },
    { label: 'Database Files', query: 'filetype:sql OR filetype:db OR filetype:backup' },
    { label: 'Sensitive Docs', query: 'filetype:pdf OR filetype:doc OR filetype:xlsx password' },
  ];

  const handleSearch = async () => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setResults([
        {
          title: 'Example Admin Panel',
          url: 'https://example.com/admin',
          description: 'Found potential admin panel with login form',
          type: 'sensitive',
          timestamp: new Date().toISOString(),
        },
        // Add more mock results
      ]);
      setIsLoading(false);
    }, 1500);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  return (
    <Box sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom>
          OSINT Search
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" paragraph>
          Use advanced Google dorking techniques to find sensitive information
        </Typography>

        {/* Search Box */}
        <Paper
          elevation={3}
          sx={{
            p: 3,
            mb: 4,
            borderRadius: 2,
          }}
        >
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                variant="outlined"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your search query (e.g., site:example.com filetype:pdf)"
                InputProps={{
                  endAdornment: (
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleSearch}
                      disabled={isLoading}
                      startIcon={isLoading ? <CircularProgress size={20} /> : <SearchIcon />}
                    >
                      Search
                    </Button>
                  ),
                }}
              />
            </Grid>
            
            {/* Predefined Queries */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Quick Searches:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {predefinedQueries.map((item, index) => (
                  <Chip
                    key={index}
                    label={item.label}
                    onClick={() => setQuery(item.query)}
                    clickable
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Grid>

            {/* Search History */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <HistoryIcon sx={{ mr: 1 }} /> Recent Searches:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {searchHistory.map((item, index) => (
                  <Chip
                    key={index}
                    label={item}
                    onClick={() => setQuery(item)}
                    onDelete={() => {/* Implement delete */}}
                    clickable
                    size="small"
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Search Results */}
        {results.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Typography variant="h6" gutterBottom>
              Search Results
            </Typography>
            <Grid container spacing={2}>
              {results.map((result, index) => (
                <Grid item xs={12} key={index}>
                  <Card
                    sx={{
                      borderLeft: 6,
                      borderColor: result.type === 'sensitive' ? 'error.main' : 'primary.main',
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="h6" component="h3" gutterBottom>
                          {result.title}
                        </Typography>
                        <Box>
                          <Tooltip title="Copy URL">
                            <IconButton onClick={() => copyToClipboard(result.url)} size="small">
                              <CopyIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Save Result">
                            <IconButton size="small">
                              <SaveIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                      <Typography
                        variant="body2"
                        color="textSecondary"
                        component="a"
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        sx={{ textDecoration: 'none' }}
                      >
                        {result.url}
                      </Typography>
                      <Typography variant="body1" sx={{ mt: 1 }}>
                        {result.description}
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        <Chip
                          label={result.type === 'sensitive' ? 'Sensitive Content' : 'Normal Content'}
                          color={result.type === 'sensitive' ? 'error' : 'default'}
                          size="small"
                        />
                        <Typography variant="caption" sx={{ ml: 2 }}>
                          Found: {new Date(result.timestamp).toLocaleString()}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        )}
      </motion.div>
    </Box>
  );
};

export default OsintSearch; 