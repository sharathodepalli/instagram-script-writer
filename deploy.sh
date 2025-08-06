#!/bin/bash

# Instagram Script Writer - Deployment Script
set -e

echo "🚀 Instagram Script Writer Deployment Script"
echo "=============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your API keys:"
    echo "  OPENAI_API_KEY=your_key_here"
    echo "  PINECONE_API_KEY=your_key_here"
    echo "  LANGCHAIN_API_KEY=your_key_here"
    exit 1
fi

echo "✅ Environment file found"

# Load environment variables
source .env

# Check required environment variables
required_vars=("OPENAI_API_KEY" "PINECONE_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set in .env file"
        exit 1
    fi
done

echo "✅ Required environment variables found"

# Build and run with Docker Compose
echo "🐳 Building and starting Docker containers..."

# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Build and start
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for service to be healthy
echo "⏳ Waiting for service to be ready..."
sleep 10

# Check if service is running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Service is running!"
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📱 Your app is available at:"
    echo "   • Local: http://localhost:8501"
    echo "   • Network: http://$(hostname -I | awk '{print $1}'):8501"
    echo ""
    echo "📊 To view logs:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    echo "🛑 To stop the service:"
    echo "   docker-compose -f docker-compose.prod.yml down"
else
    echo "❌ Service failed to start. Check logs:"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi