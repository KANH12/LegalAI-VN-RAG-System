import os
import re
import pandas as pd

def parse_law_text(file_path, document_name):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = []

    chapters = re.split(r"(Chương\s+[IVXLC]+)", text)
    current_chapter = None

    for part in chapters:
        part = part.strip()

        if part.startswith("Chương"):
            current_chapter = part
            continue

        articles = re.split(r"(Điều\s+(\d+)\.?\s*(.*))", part)

        current_article_num = None
        current_article_title = None

        i = 0
        while i < len(articles):
            a = articles[i].strip()

            if a.startswith("Điều"):
                current_article_num = articles[i+1]
                current_article_title = articles[i+2]
                i += 3
                continue

            clauses = re.split(r"\n(\d+)\.\s", a)
            current_clause = None

            j = 0
            while j < len(clauses):
                c = clauses[j].strip()

                if c.isdigit():
                    current_clause = c
                    j += 1
                    continue

                points = re.split(r"\n([a-z])\)\s", c)
                current_point = None

                k = 0
                while k < len(points):
                    p = points[k].strip()

                    if len(p) == 1 and p.isalpha():
                        current_point = p
                        k += 1
                        continue

                    if len(p) > 20:
                        data.append({
                            "document": document_name,
                            "chapter": current_chapter,
                            "article": current_article_num,
                            "article_title": current_article_title,
                            "clause": current_clause,
                            "point": current_point,
                            "content": p
                        })

                    k += 1

                j += 1

            i += 1

    return data