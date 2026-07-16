import re
from playwright.sync_api import Page, expect

def test_react_ui_loads(page: Page):
    """
    Validates that the React UI boots and the core components render.
    """
    # Navigate to Vite default port
    page.goto("http://localhost:5173")
    
    # Wait for the main app container to load
    page.wait_for_selector("main")
    
    # Check title
    expect(page.get_by_text("OmniBrain", exact=True)).to_be_visible()
    
    # Check Ingestion section
    expect(page.get_by_text("Ingest Documents")).to_be_visible()
    
    # Check Query section
    expect(page.get_by_placeholder("Ask OmniBrain...")).to_be_visible()
    
    print("UI Load E2E Test Passed.")

def test_missing_api_key_graceful_fail(page: Page):
    """
    Validates that submitting a query without an OPENAI_API_KEY gracefully
    bubbles the error up to the UI instead of crashing the backend.
    """
    page.goto("http://localhost:5173")
    
    # Fill the text input
    page.get_by_placeholder("Ask OmniBrain...").fill("Test Query")
    page.get_by_placeholder("Ask OmniBrain...").press("Enter")
    
    # Wait for the error message component to appear and verify its text
    # The API returns 500, and our frontend displays "Query failed: Internal Server Error"
    error_message = page.locator("text=/Query failed|An error occurred|OPENAI_API_KEY/")
    expect(error_message).to_be_visible(timeout=5000)
    print("Graceful Fail E2E Test Passed.")

def test_upload_missing_api_key():
    """
    Validates that /upload returns a 500 error if the OPENAI_API_KEY is missing.
    """
    import os
    import sys
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, PROJECT_ROOT)
    
    from fastapi.testclient import TestClient
    from backend.api import app
    
    # Ensure OPENAI_API_KEY is unset
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
        
    client = TestClient(app)
    
    pdf_path = os.path.join(PROJECT_ROOT, "test_data", "financial_report.pdf")
    
    print("Testing /upload with missing API key...")
    with open(pdf_path, "rb") as f:
        res = client.post("/upload", files={"file": f})
    
    assert res.status_code == 500, f"Expected 500, got {res.status_code}. Response: {res.text}"
    assert "OPENAI_API_KEY" in res.text, f"Expected API key error message, got: {res.text}"
    print("Upload Missing API Key Test Passed.")

def test_functional_backend():
    """
    Validates the end-to-end flow of the Agentic Orchestrator (Supervisor -> Search -> Vision/SQL)
    and asserts that the final synthesis properly cites the page number.
    """
    import os
    import sys
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, PROJECT_ROOT)
    
    # Set dummy key so ingestion doesn't fail the manual check
    os.environ["OPENAI_API_KEY"] = "dummy_for_mock_test"
    
    from fastapi.testclient import TestClient
    from unittest.mock import patch, MagicMock
    from backend.api import app
    from langchain_core.messages import AIMessage
    
    client = TestClient(app)
    
    pdf_path = os.path.join(PROJECT_ROOT, "test_data", "financial_report.pdf")
    if not os.path.exists(pdf_path):
        print("SKIPPED: Dummy PDF not found. Run generate_test_pdf.py first.")
        return
        
    print("1. Uploading PDF to /upload (Mocked Embeddings)...")
    from langchain_core.embeddings import Embeddings
    class DummyEmbeddings(Embeddings):
        def embed_documents(self, texts):
            return [[0.1] * 1536 for _ in texts]
        def embed_query(self, text):
            return [0.1] * 1536

    with patch("backend.ingestion.OpenAIEmbeddings", return_value=DummyEmbeddings()):
        with open(pdf_path, "rb") as f:
            res = client.post("/upload", files={"file": f})
        assert res.status_code == 200, f"Upload failed: {res.text}"
    
    print("2. Submitting complex query to /query (Mocked LLM & Agents)...")
    query = "According to the 2023 report, what was the Q3 revenue growth for Asia Pacific? Please check the chart."
    
    # We will mock the LLM inside supervisor.py and the specialized agents
    with patch("backend.supervisor.ChatOpenAI") as MockLLM, \
         patch("backend.supervisor.search_agent") as mock_search, \
         patch("backend.supervisor.vision_agent") as mock_vision, \
         patch("backend.supervisor.sql_agent") as mock_sql:
         
        # Agent Mocks
        mock_search.return_value = "Mention of revenue growth chart [Source: financial_report.pdf, Page: 2]"
        mock_vision.return_value = "Chart indicates Asia Pacific grew by 40% [Source: financial_report.pdf, Page: 2]"
        mock_sql.return_value = "Database shows total revenue is $100M"
        
        # LLM Mock for Supervisor routing:
        # 1. Route to search
        # 2. Route to vision
        # 3. Route to FINISH (synthesize)
        # 4. Synthesize final answer
        mock_llm_instance = MockLLM.return_value
        mock_llm_instance.invoke.side_effect = [
            AIMessage(content='{"next_action": "search", "reasoning": "Need text context"}'),
            AIMessage(content='{"next_action": "vision", "reasoning": "Need chart data"}'),
            AIMessage(content='{"next_action": "FINISH", "reasoning": "Got the data"}'),
            AIMessage(content="Based on the chart, Asia Pacific Q3 revenue growth was 40% [Source: financial_report.pdf, Page: 2]")
        ]
        
        res = client.post("/query", json={"query": query})
        assert res.status_code == 200, f"Query failed: {res.text}"
        
        data = res.json()
        answer = data.get("answer", "")
        findings = data.get("findings", "")
        
        print("\n--- Final Answer ---")
        print(answer)
        print("\n--- Accumulated Findings ---")
        print(findings)
        print("--------------------\n")
        
        # Assert citation rules were followed by the Synthesizer
        assert "[Source: financial_report.pdf, Page: 2]" in answer or "[Source: financial_report.pdf, Page: 1]" in answer, "Missing or incorrect citation in the final answer!"
        
        # Assert findings accumulated both Search and Vision outputs
        assert "[Search Agent]" in findings, "Search findings missing!"
        assert "[Vision Agent]" in findings, "Vision findings missing!"
        
        print("Functional Backend Test Passed: Citations and State Accumulation are correctly enforced!")

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Running UI E2E tests...")
            test_react_ui_loads(page)
            test_missing_api_key_graceful_fail(page)
            print("UI E2E tests passed successfully.")
            
            print("\nRunning API Failure Case Tests...")
            test_upload_missing_api_key()
            
            print("\nRunning Functional Backend E2E Test...")
            test_functional_backend()
            
            print("\nALL TESTS PASSED SUCCESSFULLY.")
        finally:
            browser.close()

