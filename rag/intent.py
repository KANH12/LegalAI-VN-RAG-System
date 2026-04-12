import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_intent(query):
    """
    Phân loại ý định người dùng để hướng dẫn Generator trả lời đúng trọng tâm.
    """
    
    try:
        prompt = f"""
        Bạn là chuyên gia phân loại ý định người dùng cho chatbot Luật Giao thông Việt Nam.
        Hãy phân loại câu hỏi sau vào 1 trong 3 nhóm:
        1. 'penalty': Hỏi về mức phạt, tiền phạt, hình phạt bổ sung, bị tước bằng, giữ xe.
        2. 'definition': Hỏi về khái niệm, định nghĩa, giải thích biển báo, vạch kẻ đường là gì.
        3. 'general': Các câu hỏi chung về quy định, hướng dẫn cách đi đúng luật.

        Câu hỏi: "{query}"

        Chỉ trả về duy nhất 1 từ khóa: 'penalty', 'definition', hoặc 'general'. Không giải thích gì thêm.
        """
        
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        intent = res.choices[0].message.content.strip().lower()
        
        if intent in ['penalty', 'definition', 'general']:
            return intent
            
    except Exception as e:
        print(f"Intent Detection LLM Error: {e}")
