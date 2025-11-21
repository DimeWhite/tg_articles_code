from aiogram import Router

from . import handler


def get_routers() -> list[Router]:
    return [
        handler.router,
    ]