import os
import pandas as pd
import re
from processing.parse import parse_law_text
from processing.chunking import build_chunk_text

def create_law_key(row):

    dieu = str(row.get('article', '') or '').strip()
    khoan = str(row.get('clause', '') or '').strip()
    diem = str(row.get('point', '') or '').strip()
    
    if not dieu and not khoan and not diem:
        return "no_key_" + str(row.name) 
        
    return f"{dieu}_{khoan}_{diem}".lower().replace(" ", "")

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

                for item in parsed:
                    item['document_name'] = document_name
                all_data.extend(parsed)

    df = pd.DataFrame(all_data)

    # 1. Build chunk text
    df["chunk_text"] = df.apply(build_chunk_text, axis=1)

    # 2. Xử lý trùng lặp (Overridden)
    print("--- Cleaning Overridden Data (NĐ 100 vs NĐ 123) ---")
    
    # Tạo key định danh
    df['law_key'] = df.apply(create_law_key, axis=1)
    
    # Tìm các key mà NĐ 123 đã cập nhật
    nd123_mask = df['document_name'].str.contains('123', na=False)
    # Chỉ lấy các key hợp lệ (có Điều/Khoản)
    nd123_keys = df[nd123_mask & (df['law_key'] != "no_key")]['law_key'].unique()

    initial_count = len(df)
    
    # LỌC: Bỏ những dòng thuộc NĐ 100 mà đã có key xuất hiện trong NĐ 123
    df = df[~(
        (df['document_name'].str.contains('100', na=False)) & 
        (df['law_key'].isin(nd123_keys))
    )]
    
    print(f"Đã loại bỏ {initial_count - len(df)} dòng dữ liệu cũ bị thay thế.")

    # 3. Clean & Deduplicate
    df = df.dropna(subset=["content"])
    df = df[df["content"].str.len() > 20]
    df = df.drop_duplicates(subset=["chunk_text"])

    df = df.reset_index(drop=True)
    df["chunk_id"] = df.index

    # ===== SAVE =====
    output_dir = os.path.join(base_dir, "..", "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    parquet_path = os.path.join(output_dir, "laws.parquet")
    df.to_parquet(parquet_path, index=False)

    json_path = os.path.join(output_dir, "laws.json")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    print(f"\nSaved parquet to {parquet_path}")
    print(f"Saved json to {json_path}")

if __name__ == "__main__":
    process_all_files()