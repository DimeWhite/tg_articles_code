from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import types, Router, F
import asyncio
from service import GroupService

router = Router()

TIMEOUT_SECONDS = 3

class FilesForm(StatesGroup):
    current_group = State()
    timer_task = State()

@router.message(F.content_type == "document")
async def fileHandle(message: types.Message, state: FSMContext):
    async def timer():
        await asyncio.sleep(TIMEOUT_SECONDS)
        data = await state.get_data()
        current_group = data.get("current_group", [])
        if not current_group:
            return
        
        asyncio.create_task(GroupService(message).handle_group(current_group))
        await state.update_data(current_group=[], timer_task=None)


    document = message.document
    if document is None or not document.file_name.endswith((".xlsx", ".xls")):
        await message.reply(f"Файл {document.file_name} должен быть Excel (.xlsx или .xls)")
        return
    data = await state.get_data()
    timer_task: asyncio.Task | None = data.get("timer_task")
    current_group = data.get("current_group", [])

    current_group.append(document)
    await state.update_data(current_group=current_group)

    if timer_task and not timer_task.done():
        timer_task.cancel()

    new_task = asyncio.create_task(timer())
    await state.update_data(timer_task=new_task)
    