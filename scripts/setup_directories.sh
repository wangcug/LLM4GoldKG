#!/bin/bash

BASE_DIR="$HOME/geology_extractor"

echo "=== Create directory structure ==="
mkdir -p "$BASE_DIR"/{input_files,output_results,logs,config}

echo "=== Set directory permissions ==="
find "$BASE_DIR" -type d -exec chmod 755 {} \;


