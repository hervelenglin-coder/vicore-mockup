import json
from datetime import datetime
from typing import Final, Sequence

import flask
import pytz
from eurotunnel_datamodel.ConfigManager import Config_Manager
from eurotunnel_datamodel.DatabaseHelpers import get_session
from eurotunnel_datamodel.DataModel import Installation
from sqlalchemy import select

from eurotunnel_web.redis_web import RedisInterfaceWeb

redis_interface = RedisInterfaceWeb()  # Loads the config and creates a redis connection


max_age_seconds: Final[int] = Config_Manager.GetCurrentConfig().max_heartbeat_age_seconds
timezone: Final = pytz.timezone(Config_Manager.GetCurrentConfig().default_timezone)

systems: Sequence[Installation] = []
"""Sequence[Installation]: Systems is a list of available installations

This is populated on load and remains cached.
If we ever add another system we will need to restart the container
"""


# This no longer actually used as an endpoint, but it could be
def get_systems() -> Sequence[Installation]:
    global systems
    if systems:
        return systems
    with get_session() as db_session:
        qry = select(Installation).order_by(Installation.location)
        result = db_session.execute(qry)
        systems = result.scalars().all()
        return systems


def get_worst_system_status() -> str:
    """True is healthy, false is unhealthy"""
    for system in get_systems():
        id = 0
        # If it's cached it's a dict
        # it's we fetch it from the db it's an object
        # this way madness lies, but I've lost all afternoon to shit not being serialisable and life is far too short
        if isinstance(system, Installation):
            id = system.installation_id
        else:
            id = system["installation_id"]
        hb = redis_interface.get_heartbeat(id)
        if not hb:
            # No heartbeat at all is definitely an issue
            return json.dumps(False)
        now_with_tz = datetime.now(timezone)
        if (now_with_tz - hb.time).total_seconds() > max_age_seconds:
            return json.dumps(False)
    return json.dumps(True)


def system_status_full(system: int):
    """Get the full details from the heartbeat file"""
    hb_json_str = redis_interface.get_heartbeat_str(system)
    if hb_json_str:
        response = flask.current_app.response_class(response=hb_json_str, status=200, mimetype="application/json")
    else:
        response = flask.current_app.response_class(status=412)
    return response


def system_last_hb_time(system: int):
    """Get the time of the last heart beat. Displaying page chooses if it's still healthy"""
    hb = redis_interface.get_heartbeat(system)
    if hb:
        dt = hb.time
    else:
        # system should show as no recent heartbeat
        dt = datetime.min
    return dt.isoformat()
