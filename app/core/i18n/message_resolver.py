from app.core.i18n.messages import MESSAGES
from app.core.error.message_codes import MessageCode


class MessageResolver:

    @staticmethod
    def resolve(code: MessageCode, lang: str = "en") -> str:
        return MESSAGES.get(code, {}).get(lang, "Unknown message")