import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Container,
  useTheme,
} from '@mui/material';
import {
  Search as SearchIcon,
  History as HistoryIcon,
  Security as SecurityIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

interface Feature {
  title: string;
  description: string;
  icon: React.ReactElement;
  path: string;
}

const features: Feature[] = [
  {
    title: 'Advanced OSINT Search',
    description: 'Powerful search capabilities with multiple data sources',
    icon: <SearchIcon fontSize="large" />,
    path: '/search/osint',
  },
  {
    title: 'Search History',
    description: 'Track and manage your search history',
    icon: <HistoryIcon fontSize="large" />,
    path: '/history',
  },
  {
    title: 'Secure & Private',
    description: 'Your searches are encrypted and private',
    icon: <SecurityIcon fontSize="large" />,
    path: '/security',
  },
  {
    title: 'Analytics',
    description: 'Detailed analytics and insights from your searches',
    icon: <AnalyticsIcon fontSize="large" />,
    path: '/analytics',
  },
];

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

const Home: React.FC = () => {
  const theme = useTheme();

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(45deg, ${theme.palette.primary.light} 30%, ${theme.palette.primary.main} 90%)`,
          color: 'white',
          py: 8,
          mb: 6,
          borderRadius: 2,
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography
              variant="h2"
              component="h1"
              gutterBottom
              align="center"
              sx={{ fontWeight: 'bold' }}
            >
              Welcome to DorkySearch
            </Typography>
            <Typography variant="h5" align="center" paragraph>
              Your advanced OSINT search platform for comprehensive digital
              investigations
            </Typography>
            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Button
                component={Link}
                to="/search/osint"
                variant="contained"
                size="large"
                sx={{
                  backgroundColor: 'white',
                  color: theme.palette.primary.main,
                  '&:hover': {
                    backgroundColor: theme.palette.grey[100],
                  },
                }}
              >
                Get Started
              </Button>
            </Box>
          </motion.div>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <Grid container spacing={4}>
            {features.map((feature) => (
              <Grid item xs={12} sm={6} md={3} key={feature.title}>
                <motion.div variants={itemVariants}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: '0.3s',
                      '&:hover': {
                        transform: 'translateY(-8px)',
                        boxShadow: 6,
                      },
                    }}
                  >
                    <CardContent>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'center',
                          mb: 2,
                          color: theme.palette.primary.main,
                        }}
                      >
                        {feature.icon}
                      </Box>
                      <Typography
                        gutterBottom
                        variant="h5"
                        component="h2"
                        align="center"
                      >
                        {feature.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        align="center"
                      >
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>

      {/* Pricing Section */}
      <Container maxWidth="lg" sx={{ mt: 8 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Choose Your Plan
        </Typography>
        <Grid container spacing={4} sx={{ mt: 2 }}>
          {['Weekly', 'Monthly', 'Yearly'].map((plan) => (
            <Grid item xs={12} md={4} key={plan}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: ['Weekly', 'Monthly', 'Yearly'].indexOf(plan) * 0.2 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h5" align="center" gutterBottom>
                      {plan}
                    </Typography>
                    <Box sx={{ textAlign: 'center', mt: 2 }}>
                      <Button
                        variant="contained"
                        color="primary"
                        component={Link}
                        to={`/subscribe/${plan.toLowerCase()}`}
                      >
                        Subscribe
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default Home; 