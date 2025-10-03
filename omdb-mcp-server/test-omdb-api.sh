#!/bin/bash

# Test OMDB API directly to verify it works
API_KEY={YOUR-API-KEY}

echo "Testing OMDB API directly..."
echo "============================="

echo -e "\n1. Testing search..."
curl -s "https://www.omdbapi.com/?apikey=${API_KEY}&s=Matrix" | jq .

echo -e "\n2. Testing get by title..."
curl -s "https://www.omdbapi.com/?apikey=${API_KEY}&t=The%20Matrix&y=1999" | jq .

echo -e "\n3. Testing get by IMDB ID..."
curl -s "https://www.omdbapi.com/?apikey=${API_KEY}&i=tt0133093" | jq .

echo -e "\nDone!"
