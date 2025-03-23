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

echo "Production build completed successfully!"
echo "To run the application in production mode, use: gunicorn wsgi:app" 