from playwright.sync_api import sync_playwright
import time
import os

def crawl_legal_ai_vn():
    print("--- [LegalAI-VN] TASK: EXTRACT ROAD TRAFFIC LAW 2008 ---")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        # Thiết lập User-Agent để tránh bị hệ thống chặn
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        target_url = "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Luat-giao-thong-duong-bo-2008-23-2008-QH12-82203.aspx"
        
        try:
            print(f"Navigating to: {target_url}")
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)

            # Đợi 7 giây để JavaScript render nội dung vào thẻ div.content1
            print("Rendering page content, please wait...")
            time.sleep(7)

            law_content_locator = page.locator(".content1").first

            if law_content_locator.is_visible():
                raw_text = law_content_locator.inner_text()
                
                if len(raw_text) > 500:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    output_path = os.path.join(base_dir, "..", "data", "raw", "road_traffic_law_2008_raw_data.txt")
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(raw_text)
                    
                    print(f"SUCCESS: Data ingested into {output_path}")
                    print(f"Total characters captured: {len(raw_text)}")
                else:
                    print("ERROR: Content is too short. Something went wrong during rendering.")
            else:
                print("ERROR: Could not find the '.content1' container.")

        except Exception as e:
            print(f"Runtime Error: {e}")
        
        finally:
            print("Closing browser...")
            browser.close()

if __name__ == "__main__":
    crawl_legal_ai_vn()