import os
import requests

def run():
    api_key = os.getenv("OPENAI_API_KEY")

    print("1. Uploading PDF...")
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(PROJECT_ROOT, "test_data", "financial_report.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    with open(pdf_path, "rb") as f:
        res = requests.post("http://localhost:8000/upload", files={"file": f})
    
    if res.status_code != 200:
        print(f"Upload failed: {res.text}")
        return
    print(f"Upload response: {res.json()}")

    print("\n2. Submitting query...")
    query = "According to the 2023 report, what was the Q3 revenue growth for Asia Pacific? Please check the chart."
    res = requests.post("http://localhost:8000/query", json={"query": query})
    
    if res.status_code != 200:
        print(f"Query failed: {res.text}")
        return
        
    data = res.json()
    print("\n--- Final Answer ---")
    print(data.get("answer", ""))
    print("\n--- Accumulated Findings ---")
    print(data.get("findings", ""))
    print("--------------------\n")

if __name__ == "__main__":
    run()
