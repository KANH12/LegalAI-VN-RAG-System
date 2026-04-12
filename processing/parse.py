import os
import re
import pandas as pd

def parse_law_text(file_path, document_name):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = []
    
    chapters = re.split(r"(Chương\s+[IVXLCV]+)", text)
    current_chapter = "Không có chương"

    for part in chapters:
        if not part.strip(): continue
        if part.startswith("Chương"):
            current_chapter = part.strip()
            continue

        articles = re.split(r"(Điều\s+(\d+)\.\s*(.*?)\n)", part)
        
        i = 0
        while i < len(articles):
            a_content = articles[i].strip()
            if not a_content: 
                i += 1
                continue
                
            if a_content.startswith("Điều"):
                current_article_num = articles[i+1]
                current_article_title = articles[i+2]
                actual_content = articles[i+3] if (i+3) < len(articles) else ""
                clauses = re.split(r"\n(\d+)\.\s", "\n" + actual_content)
                
                j = 0
                current_clause = None
                while j < len(clauses):
                    c_text = clauses[j].strip()
                    if not c_text:
                        j += 1
                        continue
                    
                    if c_text.isdigit():
                        current_clause = c_text
                        j += 1
                        continue
                    
                    points = re.split(r"\n([a-zđ])\)\s", "\n" + c_text)
                    k = 0
                    current_point = None
                    while k < len(points):
                        p_content = points[k].strip()
                        if not p_content:
                            k += 1
                            continue
                            
                        if len(p_content) == 1 and (p_content.isalpha() or p_content == 'đ'):
                            current_point = p_content
                            k += 1
                            continue
                        
                        if len(p_content) > 5:
                            data.append({
                                "document": document_name,
                                "chapter": current_chapter,
                                "article": current_article_num,
                                "article_title": current_article_title.strip(),
                                "clause": current_clause,
                                "point": current_point,
                                "content": p_content
                            })
                        k += 1
                    j += 1
                i += 4 
            else:
                i += 1
    return data