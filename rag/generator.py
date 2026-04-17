import os

from dotenv import load_dotenv
from groq import Groq
from config.settings import USE_LLM

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query, contexts, intent):
    if not contexts:
        return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu luật giao thông."

    if isinstance(contexts, list):
        context_text = "\n\n---\n\n".join(contexts[:3])
    else:
        context_text = str(contexts)

    try:
        messages = [
        {
            "role": "system",
            "content": """
            Bạn là Robot tra cứu luật giao thông Việt Nam. Chỉ sử dụng thông tin trong [Ngữ cảnh], không bịa đặt.

            NHIỆM VỤ:
            Dựa vào [Ngữ cảnh], hãy thực hiện một trong hai trường hợp sau:

            TRƯỜNG HỢP 1: Nếu [Ngữ cảnh] là QUY ĐỊNH/KHÁI NIỆM (Concept):
            - Giải thích chi tiết khái niệm hoặc quy định đó dựa trên văn bản luật.
            - Không cần ghi "Mức phạt" hay "Tổng tiền".
            - Trình bày rõ ràng, dễ hiểu.

            TRƯỜNG HỢP 2: Nếu [Ngữ cảnh] là HÀNH VI VI PHẠM (Penalty):
            - Trả lời theo FORMAT:
              Hành vi: [Tên hành vi chuẩn]
              - Điều: [Số điều, tên văn bản]
              - Mức phạt: [Con số chính xác]
              Tổng tiền: [Con số chính xác]

            NGUYÊN TẮC:
            - Luôn trích dẫn tên văn bản (ví dụ: Luật đường bộ 2024 hoặc Nghị định 168/2024).
            - Nếu không có thông tin trong [Ngữ cảnh], báo ngay: "Tôi không tìm thấy thông tin này trong dữ liệu".
            """
        },
        {
            "role": "user",
            "content": f"""
            [Ngữ cảnh]: {context_text}

            Câu hỏi: {query}
            
            Hãy trả lời dựa trên [Ngữ cảnh] trên.
            """
        },
        {
            "role": "user",
            "content": f"""
            Ngữ cảnh: {context_text}

            Câu hỏi: {query}
            """
        }
        ]

        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.0
        )

        return res.choices[0].message.content.strip()

    except Exception as e:
        print("Generator lỗi:", e)
        return "Hệ thống lỗi khi tạo câu trả lời."