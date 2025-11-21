import functools
import asyncio
import aiofiles.os

def handle_group_errors():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            try: 
                return await func(self, *args, **kwargs)
            except PermissionError as e:
                self.text += f"\nОшибка доступа {args[0].file_name}: {e}\n"
                return None
            except Exception as e:
                self.text += f"\nОшибка обработки {args[0].file_name}: {e}\n"
                return None
        return wrapper
    return decorator

def cleanup_temp_folder(DESTINATION):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            finally:
                files = await aiofiles.os.listdir(DESTINATION)
                for filename in files:
                    await aiofiles.os.remove(f"{DESTINATION}/{filename}")
        return wrapper
    return decorator
