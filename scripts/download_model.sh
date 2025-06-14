#!/usr/bin/env bash
# Download the GGUF model for local use
MODEL_URL=${MODEL_URL:-"https://example.com/path/to/meltemi7b.q4km.gguf"}
MODEL_DIR="models"
mkdir -p "$MODEL_DIR"

curl -L "$MODEL_URL" -o "$MODEL_DIR/model.gguf"
