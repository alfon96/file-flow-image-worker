import os
from dotenv import load_dotenv

load_dotenv()


class Context:
    _instance = None

    MONGO_URI: str
    DB_NAME: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.MONGO_URI = os.getenv("MONGO_URI")
            cls._instance.DB_NAME = os.getenv("DB_NAME")
        return cls._instance
