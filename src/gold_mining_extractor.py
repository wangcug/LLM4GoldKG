import os
import time
import json
import requests
import fitz  # PyMuPDF
from tqdm import tqdm
from datetime import datetime

# ========== Configuration ==========
INPUT_DIR = os.path.expanduser("~/geology_extractor/input_files")
OUTPUT_DIR = os.path.expanduser("~/geology_extractor/output_results")
LOG_DIR = os.path.expanduser("~/geology_extractor/logs")
PROMPT_FILE = os.path.expanduser("~/geology_extractor/config/prompt.txt")

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-r1:70b"  
# =============================

class GoldMiningExtractor:
    def __init__(self):
        self.create_directories()
        self.prompt_template = self.load_prompt()
        self.log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

        with open(self.log_file, "a") as f:
            f.write(f"=== System startup time：{datetime.now()} ===\n")

    def create_directories(self):
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)

    def load_prompt(self):
        try:
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ Unable to load the Prompt file: {e}")
            exit(1)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry)
        with open(self.log_file, "a") as f:
            f.write(entry + "\n")

    def send_to_ollama_chat(self, messages, max_retries=3):
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 6144
            }
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
                response.raise_for_status()
                return response.json().get("message", {}).get("content", "")
            except requests.exceptions.RequestException as e:
                self.log_message(f"retry {attempt+1}/{max_retries} fail: {e}")
                time.sleep(5 * (attempt + 1))

        self.log_message("❌ Reach the maximum retry count and abandon the request.")
        return None

    def extract_entities_relations(self, content):
        try:
            short_content = content[:10000]

            messages = [
                {"role": "user", "content": f"Please read the following geological article and use it in the following instructions：\n\n{short_content}"},
                {"role": "user", "content": self.prompt_template}
            ]

            return self.send_to_ollama_chat(messages)

        except Exception as e:
            self.log_message(f"Extraction failed: {e}")
            return None
            
    def extract_final_result(self, raw_response):
        try:
            start_marker = "```markdown"
            end_marker = "```"
            
            start_idx = raw_response.find(start_marker)
            if start_idx == -1:
                start_marker = "```"
                start_idx = raw_response.find(start_marker)
            
            if start_idx != -1:
                end_idx = raw_response.find(end_marker, start_idx + len(start_marker))
                
                if end_idx != -1:
                    table_content = raw_response[start_idx + len(start_marker):end_idx].strip()
                    
                    if "Label 1" in table_content and "Entity 1" in table_content:
                        return table_content
            
            table_start = raw_response.find("| Label 1 |")
            if table_start != -1:
                table_end = raw_response.find("\n\n", table_start)  
                if table_end == -1:
                    table_end = len(raw_response)
                return raw_response[table_start:table_end].strip()
                
            self.log_message(f"⚠️ NO valid table structure was found.Original response preview: {raw_response[:200]}...")
            return None
            
        except Exception as e:
            self.log_message(f"Result analysis failed: {e}")
            return None

    def process_file(self, file_path):
        filename = os.path.basename(file_path)
        self.log_message(f"Start processing the files: {filename}")

        try:
            if filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            elif filename.endswith(".pdf"):
                doc = fitz.open(file_path)
                content = "".join(page.get_text() for page in doc)
            else:
                self.log_message(f"Skip unsupported file types: {filename}")
                return False

            raw_result = self.extract_entities_relations(content)
            if not raw_result:
                self.log_message(f"❌ The model returned an empty result: {filename}")
                return False
                
            final_table = self.extract_final_result(raw_result)
            if not final_table:
                self.log_message(f"❌ Unable to extract valid table: {filename}")
                return False

            output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}_result.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"Literature: {filename}\n")
                f.write("Extraction time: {0}\n\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                f.write(final_table)  
            
            self.log_message(f"✅ Extraction successful.Result written: {output_path}")
            return True
        except Exception as e:
            self.log_message(f"Failure in handling: {e}")
            return False

    def run(self):
        self.log_message("=== Start the extraction process ===")
        self.log_message(f"Input Directory：{INPUT_DIR}")
        self.log_message(f"Output directory：{OUTPUT_DIR}")
        self.log_message(f"Current prompt preview：{self.prompt_template[:200]}...")

        files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith((".pdf", ".txt"))]
        if not files:
            self.log_message("⚠️ No files to be processed were found.")
            return

        success = 0
        for f in tqdm(files, desc="Handle the literature files"):
            if self.process_file(f):
                success += 1

        total = len(files)
        self.log_message("\n=== Processing completed ===")
        self.log_message(f"Total number of files: {total}")
        self.log_message(f"Number of successful extraction: {success}")
        self.log_message(f"Number of unsuccessful extraction: {total - success}")
        self.log_message(f"Success rate: {success / total * 100:.2f}%")
        self.log_message(f"Log file path: {self.log_file}")

if __name__ == "__main__":
    print("=== Gold Deposit Geological Entities and their Relationships Extraction System ===")
    extractor = GoldMiningExtractor()
    extractor.run()
    print("Processing completed.Please check the output folder.")
