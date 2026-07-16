import os
import fitz  # PyMuPDF
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "faiss_index")
IMAGE_EXTRACTION_DIR = os.path.join(PROJECT_ROOT, "extracted_images")

def ingest_pdf(pdf_path: str):
    """
    Ingests a PDF: extracts text (for FAISS) and images (for Vision Agent).
    Fails gracefully if OPENAI_API_KEY is missing.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is missing. Cannot generate embeddings.")

    os.makedirs(IMAGE_EXTRACTION_DIR, exist_ok=True)
    
    try:
        documents = []
        image_count = 0
        source_name = os.path.basename(pdf_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
        with fitz.open(pdf_path) as doc:
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
                pix = page.get_pixmap(dpi=150)
                image_filename = f"{source_name}_page{page_num+1}.png"
                image_filepath = os.path.join(IMAGE_EXTRACTION_DIR, image_filename)
                pix.save(image_filepath)
                image_count += 1
                
            print(f"Extracted {len(doc)} pages, generated {len(documents)} text chunks, and rendered {image_count} page-images from {source_name}.")
    except Exception as e:
        raise RuntimeError(f"Failed to process PDF {pdf_path}: {e}")
    
    if not documents:
        raise ValueError("No text found to embed.")
        
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
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Embedding/Vector DB operation failed: {e}")

if __name__ == "__main__":
    # Test path
    ingest_pdf("sample.pdf")
