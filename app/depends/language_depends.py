# app/depends/language_depends.py

from fastapi import Header


async def get_language(
    accept_language: str | None = Header(default="en")
) -> str:

    if not accept_language:
        return "en"

    lang = accept_language.split(",")[0].lower()

    supported = ["en", "ar", "hi"]

    return lang if lang in supported else "en"