import os
import pandas as pd
from processing.parse import parse_law_text
from processing.chunking import build_chunk_text

def create_law_key(row):
    p = row['point'] if pd.notna(row['point']) else "none"
    c = row['clause'] if pd.notna(row['clause']) else "none"
    return f"{row['article']}_{c}_{p}".lower()

def process_all_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(base_dir, "..", "data", "raw")
    all_data = []

    for root, _, files in os.walk(raw_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                document_name = file.replace(".txt", "")
                print(f" Processing: {document_name}")
                parsed = parse_law_text(file_path, document_name)
                all_data.extend(parsed)

    df = pd.DataFrame(all_data)
    df = df.dropna(subset=["content"])
    df = df[df["content"].str.len() > 5]

    # ===== CHUNK & KEY =====
    df["chunk_text"] = df.apply(build_chunk_text, axis=1)
    df["law_key"] = df.apply(create_law_key, axis=1)

    # ===== LOGIC OVERCOMING OLD LAWS =====
    old_mask = df["document_name"].str.contains(r"law_2024A|law2024B", regex=True, na=False)
    new_mask = df["document_name"].str.contains("168", na=False)
    nd168_keys = df[new_mask]["law_key"].unique()
    
    df = df[~(old_mask & df["law_key"].isin(nd168_keys))]

    # ===== DEDUP & ID =====
    df = df.drop_duplicates(subset=["chunk_text"])
    df = df.reset_index(drop=True)
    df["chunk_id"] = df.index

    # ===== SAVE =====
    output_dir = os.path.join(base_dir, "..", "data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    df.to_parquet(os.path.join(output_dir, "laws.parquet"), index=False)
    df.to_json(os.path.join(output_dir, "laws.json"), orient="records", force_ascii=False, indent=2)

    print(f" DONE: Total {len(df)} chunks processed.")

if __name__ == "__main__":
    process_all_files()