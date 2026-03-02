"""
FastAPI application for Agentic RAG Financial Analysis System
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Import modules
from config import settings
from ingestion import extract_pdf, chunk_document
from db import get_chroma_client
from agents import (
    create_plan,
    retrieve_context,
    analyze_context,
    generate_response,
    evaluate_response
)
from utils.weight_decay import compute_adjusted_temperature, compute_retrieval_depth


# Initialize FastAPI app
app = FastAPI(
    title="Agentic RAG Financial Analysis System",
    description="Lightweight agentic RAG system for financial report analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class QueryRequest(BaseModel):
    question: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What was the net profit margin in 2023?"
            }
        }


# Response models
class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int
    status: str


class QueryResponse(BaseModel):
    query: str
    plan: Dict
    executive_summary: str
    analysis: Any
    risk_factors: Any
    confidence: float
    computed_metrics: Optional[Dict[str, Any]] = None
    retry_count: int
    final_weight: float
    status: str


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Agentic RAG Financial Analysis System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    chroma = get_chroma_client()
    doc_count = chroma.count_documents()
    
    return {
        "status": "healthy",
        "documents_indexed": doc_count,
        "ollama_url": settings.OLLAMA_BASE_URL,
        "model": settings.OLLAMA_MODEL
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process PDF file
    
    Args:
        file: PDF file to upload
        
    Returns:
        Upload status and metadata
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Save uploaded file
        upload_path = settings.UPLOADS_DIR / file.filename
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from PDF
        print(f"Extracting text from {file.filename}...")
        pages = extract_pdf(str(upload_path))
        
        # Chunk document
        print(f"Chunking document...")
        chunks = chunk_document(pages, file.filename)
        
        # Store in ChromaDB
        print(f"Storing {len(chunks)} chunks in ChromaDB...")
        chroma = get_chroma_client()
        success = chroma.add_documents(chunks)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store document in database"
            )
        
        return UploadResponse(
            message="PDF processed successfully",
            filename=file.filename,
            chunks_created=len(chunks),
            status="success"
        )
    
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query financial documents using agentic RAG pipeline
    
    Args:
        request: Query request with question
        
    Returns:
        Structured analysis response
    """
    try:
        query = request.question
        print(f"\n{'='*60}")
        print(f"Processing query: {query}")
        print(f"{'='*60}\n")
        
        # PHASE 1: Planning
        print("PHASE 1: Planning...")
        plan = create_plan(query)
        print(f"Plan: {plan}")
        
        # Initialize retry loop
        retry_count = 0
        best_response = None
        evaluation = None
        
        while retry_count <= settings.MAX_RETRIES:
            print(f"\n--- Attempt {retry_count + 1} ---")
            
            # PHASE 2: Retrieval
            print("PHASE 2: Retrieving context...")
            
            # Adjust retrieval depth on retries
            retrieval_depth = settings.TOP_K_CHUNKS
            if retry_count > 0:
                retrieval_depth = compute_retrieval_depth(
                    base_depth=settings.TOP_K_CHUNKS,
                    retry_count=retry_count
                )
            
            chunks, context = retrieve_context(
                query=query,
                top_k=retrieval_depth
            )
            print(f"Retrieved {len(chunks)} chunks")
            
            # PHASE 3: Analysis
            print("PHASE 3: Analyzing...")
            analysis_result = analyze_context(
                context=context,
                intent=plan["intent"]
            )
            computed_metrics = analysis_result.get("computed_metrics", {})
            print(f"Computed metrics: {computed_metrics}")
            
            # PHASE 4: Generation
            print("PHASE 4: Generating response...")
            
            # Adjust temperature on retries
            temperature = settings.LLM_TEMPERATURE
            if retry_count > 0:
                temperature = compute_adjusted_temperature(
                    base_temperature=settings.LLM_TEMPERATURE,
                    retry_count=retry_count
                )
            
            response = generate_response(
                query=query,
                context=context,
                intent=plan["intent"],
                computed_metrics=computed_metrics,
                temperature=temperature
            )
            print(f"Generated response with confidence: {response.get('confidence', 0.0)}")
            
            # PHASE 5: Critique
            print("PHASE 5: Evaluating...")
            evaluation = evaluate_response(
                response=response,
                query=query,
                retry_count=retry_count
            )
            print(f"Evaluation: confidence={evaluation['confidence']}, "
                  f"meets_threshold={evaluation['meets_threshold']}, "
                  f"weight={evaluation['weight']}")
            
            # Store best response
            best_response = response
            
            # Check if retry is needed
            if not evaluation["should_retry"]:
                print("✓ Response meets quality threshold")
                break
            
            print(f"⚠ Confidence below threshold. Retrying with adjusted parameters...")
            retry_count += 1
        
        # Return final response
        return QueryResponse(
            query=query,
            plan=plan,
            executive_summary=best_response.get("executive_summary", ""),
            analysis=best_response.get("analysis", ""),
            risk_factors=best_response.get("risk_factors", ""),
            confidence=best_response.get("confidence", 0.0),
            computed_metrics=best_response.get("computed_metrics"),
            retry_count=retry_count,
            final_weight=evaluation.get("weight", 1.0),
            status="success"
        )
    
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/history")
async def get_query_history():
    """
    Get recent query history
    
    Returns:
        List of recent queries with metadata
    """
    try:
        from agents.critic import CriticAgent
        critic = CriticAgent()
        history = critic.get_history(limit=20)
        
        return {
            "history": history,
            "count": len(history)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.delete("/collection")
async def reset_collection():
    """
    Delete all documents from ChromaDB (for testing)
    
    Returns:
        Status message
    """
    try:
        chroma = get_chroma_client()
        chroma.delete_collection()
        
        # Reinitialize
        chroma._init_collection()
        
        return {
            "message": "Collection reset successfully",
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting collection: {str(e)}"
        )


@app.get("/stats")
async def get_stats():
    """
    Get system statistics
    
    Returns:
        System statistics including document count, chunks, queries processed
    """
    try:
        chroma = get_chroma_client()
        
        # Get total chunks
        total_chunks = chroma.count_documents()
        
        # Get unique documents by checking metadata
        # Query all documents to count unique filenames
        all_docs = chroma.collection.get()
        unique_docs = set()
        if all_docs and all_docs.get('metadatas'):
            for metadata in all_docs['metadatas']:
                if metadata and 'source' in metadata:
                    unique_docs.add(metadata['source'])
        
        doc_count = len(unique_docs)
        
        # Get query history
        from agents.critic import CriticAgent
        critic = CriticAgent()
        history = critic.get_history(limit=1000)
        
        # Calculate average response time from history
        queries_processed = len(history)
        if queries_processed > 0:
            # Calculate average from retry counts (rough estimate)
            avg_response_time = sum(h.get('retry_count', 0) * 2 + 3 for h in history) / queries_processed
        else:
            avg_response_time = 0.0
        
        return {
            "total_documents": doc_count,
            "total_chunks": total_chunks,
            "queries_processed": queries_processed,
            "avg_response_time": round(avg_response_time, 2),
            "status": "healthy"
        }
    
    except Exception as e:
        print(f"Error in /stats: {e}")
        # Return default values on error
        return {
            "total_documents": 0,
            "total_chunks": 0,
            "queries_processed": 0,
            "avg_response_time": 0.0,
            "status": "error"
        }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("Starting Agentic RAG Financial Analysis System")
    print("="*60)
    print(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    print(f"Model: {settings.OLLAMA_MODEL}")
    print(f"ChromaDB: {settings.CHROMA_PERSIST_DIR}")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8888)
