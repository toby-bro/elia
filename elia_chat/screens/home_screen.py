import datetime
import os
from langchain.schema import HumanMessage, SystemMessage
from textual import on
from textual.app import ComposeResult
from textual.events import ScreenResume
from textual.screen import Screen
from textual.widgets import TextArea

from elia_chat.models import ChatData
from elia_chat.widgets.chat_list import ChatList
from elia_chat.widgets.prompt_input import PromptInput
from elia_chat.chats_manager import ChatsManager
from elia_chat.widgets.app_header import AppHeader
from elia_chat.screens.chat_screen import ChatScreen


class HomeScreen(Screen[None]):
    CSS = """\
ChatList {
    height: 1fr;
    width: 1fr;
    background: $background 15%;
}
"""

    def on_mount(self) -> None:
        self.chats_manager = ChatsManager()

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield PromptInput()
        yield ChatList()

    @on(ScreenResume)
    def reload_screen(self) -> None:
        self.query_one(ChatList).reload_and_refresh()

    @on(ChatList.ChatOpened)
    def open_chat_screen(self, event: ChatList.ChatOpened):
        chat_id = event.chat.id
        assert chat_id is not None
        chat = self.chats_manager.get_chat(chat_id)
        self.app.push_screen(ChatScreen(chat))

    @on(PromptInput.PromptSubmitted)
    def create_new_chat(self):
        system_prompt = os.getenv("ELIA_DIRECTIVE", "You are a helpful assistant.")
        text_area = self.query_one("#prompt", TextArea)
        user_prompt = text_area.text
        text_area.text = ""
        current_time = datetime.datetime.now(datetime.UTC).timestamp()
        chat = ChatData(
            id=None,
            title=None,
            create_timestamp=None,
            model_name="gpt-3.5-turbo",  # TODO - get model from ui
            messages=[
                SystemMessage(
                    content=system_prompt,
                    additional_kwargs={
                        "timestamp": current_time,
                        "recipient": "all",
                    },
                ),
                HumanMessage(
                    content=user_prompt,
                    additional_kwargs={"timestamp": current_time},
                ),
            ],
        )
        chat.id = str(ChatsManager.create_chat(chat_data=chat))
        self.app.push_screen(ChatScreen(chat))
