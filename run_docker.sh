#!/bin/bash

# Script to test the Instagram Script-Writer in Docker
echo "Building Docker container..."
docker-compose build

echo "Running Docker container..."
docker-compose up
