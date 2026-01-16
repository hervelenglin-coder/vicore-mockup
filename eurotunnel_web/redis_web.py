from typing import Final

import redis
from eurotunnel_datamodel.ConfigManager import Config_Manager
from eurotunnel_datamodel.redis_models.heartbeat_model import HeartbeatModel
from loguru import logger

from eurotunnel_web.models.display_names_model import Displaynames


class RedisInterfaceWeb:
    """
    Handles redis for the front end.
    Holds a connection
    """

    LABEL_PREFIX: Final[str] = "l:"
    LABEL_RECALCULATE: Final[int] = (
        60 * 60 * 24 * 3
    )  # labels are cached for 3 days , afterwhich point we won't regularly be needing them

    INSTALLS_KEY: Final[str] = "INSTALLS"
    INSTALLS_EXPIRE: Final[int] = 60 * 60  # Installs can live for a hour, reloading is very cheap

    LONG_DISP_NAME: Final[str] = "LongName"
    SHORT_DISP_NAME: Final[str] = "ShortName"

    def __init__(self) -> None:
        config = Config_Manager.GetCurrentConfig().redis
        self.redis = redis.Redis(host=config.host, port=config.port, decode_responses=True)
        self.json = self.redis.json()

    def get_heartbeat(self, system: int) -> HeartbeatModel | None:
        heartbeat_str = self.redis.get(HeartbeatModel.calc_redis_key(system))
        if heartbeat_str:
            heartbeat = HeartbeatModel.model_validate_json(heartbeat_str)
            return heartbeat
        else:
            return None

    def get_heartbeat_str(self, system: int) -> str:
        """Doesn't validate the JSON, just fetches it from redis. Less load"""
        heartbeat_str = self.redis.get(HeartbeatModel.calc_redis_key(system))
        return heartbeat_str

    def set_trainpass_displayname(self, tpid: int, displayNames: Displaynames):
        key = f"{RedisInterfaceWeb.LABEL_PREFIX}:{tpid}"
        display_names_dict = {
            RedisInterfaceWeb.LONG_DISP_NAME: displayNames.long_name,
            RedisInterfaceWeb.SHORT_DISP_NAME: displayNames.short_name,
        }
        self.json.set(key, "$", display_names_dict)
        self.redis.expire(key, RedisInterfaceWeb.LABEL_RECALCULATE)

    def get_trainpass_displayname(self, tpid: int) -> Displaynames | None:
        key = f"{RedisInterfaceWeb.LABEL_PREFIX}:{tpid}"
        try:
            display_names = self.json.get(key, "$")
            if not display_names:
                return None
            display_names_dict: dict[str, str] = display_names[0]  # type: ignore
            return Displaynames(
                display_names_dict[RedisInterfaceWeb.LONG_DISP_NAME],
                display_names_dict[RedisInterfaceWeb.SHORT_DISP_NAME],
            )

        except redis.ResponseError:
            logger.warning("Redis caching confusion, caused by version upgrade")
            self.redis.delete(key)
            return None
