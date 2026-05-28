from pathlib import Path
from telegram import Bot
from telegram.constants import ParseMode
from config import get_settings


class TelegramPublisher:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.bot = Bot(self.settings.telegram_bot_token) if self.settings.telegram_bot_token else None

    async def send_message(self, text: str, pin: bool = False) -> int | None:
        if self.settings.dry_run or not self.bot:
            print(f"DRY_RUN telegram message:\n{text}\n")
            return None
        msg = await self.bot.send_message(
            chat_id=self.settings.telegram_channel_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        if pin:
            await self.bot.pin_chat_message(chat_id=self.settings.telegram_channel_id, message_id=msg.message_id, disable_notification=True)
        return msg.message_id

    async def send_photo(self, image_path: Path, caption: str, pin: bool = False) -> int | None:
        if self.settings.dry_run or not self.bot:
            print(f"DRY_RUN telegram photo: {image_path}\n{caption}\n")
            return None
        with image_path.open("rb") as handle:
            msg = await self.bot.send_photo(
                chat_id=self.settings.telegram_channel_id,
                photo=handle,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
            )
        if pin:
            await self.bot.pin_chat_message(chat_id=self.settings.telegram_channel_id, message_id=msg.message_id, disable_notification=True)
        return msg.message_id

    async def edit_message(self, message_id: int, text: str) -> None:
        if self.settings.dry_run or not self.bot:
            print(f"DRY_RUN edit message {message_id}:\n{text}\n")
            return
        await self.bot.edit_message_text(
            chat_id=self.settings.telegram_channel_id,
            message_id=message_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )

    async def delete_message(self, message_id: int) -> None:
        if self.settings.dry_run or not self.bot:
            print(f"DRY_RUN delete message {message_id}")
            return
        await self.bot.delete_message(chat_id=self.settings.telegram_channel_id, message_id=message_id)
