import re

# ===== EXTRACT PENALTY =====
def extract_penalty(text):
    text = text.lower()

    match = re.search(
        r"phạt tiền từ\s+([\d\.\,]+)\s*(?:đồng|đ)?.*?đến\s+([\d\.\,]+)\s*(?:đồng|đ)",
        text
    )
    if match:
        return match.group(0)

    return None


def extract_violation(text):
    text_lower = text.lower()

    match = re.search(r"thực hiện hành vi\s*(.*)", text_lower)
    if match:
        return match.group(1).strip()

    match = re.search(r"hành vi vi phạm:\s*(.*)", text_lower)
    if match:
        return match.group(1).strip()

    match = re.search(r"đối với\s*(.*)", text_lower)
    if match:
        return match.group(1).strip()

    return None


# ===== VEHICLE =====
def detect_vehicle(text):
    text = text.lower()

    mapping = {
        "xe_may": ["xe mô tô", "xe gắn máy", "xe máy điện"],
        "o_to": ["xe ô tô"],
        "xe_dap": ["xe đạp"]
    }

    for k, arr in mapping.items():
        if any(x in text for x in arr):
            return k

    return "chung"

def detect_doc_type(document_name):
    if "168" in document_name:
        return "decree"
    return "law"


# ===== MAIN PARSER =====
def parse_law_text(file_path, document_name):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = []
    doc_type = detect_doc_type(document_name)

    # ===== CHAPTER =====
    chapters = re.split(r"(Chương\s+[IVXLC]+.*?\n)", text)
    current_chapter = "Không xác định"

    for part in chapters:
        if not part.strip():
            continue

        if part.startswith("Chương"):
            current_chapter = part.strip()
            continue

        # ===== ARTICLE =====
        articles = re.split(r"Điều\s+(\d+)\.\s*(.*?)\n", part)

        for i in range(1, len(articles), 3):
            article_num = articles[i]
            article_title = articles[i+1].strip()
            content = articles[i+2] if i+2 < len(articles) else ""

            # ===== CLAUSE =====
            clauses = re.split(r"\n(\d+)\.\s", "\n" + content)

            for j in range(1, len(clauses), 2):
                clause_num = clauses[j]
                clause_text = clauses[j+1]

                # ===== POINT =====
                points = re.split(r"\n([a-zđ])\)\s", "\n" + clause_text)

                if len(points) == 1:
                    points = ["", clause_text]

                for k in range(0, len(points), 2):
                    point_label = points[k].strip()
                    p_content = points[k+1].strip() if k+1 < len(points) else ""

                    if len(p_content) < 15:
                        continue

                    penalty = extract_penalty(p_content)

                    if doc_type == "decree":
                        violation = extract_violation(p_content)
                    else:
                        violation = None
                    vehicle = detect_vehicle(p_content)

                    data.append({
                        "document_name": document_name,
                        "doc_type": doc_type,
                        "chapter": current_chapter,
                        "article": article_num,
                        "article_title": article_title,
                        "clause": clause_num,
                        "point": point_label if point_label else None,
                        "content": p_content,
                        "penalty": penalty,
                        "violation_type": violation,
                        "vehicle_type": vehicle
                    })

    return data