import pandas as pd

def build_chunk_text(row):
    parts = []
    if pd.notna(row.get("document")):
        parts.append(f"Văn bản: {row['document']}")
    if pd.notna(row.get("chapter")):
        parts.append(row['chapter'])
    if pd.notna(row.get("article")):
        parts.append(f"Điều {row['article']}")
        if pd.notna(row.get("article_title")):
            parts.append(f"({row['article_title']})")
    if pd.notna(row.get("clause")):
        parts.append(f"Khoản {row['clause']}")
    if pd.notna(row.get("point")):
        parts.append(f"Điểm {row['point']}")
    
    content = str(row.get("content")).strip()
    return " - ".join(parts) + ": " + content