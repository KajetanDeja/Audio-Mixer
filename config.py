from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    demucs_model: str = Field(
        "mdx_q",
        description="Demucs model (mdx_q | htdemucs_6s | mdx_extra)"
    )
    audio_bitrate: str = Field(
        "192k",
        description="Audio bitrate for remux (e.g. 192k)"
    )
    log_level: str = Field(
        "INFO",
        description="Logging level"
    )

    model_config = SettingsConfigDict(
        env_prefix="ASM_",
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
