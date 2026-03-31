from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "OCR Document Reader CV Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    TESSERACT_CMD: str = ""          # leave empty to use system default
    OCR_LANG: str = "eng"            # tesseract language
    DPI: int = 300                   # PDF render DPI
    PREPROCESS: bool = True          # apply OpenCV preprocessing

    class Config:
        env_file = ".env"


settings = Settings()
