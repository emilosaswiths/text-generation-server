import asyncio
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
from nats.js.api import StreamConfig, RetentionPolicy
from app.core.logger import get_logger
from app.config import settings

logger = get_logger("nats_base")

# ----------------------------------------------------
# GLOBAL SINGLETONS (IMPORTANT)
# ----------------------------------------------------
_nc: NATS | None = None
_js: JetStreamContext | None = None
_connect_lock = asyncio.Lock()


class NATSConnection:
    def __init__(self, servers=None):
        self.servers = servers or [settings.nats_url]
        self.user = "app"
        self.secret = "secret"

    # ----------------------------------------------------
    # CONNECT TO NATS + JETSTREAM (SINGLETON)
    # ----------------------------------------------------
    async def connect(self):
        global _nc, _js

        async with _connect_lock:
            # ✅ Already connected → reuse
            if _nc and _nc.is_connected:
                self.nc = _nc
                self.js = _js
                logger.info("Reusing existing NATS connection")
                return

            logger.info("Creating new NATS connection")

            nc = NATS()
            await nc.connect(
                servers=self.servers,
                user=self.user,
                password=self.secret,
                connect_timeout=2,
                reconnect_time_wait=2,
            )

            js = nc.jetstream()

            _nc = nc
            _js = js

            self.nc = nc
            self.js = js

            logger.info("Connected to NATS & JetStream")

    # ----------------------------------------------------
    # NORMAL NATS SUBSCRIBE (CORE)
    # ----------------------------------------------------
    async def subscribe_core(self, subject, callback):
        async def handler(msg):
            data = msg.data.decode()
            logger.info(f"[CORE] Received message: {data}")
            await callback(msg)

        await self.nc.subscribe(subject, cb=handler)
        logger.info(f"[CORE] Subscribed {subject}")

    # ----------------------------------------------------
    # JETSTREAM STREAM CREATION
    # ----------------------------------------------------
    async def ensure_stream(self, stream_name, subjects):
        try:
            await self.js.stream_info(stream_name)
            logger.info(f"Stream '{stream_name}' already exists")
        except Exception:
            await self.js.add_stream(
                StreamConfig(
                    name=stream_name,
                    subjects=subjects,
                    retention=RetentionPolicy.LIMITS,
                    max_msgs=10000,
                )
            )
            logger.info(f"Created JS Stream '{stream_name}'")

    # ----------------------------------------------------
    # JETSTREAM SUBSCRIBE (DURABLE)
    # ----------------------------------------------------
    async def subscribe_js(self, subject, durable, callback):
        async def handler(msg):
            data = msg.data.decode()
            logger.info(f"[JS] Received message: {data}")

            try:
                await callback(data)
                await msg.ack()
                logger.info("[JS] Message acknowledged")
            except Exception:
                logger.exception("JetStream handler failed")

        await self.js.subscribe(
            subject,
            durable=durable,
            cb=handler,
            manual_ack=True
        )

        logger.info(f"[JS] Subscribed {subject} | durable={durable}")

    # ----------------------------------------------------
    # PUBLISH (CORE)
    # ----------------------------------------------------
    async def publish(self, subject, message: str):
        await self.nc.publish(subject, message.encode())
        logger.info(f"[CORE] Published {subject}")

    # ----------------------------------------------------
    # PUBLISH (JETSTREAM)
    # ----------------------------------------------------
    async def publish_js(self, subject, message: str):
        await self.js.publish(subject, message.encode())
        logger.info(f"[JS] Published {subject}")

    # ----------------------------------------------------
    # DRAIN CONNECTION (OPTIONAL)
    # ----------------------------------------------------
    async def drain(self):
        global _nc, _js

        if _nc:
            await _nc.drain()
            logger.info("NATS drained")

        _nc = None
        _js = None
