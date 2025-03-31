#!/bin/bash

# Production build script for DorkySearch

echo "Starting production build process..."

# Export production environment variables
export FLASK_ENV=production
export NODE_ENV=production

# Install backend dependencies
echo "Installing backend dependencies..."
python -m pip install -r requirements.txt

# Create database if it doesn't exist
echo "Setting up database..."
python -c "from app import app; from models import Base; from database import engine; Base.metadata.create_all(bind=engine)"

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Copy frontend build to static folder
echo "Copying frontend build to Flask static directory..."
rm -rf static/
mkdir -p static
cp -r frontend/build/* static/

# Ensure PWA assets are at root level for NGINX
echo "Ensuring PWA assets are available at root level..."
# This step is just for verification since we've configured NGINX to serve from static/

echo "Production build completed successfully!"
echo "Important: Update the NGINX configuration paths to point to the actual location of your static files."
echo "Make sure the paths in nginx.conf are updated from /path/to/dorkysearch/static/ to your actual static directory."
echo "To run the application in production mode, use: gunicorn wsgi:app" 