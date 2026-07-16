import os
import fitz  # PyMuPDF
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

FAISS_INDEX_PATH = "faiss_index"
IMAGE_EXTRACTION_DIR = "extracted_images"

def ingest_pdf(pdf_path: str):
    """
    Ingests a PDF: extracts text (for FAISS) and images (for Vision Agent).
    Fails gracefully if OPENAI_API_KEY is missing.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is missing. Cannot generate embeddings.")
        print("Please set it (e.g. export OPENAI_API_KEY='sk-...') and try again.")
        return

    os.makedirs(IMAGE_EXTRACTION_DIR, exist_ok=True)
    
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF {pdf_path}: {e}")
        return

    documents = []
    image_count = 0
    source_name = os.path.basename(pdf_path)
    
    # 1. Text Chunking Setup
    # chunk_size=1000 and overlap=100 is standard to preserve paragraph context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 2. Text Extraction & Chunking (per page)
        page_text = page.get_text()
        page_chunks = text_splitter.split_text(page_text)
        for chunk in page_chunks:
            documents.append(Document(
                page_content=chunk, 
                metadata={"source": source_name, "page": page_num + 1}
            ))
        
        # 3. Image Extraction (for Vision Agent)
        # Instead of extracting raw embedded images (which misses vector-drawn charts),
        # we render the entire page as a high-res image. This allows the Vision Agent
        # to read tables and vector charts visually, bypassing the need for Camelot.
        pix = page.get_pixmap(dpi=150)
        image_filename = f"{source_name}_page{page_num+1}.png"
        image_filepath = os.path.join(IMAGE_EXTRACTION_DIR, image_filename)
        pix.save(image_filepath)
        image_count += 1
            
    print(f"Extracted {len(doc)} pages, generated {len(documents)} text chunks, and rendered {image_count} page-images from {source_name}.")
    
    if not documents:
        print("No text found to embed.")
        return
        
    # 4. Embedding & FAISS Storage
    print("Generating embeddings and updating FAISS index...")
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        if os.path.exists(FAISS_INDEX_PATH):
            vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            vectorstore.add_documents(documents)
        else:
            vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(FAISS_INDEX_PATH)
        print(f"Successfully ingested {len(documents)} chunks into FAISS.")
    except Exception as e:
        print(f"Embedding/Vector DB operation failed: {e}")

if __name__ == "__main__":
    # Test path
    ingest_pdf("sample.pdf")
