import re

# ===== DETECT DOCUMENT TYPE =====
def detect_doc_type(document_name):
    doc_name_lower = document_name.lower()
    if "168" in doc_name_lower:
        return "decree" 
    if "law_2024a" in doc_name_lower or "law_2024b" in doc_name_lower:
        return "law_concept" 
    return "general"

# ===== EXTRACT CONCEPT (4 TYPES) =====
def extract_concept(text, article_title):
    if not text: 
        return article_title
    
    text_clean = re.sub(r"^\d+[\.\s]+|[a-zđ]\)\s*", "", text).strip()
    text_lower = text_clean.lower()
    
    split_keywords = [" là ", " bao gồm:", " bao gồm "]
    for kw in split_keywords:
        if kw in text_lower:
            idx = text_lower.find(kw)
            concept = text_clean[:idx].strip()
            if 2 < len(concept) and len(concept.split()) < 15:
                return concept.strip(' :;,.“”"\'')

    if "sau đây" in text_lower:
        idx = text_lower.find("sau đây")
        concept = text_clean[:idx].strip()
        stop_words = ["như sau", "các loại", "quy định", "trách nhiệm"]
        for sw in stop_words:
            concept = re.sub(rf"\b{sw}\b", "", concept, flags=re.IGNORECASE).strip()
        return concept.strip(' :;,.“”"\'')

    if "giải thích từ ngữ" not in article_title.lower():
        first_sentence = text_clean.split('.')[0]
        if 3 < len(first_sentence.split()) < 12:
            return first_sentence.strip(' :;,.“”"\'')
        return article_title 

    words = text_clean.split()
    if len(words) > 0:
        return " ".join(words[:6]) + "..." if len(words) > 6 else text_clean
    
    return article_title

# ===== EXTRACT PENALTY (DECREE) =====
def extract_penalty(text):
    text = text.lower()
    match = re.search(
        r"phạt tiền từ\s+([\d\.\,]+)\s*(?:đồng|đ)?.*?đến\s+([\d\.\,]+)\s*(?:đồng|đ)",
        text
    )
    return match.group(0) if match else None

# ===== EXTRACT VIOLATION (DECREE) =====
import re

def extract_violation(text):
    if not text: return None

    text_lower = text.lower()
    text_lower = re.sub(r'[“”"\'«»]', '', text_lower) 
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
        
    stop_phrases = ["một trong các", "hành vi vi phạm", "hành vi", "thực hiện"]
    for phrase in stop_phrases:
        res = res.replace(phrase, "").strip()
    
    res = res.strip(' :;,.“”"\'')
    
    res = " ".join(res.split())
    
    return res if res else None

# ===== DETECT VEHICLE =====
def detect_vehicle(text):
    text = text.lower()
    mapping = {
        "xe_may": ["xe mô tô", "xe gắn máy", "xe máy điện"],
        "o_to": ["xe ô tô"],
        "xe_dap": ["xe đạp"]
    }
    for k, arr in mapping.items():
        if any(x in text for x in arr): return k
    return "chung"

# ===== MAIN PARSE =====
def parse_law_text(file_path, document_name):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = []
    doc_type = detect_doc_type(document_name)
    
    # ===== SPLIT CHAPTERS =====
    chapters = re.split(r"(Chương\s+[IVXLC]+.*?\n)", text)
    current_chapter = "Không xác định"

    for part in chapters:
        if not part.strip(): continue
        if part.startswith("Chương"):
            current_chapter = part.strip()
            continue

        # ===== SPLIT ARTICLES =====
        articles = re.split(r"Điều\s+(\d+)\.\s*(.*?)\n", part)

        for i in range(1, len(articles), 3):
            art_num = articles[i]
            art_title = articles[i+1].strip()
            content = articles[i+2] if i+2 < len(articles) else ""

            # ===== SPLIT CLAUSES =====
            clauses = re.split(r"\n(\d+)\.\s", "\n" + content)

            for j in range(1, len(clauses), 2):
                cls_num = clauses[j]
                cls_text = clauses[j+1].strip()
                is_parent = "sau đây" in cls_text.lower()

                if doc_type == "law_concept":
                    v_type = extract_concept(cls_text, art_title)
                    p_val = None
                else:
                    v_type = extract_violation(cls_text)
                    p_val = extract_penalty(cls_text)

                # ===== SPLIT POINT =====
                points = re.split(r"\n([a-zđ])\)\s", "\n" + cls_text)

                if len(points) == 1:
                    if len(cls_text) < 15: continue
                    data.append({
                        "document_name": document_name, "chapter": current_chapter,
                        "article": art_num, "article_title": art_title,
                        "clause": cls_num, "point": None, "content": cls_text,
                        "penalty": p_val, "violation_type": v_type,
                        "vehicle_type": detect_vehicle(cls_text), "doc_type": doc_type
                    })
                else:
                    for k in range(1, len(points), 2):
                        p_label = points[k].strip()
                        p_content = points[k+1].strip()
                        if len(p_content) < 10: continue

                        if doc_type == "law_concept":
                            v_final = f"{v_type}: {p_content.split('.')[0]}"
                            p_final = None
                        else:
                            p_final = p_val if (is_parent and p_val) else extract_penalty(p_content)
                            v_current = extract_violation(p_content)
                            v_final = f"{v_type}: {p_content}" if (is_parent and v_type) else v_current

                        data.append({
                            "document_name": document_name, "chapter": current_chapter,
                            "article": art_num, "article_title": art_title,
                            "clause": cls_num, "point": p_label, "content": p_content,
                            "penalty": p_final, "violation_type": v_final,
                            "vehicle_type": detect_vehicle(f"{cls_text} {p_content}"), "doc_type": doc_type
                        })
    return data