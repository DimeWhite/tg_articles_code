import os
from aiogram.types import InputMediaDocument, FSInputFile,  Message
import asyncio
from sheet import Catalogue, Code
from utils import handle_group_errors, cleanup_temp_folder
import aiofiles

class GroupService:
    DESTINATION = os.path.join("src", "exel", "temp")
    def __init__(self, message: Message, destination: str = DESTINATION) -> None:
        self.message = message
        self.destination = destination
        self.result_files = []
        self.text = ""

    @handle_group_errors()
    async def _send_files(self):
        await self.message.answer(text=self.text)

        for i in range(0, len(self.result_files), 10):
            media = [InputMediaDocument(media=FSInputFile(path=path))
                     for path in self.result_files[i:i+10]]
            await self.message.reply_media_group(media)

    def _create_result_file(self, row, codes) -> str:
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "result"
        ws.append([row[0]])
        ws.append([row[5]])

        for code in codes:
            ws.append([code])
            
        path = os.path.join(self.destination, f"codes_{row[0]}.xlsx")
        wb.save(path)
        wb.close()
        return path
    
    async def _download_file(self, doc) -> str:
        file_data = await self.message.bot.get_file(doc.file_id)

        file_bytes = await self.message.bot.download_file(file_data.file_path)
        bytes_read = file_bytes.read()
        local_path = f"{self.destination}/{doc.file_name}"
        async with aiofiles.open(local_path, "wb") as f:
            await f.write(bytes_read)
            return local_path        
 
    @handle_group_errors()
    async def _handle_doc(self, doc):
        article = doc.file_name.split(" ")[0]
        row = await asyncio.to_thread(Catalogue().get_row_by_article, article)
        if row is None:
            self.text += f"{article} не найден в справочнике.\n"
            return
        local_path = await self._download_file(doc)
        codes = await asyncio.to_thread(Code(local_path).get_codes)
        await asyncio.sleep(0.01)
        if not len(codes):
            self.text += f"{article} не найдены коды в файле.\n" 
            return
        current_file = await asyncio.to_thread(self._create_result_file, row, codes) 
        self.result_files.append(current_file)
        
    @cleanup_temp_folder(DESTINATION)
    async def handle_group(self, group) -> None:
        for doc in group:
            await self._handle_doc(doc)
        await self._send_files()
    