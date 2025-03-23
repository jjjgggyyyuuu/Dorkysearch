import React, { useState, useEffect } from 'react';
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
  Container,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search as SearchIcon,
  ContentCopy as CopyIcon,
  History as HistoryIcon,
  LockOpen as LockOpenIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface SearchResult {
  title: string;
  url: string;
  description: string;
  type: string;
  timestamp: string;
}

// Additional interface for subscription state
interface SubscriptionState {
  isSubscribed: boolean;
  searchesRemaining: number;
  limitReached: boolean;
}

// Add this after the SubscriptionState interface
interface AuthState {
  isAuthenticated: boolean;
  redirectToLogin: boolean;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
  },
};

const OsintSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searchType, setSearchType] = useState('general');
  const [searchHistory] = useState<string[]>([
    'site:linkedin.com "cyber security"',
    'filetype:pdf "confidential"',
    'inurl:admin intitle:login',
  ]);
  const [error, setError] = useState<string | null>(null);
  const [insights, setInsights] = useState<string | null>(null);
  
  // Subscription state
  const [subscription, setSubscription] = useState<SubscriptionState>({
    isSubscribed: false,
    searchesRemaining: 2, // Default free searches
    limitReached: false,
  });
  
  // Subscription dialog
  const [subscriptionDialogOpen, setSubscriptionDialogOpen] = useState(false);

  // Add authentication state
  const [auth, setAuth] = useState<AuthState>({
    isAuthenticated: false,
    redirectToLogin: false
  });
  
  const searchTypes = [
    { value: 'general', label: 'General' },
    { value: 'sensitive', label: 'Sensitive Files' },
    { value: 'documents', label: 'Documents' },
    { value: 'technology', label: 'Technology' },
    { value: 'directories', label: 'Directories' }
  ];
  
  // Check both subscription and auth status on component mount
  useEffect(() => {
    // Check auth status first
    fetch('/api/auth/status')
      .then(response => response.json())
      .then(data => {
        setAuth({
          isAuthenticated: data.isAuthenticated,
          redirectToLogin: false
        });
        
        // Only check subscription if authenticated
        if (data.isAuthenticated) {
          fetch('/api/subscription/status')
            .then(response => response.json())
            .then(subData => {
              if (subData && !subData.error) {
                setSubscription({
                  isSubscribed: subData.isSubscribed,
                  searchesRemaining: subData.searchesRemaining,
                  limitReached: subData.searchesRemaining <= 0 && !subData.isSubscribed
                });
              }
            })
            .catch(err => {
              console.error('Error checking subscription status:', err);
            });
        }
      })
      .catch(err => {
        console.error('Error checking authentication status:', err);
      });
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    // Check if user is authenticated
    if (!auth.isAuthenticated) {
      // Redirect to login
      setAuth(prev => ({...prev, redirectToLogin: true}));
      window.location.href = '/login?redirect=search/osint';
      return;
    }
    
    // Check if search limit reached
    if (subscription.limitReached && !subscription.isSubscribed) {
      setSubscriptionDialogOpen(true);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query,
          search_type: searchType
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        // Check for authentication issues
        if (response.status === 401 && data.requires_auth) {
          setAuth(prev => ({...prev, redirectToLogin: true}));
          window.location.href = '/login?redirect=search/osint';
          throw new Error('Please login to continue searching.');
        }
        
        // Handle search limit reached error specifically
        if (response.status === 403 && data.limit_reached) {
          setSubscription(prev => ({
            ...prev,
            limitReached: true,
            searchesRemaining: 0
          }));
          setSubscriptionDialogOpen(true);
          throw new Error('Search limit reached. Please subscribe to continue.');
        }
        
        throw new Error(data.error || `Search request failed with status: ${response.status}`);
      }
      
      // Check if we received remaining searches info
      if (data.remainingSearches !== undefined) {
        setSubscription(prev => ({
          ...prev,
          searchesRemaining: data.remainingSearches >= 0 ? data.remainingSearches : prev.searchesRemaining,
          limitReached: data.remainingSearches === 0 && !prev.isSubscribed
        }));
      }
      
      setResults(data.results || []);
      setInsights(data.insights || null);
      
    } catch (error) {
      console.error('Search error:', error);
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = () => {
    // Connect to the Stripe checkout session
    fetch('/create-checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        console.error('Checkout error:', data.error);
        setError(data.error);
      } else if (data.id) {
        // Redirect to Stripe Checkout
        window.location.href = `https://checkout.stripe.com/pay/${data.id}`;
      }
    })
    .catch(err => {
      console.error('Error creating checkout session:', err);
      setError('Failed to initiate subscription process. Please try again.');
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <Container maxWidth="lg">
      <Box
        component={motion.div}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Subscription status banner */}
        {!subscription.isSubscribed && (
          <Alert 
            severity={subscription.limitReached ? "warning" : "info"} 
            sx={{ mb: 2 }}
            action={
              <Button 
                color="inherit" 
                size="small" 
                startIcon={<LockOpenIcon />}
                onClick={() => setSubscriptionDialogOpen(true)}
              >
                Upgrade
              </Button>
            }
          >
            {subscription.limitReached 
              ? "You've reached your free search limit. Subscribe to continue searching." 
              : `You have ${subscription.searchesRemaining} free searches remaining.`}
          </Alert>
        )}

        <Box
          sx={{
            p: 3,
            mb: 4,
            background: (theme) =>
              `linear-gradient(45deg, ${theme.palette.primary.light} 0%, ${theme.palette.primary.main} 100%)`,
          }}
        >
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            align="center"
            sx={{ color: 'white' }}
          >
            OSINT Search
          </Typography>
          <Box
            component="form"
            onSubmit={(e: React.FormEvent) => {
              e.preventDefault();
              handleSearch();
            }}
            sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 1 }}
          >
            <TextField
              fullWidth
              placeholder="Enter your search query..."
              value={query}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setQuery(e.target.value)
              }
              sx={{
                backgroundColor: 'white',
                borderRadius: 1,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: 'transparent',
                  },
                  '&:hover fieldset': {
                    borderColor: 'transparent',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'transparent',
                  },
                },
                flex: 3,
              }}
            />
            
            <FormControl sx={{ minWidth: 150, flex: 1, backgroundColor: 'white', borderRadius: 1 }}>
              <InputLabel id="search-type-label">Search Type</InputLabel>
              <Select
                labelId="search-type-label"
                value={searchType}
                label="Search Type"
                onChange={(e) => setSearchType(e.target.value)}
              >
                {searchTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Button
              variant="contained"
              type="submit"
              disabled={loading}
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'grey.100',
                },
              }}
            >
              {loading ? (
                <CircularProgress size={24} />
              ) : (
                <SearchIcon fontSize="large" />
              )}
            </Button>
          </Box>
        </Box>

        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Predefined Queries
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {searchHistory.map((query) => (
                <Chip
                  key={query}
                  label={query}
                  onClick={() => setQuery(query)}
                  onDelete={() => copyToClipboard(query)}
                  deleteIcon={<CopyIcon />}
                  sx={{ mb: 1 }}
                />
              ))}
            </Box>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
            {error}
          </Alert>
        )}

        {insights && results.length > 0 && (
          <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
            {insights}
          </Alert>
        )}

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate={results.length > 0 ? 'visible' : 'hidden'}
        >
          <Grid container spacing={2}>
            {results.map((result, index) => (
              <Grid item xs={12} key={index}>
                <motion.div variants={itemVariants}>
                  <Card>
                    <CardContent>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start',
                        }}
                      >
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {result.title}
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            gutterBottom
                          >
                            {result.url}
                          </Typography>
                          <Typography variant="body1">
                            {result.description}
                          </Typography>
                        </Box>
                        <Tooltip title="Copy URL">
                          <IconButton
                            onClick={() => copyToClipboard(result.url)}
                            size="small"
                          >
                            <CopyIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      <Box
                        sx={{
                          display: 'flex',
                          gap: 1,
                          mt: 2,
                          alignItems: 'center',
                        }}
                      >
                        <Chip
                          size="small"
                          label={result.type}
                          color="primary"
                          variant="outlined"
                        />
                        <Typography variant="caption" color="text.secondary">
                          {new Date(result.timestamp).toLocaleString()}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>

        {/* Subscription Dialog */}
        <Dialog 
          open={subscriptionDialogOpen} 
          onClose={() => setSubscriptionDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Upgrade to Premium</DialogTitle>
          <DialogContent>
            <Typography variant="h6" gutterBottom>
              Unlock Unlimited Searches
            </Typography>
            <Typography variant="body1" paragraph>
              Subscribe to our premium plan to enjoy unlimited searches and advanced features:
            </Typography>
            <Box sx={{ my: 2 }}>
              <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                ✅ Unlimited searches
              </Typography>
              <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                ✅ Advanced search filters
              </Typography>
              <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                ✅ Export search results
              </Typography>
              <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                ✅ Priority support
              </Typography>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSubscriptionDialogOpen(false)} color="inherit">
              Not Now
            </Button>
            <Button 
              onClick={handleSubscribe} 
              variant="contained" 
              color="primary"
              startIcon={<LockOpenIcon />}
            >
              Subscribe Now
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default OsintSearch; 