from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
from app.core.config import MEDIA_DIR, TEMPLATES_DIR
from app.routers import cooperatives, products, media, generate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coop Site Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten once there's a real frontend origin to lock to
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve uploaded images so the React preview and the /preview endpoint can show them
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
# serve the shared stylesheet for the live preview iframe (/static/style.css)
app.mount("/static", StaticFiles(directory=str(TEMPLATES_DIR)), name="static")

app.include_router(cooperatives.router)
app.include_router(products.router)
app.include_router(media.router)
app.include_router(generate.router)


@app.get("/health")
def health():
    return {"status": "ok"}