import json
import time
import os
from main import rag_system

def normalize(text):
    """Đảm bảo text luôn là string, viết thường và sạch khoảng trắng."""
    if text is None: return ""
    return str(text).lower().strip()

def exact_match(pred, gt):
    return normalize(pred) == normalize(gt)

def f1_score(pred, gt):
    pred_tokens = normalize(pred).split()
    gt_tokens = normalize(gt).split()
    if not pred_tokens or not gt_tokens: return 0
    common = set(pred_tokens) & set(gt_tokens)
    if not common: return 0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * precision * recall / (precision + recall)

def run_evaluation():
    input_path = "eval/eval_dataset.json"
    if not os.path.exists(input_path):
        print(f"❌ Error: '{input_path}' không tồn tại.")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return

    em_total = 0
    f1_total = 0
    latency_total = 0
    results = []

    print(f"🚀 Starting Evolution Test for {len(dataset)} samples...")
    print("-" * 60)

    for i, item in enumerate(dataset):
        question = item["question"]
        gt = item["answer"]
        
        raw_pred = ""
        max_retries = 3
        start_time = time.time()

        # --- CƠ CHẾ GỌI RAG AN TOÀN ---
        for attempt in range(max_retries):
            try:
                # Gọi hệ thống RAG của bạn
                raw_pred = rag_system(question)
                
                # Nếu kết quả trả về có lỗi API bên trong (chuỗi chứa mã lỗi)
                if isinstance(raw_pred, str) and ("Error code: 429" in raw_pred or "413" in raw_pred):
                    raise Exception(raw_pred)
                
                break # Thành công thì thoát vòng lặp retry
                
            except Exception as e:
                err_msg = str(e)
                if attempt < max_retries - 1:
                    # Đợi lâu dần (Exponential backoff)
                    wait_time = (attempt + 1) * 10 
                    print(f"⚠️ Cảnh báo Q[{i+1}]: Lỗi API ({err_msg[:50]}...). Thử lại sau {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Thất bại hoàn toàn tại Q[{i+1}]: {err_msg[:100]}")
                    raw_pred = "ERROR_LIMIT_OR_SIZE"

        end_time = time.time()
        latency = end_time - start_time

        # Xử lý Output từ Match Layer (Dict) hoặc Generator (String)
        if isinstance(raw_pred, dict):
            pred = raw_pred.get('content') or raw_pred.get('chunk_text') or str(raw_pred)
        else:
            pred = str(raw_pred)
        
        # Tính toán metric
        em = exact_match(pred, gt)
        f1 = f1_score(pred, gt)

        em_total += em
        f1_total += f1
        latency_total += latency

        print(f"[{i+1}/{len(dataset)}] Q: {question[:50]}...")
        print(f"   > F1: {f1:.4f} | Latency: {latency:.2f}s")
        
        results.append({
            "question": question,
            "f1": f1,
            "em": em,
            "latency": latency,
            "is_error": "ERROR" in pred
        })
        
        # NGHỈ GIỮA CÁC CÂU: Quan trọng để tránh 429 liên tục
        # Nếu câu trước đó chạy quá nhanh (Match Layer), hãy nghỉ lâu hơn một chút
        time.sleep(2 if latency > 5 else 4)

    # --- TỔNG KẾT ---
    total_samples = len(dataset)
    if total_samples == 0: return

    avg_em = em_total / total_samples
    avg_f1 = f1_total / total_samples
    avg_latency = latency_total / total_samples

    print("-" * 60)
    print("🏆 FINAL EVALUATION SUMMARY:")
    print(f"🔹 EM: {avg_em:.4f}")
    print(f"🔹 F1: {avg_f1:.4f}")
    print(f"🔹 Avg Latency: {avg_latency:.2f}s")
    print("-" * 60)

    output = {
        "summary": {
            "avg_em": avg_em,
            "avg_f1": avg_f1,
            "avg_latency": avg_latency,
            "total_samples": total_samples
        },
        "details": results
    }
    
    os.makedirs("eval", exist_ok=True)
    with open("eval/eval_results_summary.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Đã lưu báo cáo vào 'eval/eval_results_summary.json'")

if __name__ == "__main__":
    run_evaluation()