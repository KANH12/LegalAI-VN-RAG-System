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

# ===== EXTRACT VIOLATION =====
def extract_violation(text):
    if not text:
        return None
    
    text_lower = text.lower()
    res = text_lower 

    patterns = [
        r"thực hiện hành vi\s*(.*)",
        r"hành vi vi phạm:\s*(.*)",
        r"đối với\s*(.*)"
    ]
    
    for p in patterns:
        match = re.search(p, text_lower)
        if match:
            res = match.group(1).strip()
            break

    if "sau đây" in res:
        res = res.split("sau đây")[0].strip()

    stop_phrases = [
        "một trong các", 
        "hành vi vi phạm", 
        "hành vi",
        "thực hiện"
    ]
    
    for phrase in stop_phrases:
        res = res.replace(phrase, "").strip()

    res = res.strip(':').strip(',').strip(';').strip()
    
    return res if len(res) > 2 else text_lower

# ===== DETECT VEHICLE =====
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

# ===== MAIN PARSE =====
def parse_law_text(file_path, document_name):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = []
    is_decree = "168" in document_name

    # ===== CHAPTER =====
    chapters = re.split(r"(Chương\s+[IVXLC]+.*?\n)", text)
    current_chapter = "Không xác định"

    for part in chapters:
        if not part.strip(): continue
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
                clause_text = clauses[j+1].strip()

                is_parent_group = "sau đây" in clause_text.lower()
                parent_penalty = extract_penalty(clause_text)
                parent_violation = extract_violation(clause_text) if is_decree else None

                # ===== POINT =====
                points = re.split(r"\n([a-zđ])\)\s", "\n" + clause_text)

                if len(points) == 1:
                    p_content = clause_text
                    if len(p_content) < 15: continue
                    
                    data.append({
                        "document_name": document_name,
                        "chapter": current_chapter,
                        "article": article_num,
                        "article_title": article_title,
                        "clause": clause_num,
                        "point": None,
                        "content": p_content,
                        "penalty": extract_penalty(p_content),
                        "violation_type": extract_violation(p_content) if is_decree else None,
                        "vehicle_type": detect_vehicle(p_content)
                    })
                else:
                    for k in range(1, len(points), 2):
                        point_label = points[k].strip()
                        point_content = points[k+1].strip()
                        if len(point_content) < 10: continue

                        final_penalty = parent_penalty if (is_parent_group and parent_penalty) else extract_penalty(point_content)
                        
                        current_violation = extract_violation(point_content) if is_decree else None
                        if is_parent_group and parent_violation:
                            violation = f"{parent_violation}: {point_content}"
                        else:
                            violation = current_violation

                        data.append({
                            "document_name": document_name,
                            "chapter": current_chapter,
                            "article": article_num,
                            "article_title": article_title,
                            "clause": clause_num,
                            "point": point_label,
                            "content": point_content,
                            "penalty": final_penalty,
                            "violation_type": violation,
                            "vehicle_type": detect_vehicle(f"{clause_text} {point_content}")
                        })
    return data