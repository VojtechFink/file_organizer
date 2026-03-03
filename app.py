from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from src.file_organizer import FileOrganizer
from src.image_analyzer import ImageAnalyzer

app = FastAPI(title="File Organizer Web")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Global organizer instance
organizer = None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/set-directory")
async def set_directory(request: Request):
    """Set source directory"""
    global organizer
    data = await request.json()
    source_path = data.get("path")

    if not source_path:
        raise HTTPException(status_code=400, detail="Path is required")

    source_dir = Path(source_path)
    if not source_dir.exists() or not source_dir.is_dir():
        raise HTTPException(status_code=400, detail="Invalid directory path")

    organizer = FileOrganizer(source_dir)
    return {"status": "success", "path": str(source_dir)}


@app.get("/api/statistics")
async def get_statistics():
    """Get directory statistics"""
    global organizer
    if not organizer:
        raise HTTPException(status_code=400, detail="Directory not set")

    stats = organizer.get_statistics()

    # Convert Path objects to strings for JSON serialization
    largest_files = []
    for file_path, size in stats['largest_files']:
        largest_files.append({
            'path': str(file_path),
            'name': file_path.name,
            'size': size,
            'size_mb': round(size / (1024 * 1024), 2)
        })

    stats['largest_files'] = largest_files

    return stats


@app.post("/api/organize-by-type")
async def organize_by_type():
    """Organize files by type"""
    global organizer
    if not organizer:
        raise HTTPException(status_code=400, detail="Directory not set")

    try:
        organizer.organize_by_type()
        return {"status": "success", "message": "Files organized by type"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/organize-by-date")
async def organize_by_date():
    """Organize files by date"""
    global organizer
    if not organizer:
        raise HTTPException(status_code=400, detail="Directory not set")

    try:
        organizer.organize_by_date()
        return {"status": "success", "message": "Files organized by date"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/find-duplicates")
async def find_duplicates():
    """Find duplicate files"""
    global organizer
    if not organizer:
        raise HTTPException(status_code=400, detail="Directory not set")

    try:
        duplicates = organizer.find_duplicates()

        # Convert to serializable format
        result = []
        for hash_value, files in duplicates.items():
            result.append({
                'hash': hash_value,
                'count': len(files),
                'files': [str(f) for f in files],
                'total_size': sum(f.stat().st_size for f in files),
                'wasted_space': sum(f.stat().st_size for f in files[1:])
            })

        return {"duplicates": result, "groups": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/remove-duplicates")
async def remove_duplicates():
    """Remove duplicate files"""
    global organizer
    if not organizer:
        raise HTTPException(status_code=400, detail="Directory not set")

    try:
        removed_count = organizer.remove_duplicates()
        return {
            "status": "success",
            "message": f"Removed {removed_count} duplicate files"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-images")
async def analyze_images():
    """Analyze image quality in current directory"""
    if not organizer:
        raise HTTPException(status_code=400, detail="No directory set")

    try:
        analyzer = ImageAnalyzer(blur_threshold=100.0)
        stats = analyzer.organize_by_quality(organizer.source_dir)

        return {
            "message": f"Analyzed {stats['total_analyzed']} images",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/find-similar-images")
async def find_similar_images():
    """Find similar/duplicate images"""
    if not organizer:
        raise HTTPException(status_code=400, detail="No directory set")

    try:
        analyzer = ImageAnalyzer()
        similar = analyzer.find_similar_images(organizer.source_dir)

        # Format response
        groups = []
        for hash_val, paths in similar.items():
            groups.append({
                "hash": hash_val,
                "count": len(paths),
                "files": [str(p) for p in paths]
            })

        return {
            "groups": len(groups),
            "similar_images": groups
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)