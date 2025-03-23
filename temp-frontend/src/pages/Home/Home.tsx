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
  Security as SecurityIcon,
  Speed as SpeedIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';

const features = [
  {
    title: 'Advanced OSINT Search',
    description: 'Powerful Google dorking capabilities for finding sensitive information online.',
    icon: <SearchIcon fontSize="large" />,
    path: '/search/osint',
  },
  {
    title: 'Domain Intelligence',
    description: 'Comprehensive domain analysis including WHOIS, DNS, and security assessment.',
    icon: <SecurityIcon fontSize="large" />,
    path: '/search/domain',
  },
  {
    title: 'People Search',
    description: 'Find detailed information about individuals using multiple data sources.',
    icon: <PeopleIcon fontSize="large" />,
    path: '/search/people',
  },
  {
    title: 'Fast Results',
    description: 'Get instant results powered by advanced AI and machine learning.',
    icon: <SpeedIcon fontSize="large" />,
    path: '/tools',
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
          background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          color: 'white',
          py: { xs: 8, md: 12 },
          borderRadius: '0 0 20px 20px',
          mb: 6,
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Typography
              variant="h1"
              sx={{
                fontSize: { xs: '2.5rem', md: '3.5rem' },
                fontWeight: 'bold',
                mb: 2,
              }}
            >
              Faster Google Dorking
            </Typography>
            <Typography
              variant="h2"
              sx={{
                fontSize: { xs: '1.5rem', md: '2rem' },
                mb: 4,
                opacity: 0.9,
              }}
            >
              Find hidden information online with advanced search techniques
            </Typography>
            <Button
              variant="contained"
              color="secondary"
              size="large"
              component={RouterLink}
              to="/register"
              sx={{
                py: 2,
                px: 4,
                fontSize: '1.2rem',
              }}
            >
              Get Started
            </Button>
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
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <motion.div variants={itemVariants}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.2s',
                      '&:hover': {
                        transform: 'translateY(-8px)',
                      },
                    }}
                  >
                    <CardContent>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'center',
                          mb: 2,
                          color: 'primary.main',
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
                        color="textSecondary"
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

        {/* Pricing Section */}
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <Typography variant="h3" gutterBottom>
            Simple, Transparent Pricing
          </Typography>
          <Typography variant="subtitle1" color="textSecondary" paragraph>
            Choose the plan that works best for you
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Weekly
                  </Typography>
                  <Typography variant="h3" color="primary" gutterBottom>
                    $2.99
                  </Typography>
                  <Button
                    variant="outlined"
                    color="primary"
                    component={RouterLink}
                    to="/subscribe/weekly"
                    fullWidth
                  >
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card
                sx={{
                  transform: 'scale(1.05)',
                  border: `2px solid ${theme.palette.primary.main}`,
                }}
              >
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Monthly
                  </Typography>
                  <Typography variant="h3" color="primary" gutterBottom>
                    $9.99
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    component={RouterLink}
                    to="/subscribe/monthly"
                    fullWidth
                  >
                    Best Value
                  </Button>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Yearly
                  </Typography>
                  <Typography variant="h3" color="primary" gutterBottom>
                    $29.99
                  </Typography>
                  <Button
                    variant="outlined"
                    color="primary"
                    component={RouterLink}
                    to="/subscribe/yearly"
                    fullWidth
                  >
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
};

export default Home; 