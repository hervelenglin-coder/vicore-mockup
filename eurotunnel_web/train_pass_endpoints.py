from datetime import datetime
from typing import Final

from eurotunnel_datamodel.ConfigManager import Config_Manager
from flask import abort, redirect, render_template, request, session
from loguru import logger

from eurotunnel_web import system_endpoints
from eurotunnel_web.common_consts import USER_DETAILS_SESSION_VAR
from eurotunnel_web.confidence_levels import confidence_interface
from eurotunnel_web.db_iface import (
    get_n_train_passes,
    get_n_train_passes_before,
    get_n_train_passes_before_by_system,
    get_train_pass_info_with_cars,
)
from eurotunnel_web.display_name_iface import generate_train_disp_names
from eurotunnel_web.models.user import User
from eurotunnel_web.version import VERSION

n_trainpass_lazyload: Final[int] = 25  # How many Train Passes to lazy load when the bottom of the list is reached
n_trainpass_initial: Final[int] = 50  # How many Train Passes in the list initially


def listpasses():
    """Shows the systemview.html page, for selecting Train Pass"""
    user_json = session.get(USER_DETAILS_SESSION_VAR)
    if not user_json:
        return redirect("/login")
    else:

        user_model = User.model_validate_json(user_json)

        return render_template(
            "systemview.html",
            username=user_model.name,
            version=VERSION,
            installations=get_train_passes(),
            systems=system_endpoints.get_systems(),
            hb_max_age=Config_Manager.GetCurrentConfig().get_max_age_ms(),
        )


def get_train_passes():
    """This endpoint is called by systemview to get the list of train passes"""
    tps = get_n_train_passes(n_trainpass_initial)
    if not tps:
        return "No Data Found", 204
    confidence_interface.GetConfidenceInterface().add_train_conf_codes(tps)
    generate_train_disp_names(tps)
    return assign_train_pass_to_system(tps)


def get_train_pass(tpid: int):
    """
    POST request endpoint used by the Javascript called when you click on a Train Pass in the list.
    It loads the Train Pass info from the DB and returns via a reply (which is dealt with by the same JS that called it)
    """
    if request.method == "POST":
        if not session.get(USER_DETAILS_SESSION_VAR):
            abort(403)
        else:
            # pprint(vars(request)) #Prints out all the info from the http request object
            if not tpid:
                logger.error("Trainpass requested without ID. Cant work")
                abort(400, "Must pass trainpass ID")
            return get_train_pass_info_with_cars(tpid)


def load_train_passes(last_shown: str, n_to_fetch: int | None, installation_id: int | None):
    """
    POST request endpoint used by the Javascript called when you scroll to the bottom of the TrainPass list and more items need to be lazy-loaded.
    It loads the Train Pass info from the DB and returns via a reply (which is dealt with by the same JS that called it)
    """
    if request.method == "POST":
        if not session.get(USER_DETAILS_SESSION_VAR):
            abort(403)
        else:
            if not last_shown or last_shown == "undefined":
                logger.error("We need last shown date to be set for this to work")
                abort(500)
            logger.debug("Lazy-loading passes after '{}'", last_shown)
            before_time = datetime.fromisoformat(last_shown)
            n_passes_to_fetch = n_trainpass_lazyload
            if n_to_fetch:
                n_passes_to_fetch = n_to_fetch
            if installation_id:
                tps = get_n_train_passes_before_by_system(n_passes_to_fetch, before_time, installation_id)
            else:
                tps = get_n_train_passes_before(n_passes_to_fetch, before_time)
            confidence_interface.GetConfidenceInterface().add_train_conf_codes(tps)
            generate_train_disp_names(tps)
            if not installation_id:
                res = assign_train_pass_to_system(tps)
            else:
                # no point building a complex list building when it's only one item
                system = next(
                    system
                    for system in system_endpoints.get_systems()
                    if system.installation_id == int(installation_id)
                )
                res = [_make_isntall_dict(system, tps)]
            return res


def _make_isntall_dict(system, tps) -> dict[str, object]:
    return {
        "installation_id": system.installation_id,
        "location": system.location,
        "train_passes": [tp for tp in tps if tp["installation_id"] == system.installation_id],
    }


def assign_train_pass_to_system(tps: list[dict]) -> list[dict[str, object]]:
    """
    Takes a list of train passes, as the come from the db
    and arranges them into a list of systems

    Args:
        tps (list[dict]): a list of train passes, not ordered by system

    Returns:
        list[dict]: a list of dictionaries, installation_id, location and the previous train passes
    """
    res = []
    systems = system_endpoints.get_systems()
    for system in systems:
        row_dict = _make_isntall_dict(system, tps)
        res.append(row_dict)
    return res
