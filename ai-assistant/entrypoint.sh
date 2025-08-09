#!/bin/bash

# Start Ollama daemon in the foreground
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
until curl -s http://localhost:11434 > /dev/null; do
  echo "Waiting for Ollama to start..."
  sleep 2
done

# Pull required models
ollama pull llama3
ollama pull vicuna

# Wait for Ollama to exit (keeps container alive)
wait $OLLAMA_PID
