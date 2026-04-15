import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def rerank(query, contexts):
    if not contexts:
        return []

    context_str = "\n\n".join(
        [f"[{i}] {c}" for i, c in enumerate(contexts)]
    )

    prompt = f"""
    Bạn là chuyên gia luật giao thông Việt Nam.

    Câu hỏi: {query}

    Danh sách ngữ cảnh: {context_str}

    Nhiệm vụ:
    - Chọn tối đa 3 ngữ cảnh liên quan nhất đến câu hỏi
    - Ưu tiên:
        + Có hành vi vi phạm giống câu hỏi
        + Có mức phạt

    Chỉ trả về danh sách index, ví dụ:
    0,2,3
    """

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0  
        )

        output = res.choices[0].message.content.strip()

        indices = [int(i) for i in re.findall(r'\d+', output)]
        indices = [i for i in indices if i < len(contexts)]

        return [contexts[i] for i in indices[:3]] if indices else contexts[:3]

    except Exception as e:
        print(f"Rerank lỗi: {e}")
        return contexts[:3]