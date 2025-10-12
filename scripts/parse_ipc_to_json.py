import re
import json
import os

INPUT_FILE = "data/processed/indian_penal_code.txt"  # Path to your IPC text
OUTPUT_FILE = "data/processed/indian_penal_code_structured.json"

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
            # Heuristic: If line contains 'punishment', treat as punishment
            if "punishment" in line.lower():
                current["punishment"] += (line + " ")
            else:
                current["definition"] += (line + " ")
    if current:
        sections.append(current)
    return sections

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    sections = extract_sections(text)
    # Optionally, add keywords (simple split, or use NLP for better results)
    for sec in sections:
        sec["keywords"] = list(set(re.findall(r"\b\w{5,}\b", sec["definition"].lower())))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(sections)} sections to {OUTPUT_FILE}")

if __name__ == "__main__":
    main() 