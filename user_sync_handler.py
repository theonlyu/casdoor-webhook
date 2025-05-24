import importlib
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_handlers(config):
    handlers = []

    for name, sys_cfg in config.items():
        if not sys_cfg.get("enabled"):
            continue

        try:
            module = importlib.import_module(f"handlers.{name}_handler")
            class_name = f"{name.capitalize()}Handler"
            handler_class = getattr(module, class_name)

            base_url = sys_cfg["base_url"]
            
            # 支持 token 或 basic auth 两种模式
            if "token_env" in sys_cfg:
                token = os.getenv(sys_cfg["token_env"])
                handler_instance = handler_class(base_url, token)
            elif "username" in sys_cfg and "password_env" in sys_cfg:
                username = sys_cfg["username"]
                password = os.getenv(sys_cfg["password_env"])
                handler_instance = handler_class(base_url, username, password)
            else:
                raise ValueError(f"Missing authentication info for system '{name}'")

            handlers.append(handler_instance)

            #token = os.getenv(sys_cfg["token_env"])

            #handlers.append(handler_class(base_url, token))
        except Exception as e:
            print(f"⚠️ Failed to load handler '{name}': {e}")

    return handlers

