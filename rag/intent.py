import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_intent(query):
    query_lower = query.lower()
    
    # 1. Logic phân loại nhanh (giữ nguyên)
    intent = "general"
    if any(x in query_lower for x in ["phạt", "bao nhiêu tiền", "mức phạt", "tốn bao nhiêu", "bao nhiêu"]):
        intent = "penalty"
    elif any(x in query_lower for x in ["là gì", "nghĩa là", "định nghĩa", "khái niệm"]):
        intent = "definition"

    # Trong file intent.py, cập nhật lại phần prompt của Groq
    prompt = f"""
        Bạn là chuyên gia pháp luật giao thông Việt Nam.

        NHIỆM VỤ:
        Phân tích câu hỏi và chuyển câu hỏi người dùng sang THUẬT NGỮ PHÁP LUẬT CHUẨN 
        để tra cứu trong Luật đường bộ 2024 và Nghị định 168/2024/NĐ-CP.

        BẢNG QUY ĐỔI THAM KHẢO (DÙNG ĐÚNG CỤM TỪ NÀY):
        - Không đội mũ, quên mũ, không cài quai -> "không đội mũ bảo hiểm cho người đi mô tô, xe máy"
        - Vượt đèn đỏ, đèn vàng -> "không chấp hành hiệu lệnh của đèn tín hiệu giao thông"
        - Uống rượu bia, nồng độ cồn -> "điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn"
        - Đi ngược chiều, đi sai đường -> "đi ngược chiều của đường một chiều"
        - Không xi nhan -> "không có tín hiệu báo hướng rẽ"

        YÊU CẦU:
        1. "violation":
        - Viết lại hành vi theo ngôn ngữ pháp luật Việt Nam (formal, rõ ràng)
        - Không thêm giải thích

        2. "vehicle":
        Chỉ chọn 1 trong các giá trị:
        - "xe_may"
        - "o_to"
        - "xe_dap"
        - "chung"

        QUY TẮC:
        - Trả về DUY NHẤT JSON
        - Không thêm bất kỳ text nào ngoài JSON
        - Không xuống dòng linh tinh
        - Nếu không chắc → giữ nguyên câu hỏi làm violation

        Câu hỏi: "{query}"

        Output:
        {{
        "violation": "...",
        "vehicle": "..."
        }}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", 
            temperature=0, 
            response_format={"type": "json_object"}
        )
        
        extra_data = json.loads(chat_completion.choices[0].message.content)
        
        # DEBUG xem nó rewrite ra cái gì
        print(f"[DEBUG] RAW REWRITE: {extra_data.get('violation')}")
        
        return {
            "intent": intent,
            "violation": extra_data.get("violation", query),
            "vehicle": extra_data.get("vehicle", "chung")
        }
    except Exception as e:
        print(f"[WARN] Groq Intent fail: {e}")
        return {"intent": intent, "violation": query, "vehicle": "chung"}