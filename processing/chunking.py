import pandas as pd


def build_chunk_text(row):
    parts = []

    parts.append(f"Văn bản: {row['document_name']}")
    parts.append(row["chapter"])

    parts.append(f"Điều {row['article']}")
    if row.get("article_title"):
        parts.append(f"({row['article_title']})")

    if pd.notna(row.get("clause")):
        parts.append(f"Khoản {row['clause']}")

    if pd.notna(row.get("point")):
        parts.append(f"Điểm {row['point']}")

    # 👉 KEY FIX: add violation hint vào chunk
    if pd.notna(row.get("violation_type")):
        parts.append(f"Hành vi: {row['violation_type']}")

    if pd.notna(row.get("penalty")):
        parts.append(f"Mức phạt: {row['penalty']}")

    content = str(row.get("content")).strip()

    return " - ".join(parts) + ": " + content