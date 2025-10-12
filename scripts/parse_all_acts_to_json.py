import re
import json
import os

INPUT_DIR = "data/processed/"
OUTPUT_SUFFIX = "_structured.json"

# Regex pattern for section headers (e.g., "Section 378. Theft")
section_pattern = re.compile(r"Section\s+(\d+[A-Z]?)\.\s*(.+)")

def extract_sections(text):
    sections = []
    current = None
    for line in text.splitlines():
        line = line.strip()
        match = section_pattern.match(line)
        if match:
            if current:
                sections.append(current)
            current = {
                "section": f"Section {match.group(1)}",
                "title": match.group(2),
                "definition": "",
                "punishment": "",
                "keywords": []
            }
        elif current:
            if "punishment" in line.lower():
                current["punishment"] += (line + " ")
            else:
                current["definition"] += (line + " ")
    if current:
        sections.append(current)
    return sections

def process_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    sections = extract_sections(text)
    for sec in sections:
        sec["keywords"] = list(set(re.findall(r"\b\w{5,}\b", sec["definition"].lower())))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(sections)} sections to {output_path}")

def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    if not files:
        print("No .txt files found in data/processed/")
        return
    for fname in files:
        input_path = os.path.join(INPUT_DIR, fname)
        base = os.path.splitext(fname)[0]
        output_path = os.path.join(INPUT_DIR, base + OUTPUT_SUFFIX)
        process_file(input_path, output_path)

if __name__ == "__main__":
    main() 