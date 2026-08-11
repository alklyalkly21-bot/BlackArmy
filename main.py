import json
import os
import threading
import time
from datetime import datetime

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

CONFIG = "config.json"


class TelegramController:
    """User-consented Telegram controller.

    Remote commands are intentionally limited to non-sensitive diagnostics.
    Files/contacts are handled by Android user-facing pickers in the UI.
    """

    SAFE_COMMANDS = {"/ping", "/status", "/help", "/device"}

    def __init__(self, token, chat_id, log):
        self.token = token.strip()
        self.chat_id = str(chat_id).strip()
        self.base = f"https://api.telegram.org/bot{self.token}"
        self.log = log
        self.offset = 0
        self.stop_event = threading.Event()

    def send(self, text):
        try:
            requests.post(
                f"{self.base}/sendMessage",
                data={"chat_id": self.chat_id, "text": text},
                timeout=15,
            ).raise_for_status()
        except Exception as exc:
            self.log(f"Telegram send error: {exc}")

    def device_status(self):
        return (
            "📱 DEVICE STATUS\n"
            f"platform={os.name}\n"
            f"python={__import__('platform').python_version()}\n"
            f"time={datetime.now():%Y-%m-%d %H:%M:%S}\n"
            "remote_shell=disabled\n"
            "silent_collection=disabled"
        )

    def handle(self, text):
        if text == "/ping":
            return "🏓 Pong — BlackArmy Lab is online."
        if text == "/status":
            return "🟢 Controller online."
        if text == "/device":
            return self.device_status()
        if text == "/help":
            return (
                "Available commands:\n"
                "/ping\n/status\n/device\n/help\n\n"
                "Sensitive actions require an Android user-facing picker."
            )
        return "⛔ Command not available."

    def poll(self):
        self.log("Telegram controller started.")
        while not self.stop_event.is_set():
            try:
                r = requests.get(
                    f"{self.base}/getUpdates",
                    params={"offset": self.offset + 1, "timeout": 5},
                    timeout=10,
                )
                data = r.json()
                if not data.get("ok"):
                    time.sleep(2)
                    continue

                for update in data.get("result", []):
                    self.offset = update["update_id"]
                    msg = update.get("message", {})
                    if str(msg.get("chat", {}).get("id")) != self.chat_id:
                        continue
                    text = (msg.get("text") or "").strip()
                    if text:
                        reply = self.handle(text)
                        self.send(reply)
                        self.log(f"Received: {text}")
            except Exception as exc:
                self.log(f"Polling error: {exc}")
                time.sleep(3)

    def start(self):
        self.stop_event.clear()
        threading.Thread(target=self.poll, daemon=True).start()
        self.send("🟢 BlackArmy Lab v3 started.")

    def stop(self):
        self.stop_event.set()


class BlackArmyApp(App):
    def build(self):
        self.controller = None

        root = BoxLayout(
            orientation="vertical",
            padding=18,
            spacing=10,
        )

        root.add_widget(Label(
            text="🔱 BLACKARMY LAB v3",
            font_size="22sp",
            size_hint_y=None,
            height=55,
        ))
        root.add_widget(Label(
            text="User-consented Android test controller",
            size_hint_y=None,
            height=35,
        ))

        self.token = TextInput(
            hint_text="Telegram Bot Token",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=48,
        )
        self.chat_id = TextInput(
            hint_text="Telegram Chat ID",
            multiline=False,
            size_hint_y=None,
            height=48,
        )
        root.add_widget(self.token)
        root.add_widget(self.chat_id)

        self.status = Label(text="Ready.", halign="left")
        root.add_widget(self.status)

        controls = BoxLayout(
            size_hint_y=None,
            height=52,
            spacing=8,
        )
        for text, callback in (
            ("START", self.start_controller),
            ("STOP", self.stop_controller),
            ("SAVE", self.save_config),
        ):
            button = Button(text=text)
            button.bind(on_press=callback)
            controls.add_widget(button)
        root.add_widget(controls)

        # User-facing actions. These do not silently access private data.
        actions = BoxLayout(
            size_hint_y=None,
            height=52,
            spacing=8,
        )

        file_button = Button(text="SELECT FILE")
        file_button.bind(on_press=lambda *_: self.log(
            "Use Android's file picker to choose a file explicitly."
        ))

        contact_button = Button(text="SELECT CONTACT")
        contact_button.bind(on_press=lambda *_: self.log(
            "Use Android's contact picker to choose a contact explicitly."
        ))

        actions.add_widget(file_button)
        actions.add_widget(contact_button)
        root.add_widget(actions)

        self.load_config()
        return root

    def log(self, message):
        Clock.schedule_once(
            lambda dt: setattr(self.status, "text", message)
        )

    def config_path(self):
        return os.path.join(self.user_data_dir, CONFIG)

    def load_config(self):
        try:
            with open(self.config_path(), encoding="utf-8") as f:
                data = json.load(f)
            self.token.text = data.get("token", "")
            self.chat_id.text = data.get("chat_id", "")
        except Exception:
            pass

    def save_config(self, *_):
        with open(self.config_path(), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "token": self.token.text.strip(),
                    "chat_id": self.chat_id.text.strip(),
                },
                f,
            )
        self.log("Configuration saved.")

    def start_controller(self, *_):
        token = self.token.text.strip()
        chat = self.chat_id.text.strip()
        if not token or not chat:
            self.log("Enter Bot Token and Chat ID.")
            return

        self.stop_controller()
        self.save_config()
        self.controller = TelegramController(token, chat, self.log)
        self.controller.start()
        self.log("Controller online.")

    def stop_controller(self, *_):
        if self.controller:
            self.controller.stop()
            self.controller = None
            self.log("Controller stopped.")

    def on_stop(self):
        self.stop_controller()


if __name__ == "__main__":
    BlackArmyApp().run()
