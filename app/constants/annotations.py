from sqlalchemy import String
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from app.config import CONFIG_SETTINGS

DB_STRING_ENCRYPTION = (String, CONFIG_SETTINGS.ENCRYPTION_KEY, AesEngine, 'pkcs5')

print("DB_STRING_ENCRYPTION configured successfully : ", DB_STRING_ENCRYPTION)