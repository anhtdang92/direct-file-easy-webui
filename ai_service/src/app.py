from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging
import os
from pathlib import Path
import shutil
import uuid

from .document_processor import DocumentProcessor
from .tax_analyzer import TaxAnalyzer
from .cache import CacheMiddleware, get_cache, init_cache_warmup, get_cache_warmup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tax Document Analysis API",
    description="API for processing and analyzing tax documents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache and middleware
cache = get_cache()
app.add_middleware(CacheMiddleware, cache=cache)

# Initialize cache warmup
cache_warmup = init_cache_warmup(app, cache)

# Initialize processors
document_processor = DocumentProcessor()
tax_analyzer = TaxAnalyzer()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Start cache warming on application startup."""
    await cache_warmup.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop cache warming on application shutdown."""
    await cache_warmup.stop()

@app.post("/process")
async def process_document(
    file: UploadFile = File(...),
    cache: bool = True
) -> Dict[str, Any]:
    """Process a tax document."""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Save file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document
        result = document_processor.process_document(file_path)
        
        # Clean up
        os.remove(file_path)
        
        return result
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_document(
    doc_type: str,
    text: str,
    cache: bool = True
) -> Dict[str, Any]:
    """Analyze processed document data."""
    try:
        result = tax_analyzer.analyze_document(doc_type, text)
        return result
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/invalidate")
async def invalidate_cache(path: str) -> Dict[str, str]:
    """Invalidate cache for a specific path."""
    try:
        cache = get_cache()
        cache.delete(path)
        return {"status": "success", "message": f"Cache invalidated for {path}"}
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        cache = get_cache()
        warmup = get_cache_warmup()
        return {
            "cache": cache.get_stats(),
            "warmup": warmup.get_stats() if warmup else None
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/warm")
async def warm_cache() -> Dict[str, Any]:
    """Manually trigger cache warming."""
    try:
        warmup = get_cache_warmup()
        if not warmup:
            raise HTTPException(status_code=500, detail="Cache warmup not initialized")
        
        # Trigger warmup
        await warmup._warmup_endpoints()
        
        return {
            "status": "success",
            "message": "Cache warming triggered",
            "stats": warmup.get_stats()
        }
    except Exception as e:
        logger.error(f"Error warming cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 