import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Get the root element
const rootElement = document.getElementById('root');

// Render the App component
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(<App />);
}
