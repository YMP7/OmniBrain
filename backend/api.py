from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from .ingestion import ingest_pdf
from .supervisor import omni_brain_app
from langchain_core.messages import HumanMessage

app = FastAPI(title="OmniBrain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"], # * for local dev convenience, usually restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a PDF and triggers the ingestion pipeline."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    temp_uploads_dir = os.path.join(PROJECT_ROOT, "temp_uploads")
    os.makedirs(temp_uploads_dir, exist_ok=True)
    temp_path = os.path.join(temp_uploads_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Trigger minimal ingestion pipeline
        ingest_pdf(temp_path)
        
        return {"message": f"Successfully ingested {file.filename}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query")
async def query_omnibrain(req: QueryRequest):
    """Submits a query to the LangGraph Supervisor."""
    try:
        # Initialize LangGraph state
        initial_state = {
            "messages": [HumanMessage(content=req.query)],
            "intermediate_findings": "",
            "next_agent": "supervisor"
        }
        
        # Execute workflow
        final_state = omni_brain_app.invoke(initial_state)
        
        # Extract the final answer from the synthesizer node
        final_message = final_state["messages"][-1].content
        
        return {
            "answer": final_message,
            "findings": final_state.get("intermediate_findings", "No intermediate findings.")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

frontend_dist = os.path.join(PROJECT_ROOT, "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
