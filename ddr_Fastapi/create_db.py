from db import Base, engine
import asyncio


async def create_db():
    """
    coroutine responsible for creating database tables
    """
    try:
        async with engine.begin() as conn:
            from models import Note

            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()
    except Exception as e:
        print("An error occurred while creating the database tables:", e)

try:
    asyncio.run(create_db())
except KeyboardInterrupt:
    print("Execution interrupted by the user")
except Exception as e:
    print("An error occurred during execution:", e)