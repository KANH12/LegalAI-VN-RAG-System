import os

from dotenv import load_dotenv
from groq import Groq
from config.settings import USE_LLM

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query, contexts, intent):
    if not contexts:
        return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu luật giao thông."

    # 1. FIX LỖI DICTIONARY: Phải dùng dấu { "key": "value" }
    intent_instructions = {
        "xử phạt": "Tìm chính xác hành vi vi phạm và số tiền phạt. Ưu tiên mức phạt mới nhất từ Nghị định 123.",
        "None": "Tìm chính xác hành vi vi phạm và số tiền phạt dựa trên ngữ cảnh.",
        "giải thích": "Giải thích chi tiết các quy định pháp luật liên quan."
    }

    # Lấy chỉ dẫn, ép kiểu intent về string cho chắc
    specific_instruction = intent_instructions.get(str(intent), "Trả lời chính xác mức phạt và điều khoản.")

    try:
        if isinstance(contexts, list):
            clean_contexts = [c[:1000] for c in contexts[:5]]
            context_text = "\n\n---\n\n".join(clean_contexts)
        else:
            context_text = str(contexts)[:4000] 

        messages = [
        {
            "role": "system", 
            "content": (
                "Bạn là chuyên gia luật giao thông. \n"
                "NHIỆM VỤ: Giải thích ngắn gọn và Tìm mức phạt phù hợp nhất với ngữ cảnh câu hỏi.\n"
                "LƯU Ý: \n"
                "Đảm bảo câu trả lời có sự giống nhau về mặt ngữ nghĩa với câu hỏi ngữ cảnh\n"
                "CHỈ trả lời những gì có trong văn bản, trích dẫn đúng Điều, Khoản. TUYỆT ĐỐI không tự tạo ra câu trả lời.\n"
                "Nếu không tìm được những tài liệu nào liên quan cứ nói là Không tìm thấy nguồn dữ liệu phù hợp"
            )
        },
        {
            "role": "user", 
            "content": f"Ngữ cảnh:\n{context_text}\n\nCâu hỏi: {query}\n\nTrả lời ngay mức phạt và điều khoản."
        }
        ]

        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2
        )
        return res.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Lỗi Generator cụ thể: {e}")

        if isinstance(contexts, list) and len(contexts) > 0:
            return f"Hệ thống đang quá tải (TPM), nhưng dữ liệu tìm thấy có nhắc đến: {contexts[0][:200]}..."
        return "Xin lỗi, hệ thống gặp lỗi khi tạo câu trả lời."