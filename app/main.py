# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.kiotViet import processing_entry_form as processing
from app.routers.automation_media import automation_media_crawler
from app.routers.five_tech import automation_product_crawler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(processing.router, prefix="/api/kiotViet")
app.include_router(automation_product_crawler.router, prefix="/api/5tech/automation")
app.include_router(automation_media_crawler.router, prefix="/api/automation")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)