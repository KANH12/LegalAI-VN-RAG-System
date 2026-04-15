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
            Bạn là chuyên gia luật giao thông Việt Nam. 
            Đầu tiên hãy viết lại câu hỏi sang câu hỏi theo thuật ngữ của pháp luật và dùng nó để tìm dữ liệu trong context và không tự ý bịa

            NHIỆM VỤ:
            1. Xác định TẤT CẢ hành vi vi phạm trong câu hỏi
            2. Với mỗi hành vi:
            - Trích Điều, Khoản
            - Đưa mức phạt
            3. Nếu có nhiều hành vi → PHẢI cộng tổng tiền

            QUY TẮC:
            - Chỉ dùng dữ liệu trong context
            - Không tự bịa
            - Nếu không có → trả lời: "Không tìm thấy nguồn phù hợp"

            FORMAT:
            1. Hành vi: ...
            - Điều: ...
            - Mức phạt: ...

            2. Hành vi (nếu có thêm, không được trùng với hành vi trước đó): ...
            - Điều: ...
            - Mức phạt: ...

            Tổng tiền (nếu có): ...
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