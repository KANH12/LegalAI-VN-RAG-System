from playwright.sync_api import sync_playwright
import time
import os

#1. List documents
DOCUMENTS = [
    {
        "name": "law_2024A",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Luat-Duong-bo-2024-588811.aspx",
        "type": "base"
    },
    {
        "name": "law_2024B",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Luat-trat-tu-an-toan-giao-thong-duong-bo-2024-so-36-2024-QH15-444251.aspx",
        "type": "base"
    },
    {

        "name": "decree_168_2024",

        "url": "https://thuvienphapluat.vn/van-ban/Giao-thong-Van-tai/Nghi-dinh-168-2024-ND-CP-xu-phat-vi-pham-hanh-chinh-an-toan-giao-thong-duong-bo-619502.aspx",

        "type": "current"
    }
]

def crawl_multiple_documents():
    print("START MULTI-CRAWL PIPELINE")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        for doc in DOCUMENTS:
            print(f"\n--- Crawling: {doc['name']} ---")

            try:
                page.goto(doc["url"], wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)

                content = page.locator(".content1").first

                if content.is_visible():
                    raw_text = content.inner_text()

                    if len(raw_text) > 500:
                        #build folder path theo type
                        folder_path = os.path.join(base_dir, "..", "data", "raw", doc["type"])
                        
                        # create dict if not exist
                        os.makedirs(folder_path, exist_ok=True)

                        file_path = os.path.join(folder_path, f"{doc['name']}.txt")

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(raw_text)

                        print(f"Saved: {file_path}")
                    else:
                        print("Content too short")

                else:
                    print("Cannot find content")

            except Exception as e:
                print(f"Error: {e}")

        browser.close()
        print("\n DONE ALL DOCUMENTS")

if __name__ == "__main__":
    crawl_multiple_documents()