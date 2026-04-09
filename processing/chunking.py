import pandas as pd

def build_chunk_text(row):
    def safe_str(x):
        return str(x).strip() if pd.notna(x) else None

    parts = [
        safe_str(row.get("chapter")),
        f"Điều {safe_str(row.get('article'))}" if pd.notna(row.get("article")) else None,
        f"Khoản {safe_str(row.get('clause'))}" if pd.notna(row.get("clause")) else None,
        f"Điểm {safe_str(row.get('point'))}" if pd.notna(row.get("point")) else None,
        safe_str(row.get("content"))
    ]

    return " | ".join([p for p in parts if p])