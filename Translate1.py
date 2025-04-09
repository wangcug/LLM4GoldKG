import time
from deep_translator import GoogleTranslator

def translate_text(text, src_lang='zh-CN', dest_lang='en', retries=5, delay=3):
    attempt = 0
    while attempt < retries:
        try:
            translated_text = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
            print(f"successful: {text} -> {translated_text}")
            time.sleep(1)
            return translated_text
        except Exception as e:
            print(f"unsuccessful: {e}. {delay}retry...")
            time.sleep(delay)
            attempt += 1
    print(f"unsuccessful: {text}")
    return text


def process_line(line, translator):
    try:
        line = line.strip().rstrip(',')

        if line.startswith("(") and "{name:" in line:
            entity_start = line.find("(") + 1
            entity_end = line.find(":")
            entity_part = line[entity_start:entity_end].strip()
            label_start = entity_end + 1
            label_end = line.find("{")
            label_part = line[label_start:label_end].strip()
            name_start = line.find('name:"') + 6
            name_end = line.find('"', name_start)
            name_part = line[name_start:name_end].strip()
            translated_entity = translator(entity_part)
            translated_label = translator(label_part)
            translated_name = translator(name_part)
            translated_line = f"({translated_entity}:{translated_label}{{name:\"{translated_name}\"}}),"
            print(f"Original text: {line}")
            print(f"Traslated text: {translated_line}\n")
            return translated_line
        else:
            print(f"Unrecognizable format,skipping: {line}")
            return line
    except Exception as e:
        print(f"Error occurred during processing of the line: {line}，Error: {e}")
        return line

def translate_text_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            translated_line = process_line(line, translate_text)
            outfile.write(translated_line + '\n')
input_file = '111.txt'
output_file = '222.txt'

translate_text_file(input_file, output_file)
print("Translation completed")
