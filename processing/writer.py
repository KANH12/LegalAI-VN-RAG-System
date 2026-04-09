import os
import pandas as pd
from processing.parse import parse_law_text
from processing.chunking import build_chunk_text

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

    # build chunk (AI step)
    df["chunk_text"] = df.apply(build_chunk_text, axis=1)

    # basic clean
    df = df.dropna(subset=["content"])
    df = df[df["content"].str.len() > 20]

    # deduplicate
    df = df.drop_duplicates(subset=["chunk_text"])

    # id
    df = df.reset_index(drop=True)
    df["chunk_id"] = df.index

    # ===== SAVE =====
    output_dir = os.path.join(base_dir, "..", "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    # save by parquet (main)
    parquet_path = os.path.join(output_dir, "laws.parquet")
    df.to_parquet(parquet_path, index=False)

    # save by json (debug)
    json_path = os.path.join(output_dir, "laws.json")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print(f"\n Saved parquet to {parquet_path}")
    print(f" Saved json to {json_path}")
    print(df.head())


if __name__ == "__main__":
    process_all_files()