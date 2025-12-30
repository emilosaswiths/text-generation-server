import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Config & Logger
from app.config import settings
from app.core.logger import get_logger
from app.core.model_loader import load_model
from app.core.blip_loader import load_blip
from app.core.emotion_loader import load_emotion_model

# API Routers
from app.api.caption import router as caption_router
from app.api.chat_recommendation import router as chat_recommendation_router

#NATS
from app.nats.chat_recommendation_consumer import start_chat_recommendation_consumer
from app.nats.monthly_blip_consumer import start_monthly_blip_consumer
from app.nats.reminder_notification_consumer import start_reminder_notification_consumer




logger = get_logger("text_generation_server")


consumer_tasks: list[asyncio.Task] = []

# -------------------------------
# Lifespan (startup / shutdown)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup ----
    logger.info("Starting Text Generation Server")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")

    try:
        await asyncio.to_thread(load_model)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise e
    try:
        await asyncio.to_thread(load_blip)
        logger.info("BLIP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load BLIP model: {e}")
        raise e
    
      



    consumers = [
        start_chat_recommendation_consumer(),
        start_monthly_blip_consumer(),
        start_reminder_notification_consumer(),
    ]
    for consumer in consumers:
        task = asyncio.create_task(consumer)
        consumer_tasks.append(task)

    logger.info("All NATS consumers started successfully")

    yield

    # ---- Shutdown ----
    logger.info("Shutting down Text Generation Server")
    # Later:
    # - Close NATS connections
    # - Free GPU memory


# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url="/redoc" if settings.ENV != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(caption_router, prefix="/api/v1")
app.include_router(chat_recommendation_router, prefix="/api/v1")

# -------------------------------
# Health Check
# -------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV
    }


# -------------------------------
# Entry Point
# -------------------------------
# def start():
#     import uvicorn

#     logger.info("Launching Uvicorn server")

#     uvicorn.run(
#         "app.main:app",
#         host=settings.HOST,
#         port=settings.PORT,
#         reload=settings.ENV == "development",
#         log_level="info",
#     )


# if __name__ == "__main__":
#     start()
