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
            Bạn là Robot tra cứu luật giao thông Việt Nam chỉ nói những thứ có trong context, không được tự ý bịa.

            NHIỆM VỤ:
            1. Trích xuất chính xác thông tin từ [Ngữ cảnh] được cung cấp.
            2. Tuyệt đối KHÔNG sử dụng kiến thức bên ngoài, không tự bịa tên Nghị định, không tự bịa mức phạt.
            3. Nếu [Ngữ cảnh] không chứa mức phạt cụ thể cho phương tiện người dùng hỏi, hãy báo: "Không tìm thấy mức phạt cụ thể trong dữ liệu".

            NGUYÊN TẮC TRẢ LỜI:
            - Tên văn bản: Phải lấy đúng từ context.
            - Mức phạt: Phải là con số có trong context.
            - Nếu người dùng hỏi xe máy, chỉ lấy mức phạt của xe máy (mô tô).

            FORMAT:
            Hành vi: [Tên hành vi chuẩn]
            - Điều: [Số điều, tên văn bản]
            - Mức phạt: [Con số chính xác]
            
            Tổng tiền: [Tính toán nếu có nhiều hành vi, nếu không thì ghi mức phạt chính]
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