from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import sys
import logging
from http import HTTPStatus
import dashscope

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_app_token: str = Field(..., env="SLACK_APP_TOKEN")
    rag_app_api_key: str = Field(..., env="RAG_APP_API_KEY")
    rag_app_id: str = Field(..., env="RAG_APP_ID")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
app = App(token=settings.slack_bot_token)


@app.message("")
def message_hello(message, say):
    text = message.get("text", "")
    user = message.get("user", "")
    logger.info(f"Received message from {user}: {text}")

    response = dashscope.Application.call(
        app_id=settings.rag_app_id,
        prompt=text,
        api_key=settings.rag_app_api_key,
    )

    if response.status_code != HTTPStatus.OK:
        logger.error(
            f"request_id={response.request_id}, code={response.status_code}, message={response.message}"
        )
        say(response.message)
    else:
        logger.info(
            f"request_id={response.request_id}, output={response.output}, message={response.usage}"
        )
        say(response.output)


if __name__ == "__main__":
    SocketModeHandler(app, settings.slack_app_token).start()
