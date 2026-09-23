from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.utils.logging import setup_logger
from backend.services.database import init_db
from backend.routes import upload, chat, extract, compare, report, documents, flows

logger = setup_logger("main")

app = FastAPI(title="AUTOSAR HLD AI Assistant API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init DB
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application...")
    init_db()

# Include routers
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(extract.router)
app.include_router(compare.router)
app.include_router(report.router)
app.include_router(documents.router)
app.include_router(flows.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AUTOSAR HLD AI Assistant API"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
