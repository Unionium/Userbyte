import os
import importlib.util
import tomllib
from telethon import TelegramClient

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

api_id = config["api"]["api_id"]
api_hash = config["api"]["api_hash"]
session = config["api"]["session_name"]

client = TelegramClient(session, api_id, api_hash)
client.config = config
client.registry = {}


def load_plugins():
    folder = "modules"
    os.makedirs(folder, exist_ok=True)
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
        name = filename[:-3]
        path = os.path.join(folder, filename)
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.setup(client)
            title = getattr(mod, "info", {}).get("name", name)
            print(f"[+] {title}")
        except Exception as e:
            print(f"[!] {filename}: {e}")


async def main():
    await client.start()
    print("[*] Userbyte started.")
    load_plugins()
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n[*] Stopped.")
