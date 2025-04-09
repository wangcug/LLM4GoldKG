import os
input_file = (File Address)
output_file = (File Address)

lines = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        lines.append(line.strip().split('\t'))
print(f"Total of {len(lines)} rows of data.")
result_dict = {}

for line in lines:
    if len(line) >= 5:
        key1, value1 = line[1], line[0]
        key2, value2 = line[4], line[3]

        result_dict[(key1, value1)] = None
        result_dict[(key2, value2)] = None

print(f"Dictionary contains {len(result_dict)} unique keys.")

relationships = set()
for line in lines:
    if len(line) >= 5:
        relationship_tuple = (line[1], line[2], line[4])
        relationships.add(relationship_tuple)

with open(output_file, 'w', encoding='utf-8') as f:
    for idx, (key, value) in enumerate(result_dict.keys()):
        f.write(f'({key}:{value}{{name:"{key}"}})')
        if idx != len(result_dict) - 1:
            f.write(',\n')
        else:
            f.write('\n')
    for idx, (start_node, relationship, end_node) in enumerate(relationships):
        f.write(f'({start_node})-[:{relationship}]->({end_node})')
        if idx != len(relationships) - 1:
            f.write(',\n')
        else:
            f.write('\n')
print("save to", output_file)
