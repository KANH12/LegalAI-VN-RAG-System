def generate_answer(query, contexts):
    if not contexts:
        return "Không tìm thấy thông tin phù hợp."

    return f"Dựa trên luật:\n{contexts[0]}"