
```bash
echo "=== Install system dependencies ==="
sudo apt update
sudo apt install -y python3-pip python3-venv libgl1

echo "=== Install Ollama ==="
curl -fsSL https://ollama.com/install.sh | sh

echo "=== Install model ==="
ollama pull deepseek-r1:70b

echo "=== Create Python virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Install Python dependencies ==="
pip install --upgrade pip
pip install requests PyMuPDF tqdm

echo "=== Installation completed ==="
echo "Start Ollama service: ollama serve"
echo "Run the program: python src/gold_mining_extractor.py"
