import asyncio
from handler import get_routers
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "TOKENHERE"

async def main(token=TOKEN):
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(*get_routers())

    bot = Bot(token)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print("Ошибка при poling", e)
    
if __name__ == "__main__":
    asyncio.run(main())