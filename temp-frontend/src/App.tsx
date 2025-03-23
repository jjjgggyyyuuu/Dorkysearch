import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme';
import Layout from './components/Layout/Layout';
import Home from './pages/Home/Home';
import OsintSearch from './pages/Search/OsintSearch';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search/osint" element={<OsintSearch />} />
            {/* Add more routes here */}
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
};

export default App; 