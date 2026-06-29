import asyncio
from app.core.database import engine, Base
from app.models.models import User

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())
