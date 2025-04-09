from googletrans import Translator
import time
translator = Translator()

try:
    with open('111.txt', 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
except Exception as e:
    print(f"unsuccessful: {e}")
    exit()

translated_lines = []
delay_between_requests = 1
max_retries = 3

def translate_line(i, line):
    retry_count = 0
    translated_successfully = False

    while retry_count < max_retries and not translated_successfully:
        try:
            if line.startswith("(") and ")-[" in line and "]->(" in line:
                line = line.strip()

                start_entity = line.split(")-[:")[0][1:]
                relation = line.split(")-[:")[1].split("]->")[0]
                end_entity = line.split("]->(")[1][:-1]

                translated_start = translator.translate(start_entity, src='zh-cn', dest='en').text
                translated_end = translator.translate(end_entity, src='zh-cn', dest='en').text

                new_line = f"({translated_start})-[:{relation}]->({translated_end})\n"

                translated_lines.append(new_line)

                print(f"translate: {start_entity} -> {translated_start}")
                print(f"translate: {end_entity} -> {translated_end}")

                translated_successfully = True

            else:
                print(f"skipping: {line.strip()}")

            time.sleep(delay_between_requests)
            break

        except Exception as e:
            retry_count += 1
            print(f"unsuccessful: {line.strip()} error: {e}，retry（{retry_count}/{max_retries}）")
            time.sleep(2)

    if not translated_successfully:
        translated_lines.append(f"unsuccessful: {line.strip()} error: {e}\n")

def process_lines():
    for i, line in enumerate(lines):
        translate_line(i, line)
        with open('222.txt', 'a', encoding='utf-8') as outfile:
            outfile.writelines(translated_lines)
        print(f"completed{(i + 1)}行，save to (File Name)")
        translated_lines.clear()
        time.sleep(1)

    print("save to (File Name)")
process_lines()
