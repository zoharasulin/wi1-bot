from config import config
from pushover import Client, RequestError  # type: ignore


_client = None

try:
    if config["pushover"]["user_key"] and config["pushover"]["api_key"]:
        _client = Client(
            config["pushover"]["user_key"], api_token=config["pushover"]["api_key"]
        )
except Exception:
    pass


def send(msg: str, title: str = None, url: str = None, priority: int = 0) -> None:
    try:
        if _client:
            _client.send_message(
                msg,
                title=title,
                url=url,
                priority=priority,
                device=config["pushover"]["devices"],
            )
    except RequestError:
        pass
