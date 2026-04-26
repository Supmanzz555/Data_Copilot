#!/bin/bash
# script to run the application 

set -e

echo "🏦 Deep Insights Copilot - Startup Script"
echo "=========================================="

# check the .env file
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo ".env file created. Please edit it and add your GROQ_API_KEY"
        echo "   Then run this script again."
        exit 1
    else
        echo ".env.example not found. Please create .env manually."
        exit 1
    fi
fi

# check required keys
if grep -qi "your_groq_api_key_here" .env || ! grep -q "GROQ_API_KEY=" .env; then
    echo "Please edit .env and add your actual Groq API key."
    echo "Get one at: https://console.groq.com"
    exit 1
fi

if ! grep -q "JINA_API_KEY=" .env; then
    echo "Please add JINA_API_KEY to .env."
    echo "Get one at: https://jina.ai/embeddings"
    exit 1
fi

echo "Configuration verified"
echo ""

# start docker if evrything is set
echo "Starting Docker containers..."
echo "   (Database initialization will happen automatically on first run)"
docker-compose up --build -d

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Access the application at: http://localhost:8000"
echo ""
echo "Useful commands:"
echo "   View logs:        docker-compose logs -f app"
echo "   Run tests:        docker-compose exec app python test_system.py"
echo "   Run dbt manually: docker-compose exec app bash -lc 'cd dbt && dbt run && dbt test'"
echo "   Stop services:    docker-compose down"
echo ""

