import os
import re
import pandas as pd

def parse_law_text(file_path, document_name):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = []

    chapters = re.split(r"(Chương\s+[IVXLC]+)", text)

    current_chapter = None

    for part in chapters:
        part = part.strip()

        if part.startswith("Chương"):
            current_chapter = part
            continue

        # split Điều
        articles = re.split(r"(Điều\s+\d+\.?.*?)", part)

        current_article = None

        for a in articles:
            a = a.strip()

            if a.startswith("Điều"):
                current_article = a
                continue

            # split Khoản
            clauses = re.split(r"(\n\d+\.\s)", a)

            current_clause = None

            for c in clauses:
                c = c.strip()

                if re.match(r"\d+\.", c):
                    current_clause = c
                    continue

                # split điểm a), b), c)
                points = re.split(r"(\n[a-z]\))", c)

                current_point = None

                for p in points:
                    p = p.strip()

                    if re.match(r"[a-z]\)", p):
                        current_point = p
                        continue

                    if len(p) > 20:
                        data.append({
                            "document": document_name,
                            "chapter": current_chapter,
                            "article": current_article,
                            "clause": current_clause,
                            "point": current_point,
                            "content": p
                        })

    return data

def process_all_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(base_dir, "..", "data", "raw")

    all_data = []

    for root, _, files in os.walk(raw_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                document_name = file.replace(".txt", "")

                print(f"Processing: {document_name}")

                parsed = parse_law_text(file_path, document_name)
                all_data.extend(parsed)

    df = pd.DataFrame(all_data)

    output_path = os.path.join(base_dir, "..", "data", "processed", "laws.parquet")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df.to_parquet(output_path, index=False)

    print(f"✅ Saved processed data to {output_path}")
    print(df.head())


if __name__ == "__main__":
    process_all_files()