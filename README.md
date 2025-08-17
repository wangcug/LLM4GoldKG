# Gold Deposit Geological Entities and their Semantic Relationships Extraction System 

Based on the locally deployed DeepSeek-R1 large language model, automatically extract gold deposit geological entities and their relationships from geological literature(PDF/TXT).

## ✨ Functional characteristics

- Support automatic parsing of PDF/TXT files
- Use the DeepSeek-R1 70b model for entities and their relationships extraction
- Automatically generate structured table results

## ⚙️ System Requirements

   - Ubuntu 20.04+
   - Recommendation:128GB of memory(required for the 70b model)
   - At least 50GB of available disk sapce
   - Python 3.8+
   - Ollama service

## ⚙️ Configuration options

### 1. Model configuration

Make the modifications in `src/gold_mining_extractor.py`

```python
# Model Name（Can be replaced with other models supported by ollama）
MODEL_NAME = "deepseek-r1:70b" 

# Inference parameters
options = {
    "temperature": 0.2,    # Temperature (0-1)
    "num_ctx": 6144         # Length of the context
}
```

### 2. Prompt

Edit configuration file：
```
~/geology_extractor/config/prompt.txt
```

## 📂 File structure

```
geology_extractor/
├── src/                          # Soure code
├── config/                       # Prompt
├── docs/                         # Documents
├── scripts/                      # Auxiliary script
├── tests/                        # Test file
├── .gitignore                    # Gitignore
├── LICENSE                       # Open source license
├── README.md                     # This document
└── requirements.txt              # Python dependencies
```

## Quick start

```bash
# Clone repository
git clone https://github.com/wangcug/LLM4GoldKG.git
cd LLM4GoldKG

# Install dependencies
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh

# Set up the table of contents
chmod +x scripts/setup_directories.sh
./scripts/setup_directories.sh

##⚠️ Usage Notes

1.**Text Truncation**:
-The system automatically truncates to the first 10,000 characters
-For long documents, consider processing them in chunks

2.**Model Performance**:
-The 70B model requires a large amount of memory
-If memory is insufficient, consider using a smaller model: deepseek-r1:35b

3.**Error Handling**:
-All errors are logged in the log file
-Files that fail to process will be skipped

## 📜 Open source license

This project is licensed under the MIT license.

## 📞 Contact information
 wangchb@cug.edu.cn

