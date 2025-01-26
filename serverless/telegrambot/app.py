from helpers import Boto3Client,TelegramBotHandler
from typing import Dict, Any
boto3_client = Boto3Client()

bot_token = boto3_client.get_parameter("/Telegram/TokenBot")
telegram_bot_handler = TelegramBotHandler(bot_token)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    return telegram_bot_handler.lambda_handler(event, context)
