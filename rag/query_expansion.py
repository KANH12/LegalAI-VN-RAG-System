import os

from dotenv import load_dotenv
from groq import Groq
from config.settings import USE_LLM

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def expand_query(query):
    standard_terms = ""
    SYNONYMS = {
        # Tín hiệu & Đường xá
        "vượt đèn đỏ": "không chấp hành hiệu lệnh của đèn tín hiệu giao thông",
        "vượt đèn vàng": "không chấp hành hiệu lệnh của đèn tín hiệu giao thông",
        "đi ngược chiều": "đi ngược chiều của đường một chiều hoặc biển cấm đi ngược chiều",
        "sai làn": "đi không đúng phần đường hoặc làn đường quy định",
        "vỉa hè": "điều khiển xe đi trên hè phố",
        "đường cấm": "đi vào khu vực cấm đường có biển hiệu có nội dung cấm",
        
        # Thiết bị & Hành vi
        "mũ bảo hiểm": "không đội mũ bảo hiểm cho người đi mô tô xe máy cài quai không đúng quy cách",
        "điện thoại": "dùng tay điều khiển xe sử dụng điện thoại di động thiết bị âm thanh",
        "không gương": "không có gương chiếu hậu bên trái người điều khiển",
        "buông tay": "buông cả hai tay khi đang điều khiển xe dùng chân điều khiển xe",
        
        # Chất kích thích (Nghị định 168 phạt cực nặng)
        "nồng độ cồn": "điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn",
        "rượu bia": "điều khiển xe trên đường mà trong máu hoặc hơi thở có nồng độ cồn",
        "ma túy": "điều khiển xe trên đường mà trong cơ thể có chất ma túy",
        
        # Giấy tờ
        "không bằng lái": "không có giấy phép lái xe hoặc sử dụng giấy phép không do cơ quan có thẩm quyền cấp",
        "không bảo hiểm": "không có hoặc không mang theo giấy chứng nhận bảo hiểm trách nhiệm dân sự",
        "quên bằng lái": "không mang theo giấy phép lái xe",
        
        # Tốc độ
        "quá tốc độ": "điều khiển xe chạy quá tốc độ quy định",
        "đua xe": "tụ tập để cổ vũ đua xe trái phép đua xe máy trái phép",
        "lạng lách": "lạng lách hoặc đánh võng trên đường bộ",

        # Định danh loại xe 
        "xe máy": "người điều khiển xe mô tô, xe gắn máy các loại xe tương tự xe mô tô",
        "xe đạp": "người điều khiển xe đạp, xe đạp máy xe thô sơ",
        "xe điện": "xe máy điện xe đạp điện",
        "ô tô": "người điều khiển xe ô tô và các loại xe tương tự xe ô tô",
        "xe tải": "xe ô tô tải máy kéo xe chuyên dùng",

        # --- Độ tuổi 
        "chưa đủ 18 tuổi": "người từ đủ 16 tuổi đến dưới 18 tuổi",
        "dưới 18 tuổi": "người từ đủ 16 tuổi đến dưới 18 tuổi",
        "dưới 16 tuổi": "người từ đủ 14 tuổi đến dưới 16 tuổi",
        "17 tuổi": "người từ đủ 16 tuổi đến dưới 18 tuổi",
        "15 tuổi": "người từ đủ 14 tuổi đến dưới 16 tuổi"
    }
    
    query_lower = query.lower()
    for k, v in SYNONYMS.items():
        if k in query_lower:
            standard_terms = v 
            break

    if not USE_LLM:
        return f"{query} {standard_terms}".strip()

    try:
        prompt = f"""Bạn là chuyên gia pháp luật. Hãy chuyển câu hỏi sau thành các từ khóa tìm kiếm.
        ƯU TIÊN cụm từ: '{standard_terms if standard_terms else query}'
        Câu hỏi: {query}
        Trả lời ngắn gọn (dưới 10 từ)."""

        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        rewritten = res.choices[0].message.content.strip()
        
        if ":" in rewritten:
            rewritten = rewritten.split(":")[-1].strip()
            
        rewritten = rewritten.replace('"', '').replace("'", "").replace(".", "").strip()
        
        rewritten = rewritten.lower()
        
        if standard_terms and standard_terms not in rewritten:
            return f"{standard_terms} {rewritten}"
            
        return rewritten

    except Exception as e:
        print("LLM lỗi → fallback")
        return expand_query(query)