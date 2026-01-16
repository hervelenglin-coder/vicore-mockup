import os
import secrets
from typing import Final

from eurotunnel_datamodel.ConfigManager import Config_Manager
from flask import Flask, abort, redirect, render_template, request, send_from_directory, session
from loguru import logger

# This will also connect to redis
import eurotunnel_web.system_endpoints as system_endpoints
from eurotunnel_web.common_consts import USER_DETAILS_SESSION_VAR
from eurotunnel_web.db_iface import get_car_info_with_wheels, get_train_pass_info_with_cars
from eurotunnel_web.missing_spring_endpoints import get_all_images_for_spring, put_confirmation_status
from eurotunnel_web.models.user import User
from eurotunnel_web.train_pass_endpoints import get_train_pass, get_train_passes, listpasses, load_train_passes
from eurotunnel_web.user_management import authenticate_user, create_users_if_none
from eurotunnel_web.version import VERSION


def get_secret_key() -> str:
    """
    Get secret key from environment variable.
    In development mode, generates a temporary key if not set.
    In production, raises an error if not set.
    """
    key = os.environ.get("FLASK_SECRET_KEY")
    if key:
        return key

    # Check if we're in debug/development mode
    is_debug = os.environ.get("WEB_DEBUG", "False").lower() == "true"
    if is_debug:
        key = secrets.token_hex(32)
        logger.warning("FLASK_SECRET_KEY not set. Using temporary key for development.")
        return key

    # Production mode without key - this is an error
    raise ValueError(
        "FLASK_SECRET_KEY environment variable must be set in production. "
        'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
    )


app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60 * 60

# SECURITY: Secret key from environment variable (P0-1 fix)
app.secret_key = get_secret_key()
fallback_wheel_img_dir: Final[str] = (
    "/mnt/c/Users/Graeme Yeo/Documents/ET Vision/eurotunnel_web/wheelimg"  # Used if the WHEEL_IMG_DIR environment variable is not set
)


create_users_if_none()  # If there are no users in the DB, then create one before we start

# Add system health monitoring functions, from system_endpoints
app.add_url_rule("/get_worst_system_status", view_func=system_endpoints.get_worst_system_status)
app.add_url_rule("/hb_time/<system>", view_func=system_endpoints.system_last_hb_time)
app.add_url_rule("/heartbeat/<system>", view_func=system_endpoints.system_status_full)

app.add_url_rule("/get_all_images_for_spring/<spring_location>", view_func=get_all_images_for_spring)
app.add_url_rule(
    "/put_confirmation_status/<spring_location>/<human_says>", view_func=put_confirmation_status, methods=["PUT"]
)


app.add_url_rule("/getTrainPass/<tpid>", methods=["POST"], view_func=get_train_pass)
# 2 of the 3 parameters here are optional
app.add_url_rule(
    "/loadTrainPasses/<last_shown>/<n_to_fetch>/<installation_id>", methods=["POST"], view_func=load_train_passes
)
app.add_url_rule(
    "/loadTrainPasses/<last_shown>/<n_to_fetch>",
    defaults={"installation_id": None},
    methods=["POST"],
    view_func=load_train_passes,
)
app.add_url_rule(
    "/loadTrainPasses/<last_shown>",
    defaults={"n_to_fetch": None, "installation_id": None},
    methods=["POST"],
    view_func=load_train_passes,
)

app.add_url_rule("/listpasses/", methods=["GET"], view_func=listpasses)
app.add_url_rule("/get_train_passes/", methods=["GET"], view_func=get_train_passes)
# Alias index to be listpasses as well, it's where we want users to land up, and how it previously worked
app.add_url_rule("/", methods=["GET"], view_func=listpasses)


@app.route("/login", methods=["GET"])
def show_login_page():
    return render_template("login.html")


# No cacheing at all for API endpoints.
# but add public for the others
@app.after_request
def add_header(response):
    if "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-store"
    else:
        response.headers["Cache-Control"] = "public"
    return response


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        try:
            login_infos = request.get_json()
            user_name = login_infos["username"]
            logger.debug("User: \t{} attempting login", user_name)
            password = login_infos["password"].encode("utf-8")
            user = authenticate_user(user_name, password)
            if user:
                session[USER_DETAILS_SESSION_VAR] = user.model_dump_json()
                logger.info("User: \t{} logged in ok with id {}", user_name, user.id)
                return "1"
            else:
                return "01"
        except Exception as err:
            logger.exception(err)
            logger.error("Error during login process")
            return "0"


@app.route("/logout", methods=["GET"])
def logout():
    if USER_DETAILS_SESSION_VAR in session:
        del session[USER_DETAILS_SESSION_VAR]
    return render_template("login.html")


@app.route("/test", methods=["GET"])
def test():
    user_json = session.get(USER_DETAILS_SESSION_VAR)
    if not user_json:
        return redirect("/login")
    user_model = User.model_validate_json(user_json)
    return render_template(
        "test.html",
        username=user_model.name,
        version=VERSION,
        system_ids=system_endpoints.get_systems(),
        hb_max_age=Config_Manager.GetCurrentConfig().get_max_age_ms(),
    )


@app.route("/cars/<train_pass_id>/<car_num>")
def carview(train_pass_id, car_num):
    """Gets the carview.html page with data from the supplied <train_pass_id>, and initially showing the supplied <car_num> (starting at 1)"""
    user_json = session.get(USER_DETAILS_SESSION_VAR)
    if not user_json:
        return redirect("/login")
    else:
        user_model = User.model_validate_json(user_json)
        tpic = get_train_pass_info_with_cars(train_pass_id)
        # tpic['img_dir'] = tpic['time_start'].replace(microsecond=0).isoformat().translate(str.maketrans('','',':')) + 'Z' #MAY NOT NEED THIS NOW
        car = get_car_info_with_wheels(train_pass_id, car_num)

        return render_template(
            "carview.html",
            train_pass=tpic,
            current_car=car,
            wheel_img_root="/wheelimg",
            username=user_model.name,
            version=VERSION,
            systems=system_endpoints.get_systems(),
            hb_max_age=Config_Manager.GetCurrentConfig().get_max_age_ms(),
            show_confirm=Config_Manager.GetCurrentConfig().features.show_confirm_missing,
        )


@app.route("/getCar/<train_pass_id>/<car_num>", methods=["POST"])
def get_car(train_pass_id, car_num):
    if request.method == "POST":
        if not session.get(USER_DETAILS_SESSION_VAR):
            abort(403)
        else:
            logger.debug("Getting car and wheels info for car {}", car_num)
            car = get_car_info_with_wheels(train_pass_id, car_num)
            return car


@app.route("/wheelimg/<path:filename>")
def custom_static(filename):
    """
    This effectively maps the /wheelimg directory on the website, to the /mnt/wheelimg directory on the docker container, which gets volume-mapped to where the 'outgoing' images are stored.
    The path of the folder on docker must be supplied as an environment variable called WHEEL_IMG_DIR.
    If WHEEL_IMG_DIR does not exist, it will use fallback_img_dir (variable at the top of this py file), because I am too lazy to set environment variables in Windows.
    """
    if not session.get(USER_DETAILS_SESSION_VAR):
        abort(403)
    else:
        return send_from_directory(os.environ.get("WHEEL_IMG_DIR", fallback_wheel_img_dir), filename)


if __name__ == "__main__":
    """
    Run the Flask application.
    If environment vars are set it will override the default settings (which are host on 127.0.0.1:5000 with Debug mode OFF)
    Environment variables:
        WEB_HOST  : Set to 0.0.0.0 to expose to external IP addresses.
        WEB_PORT  : Default is 5000, but usually gets set to 1234 in our docker container.
        WEB_DEBUG : "True" to turn on debugging output. "False" to turn off (default)
    """
    create_users_if_none()  # If there are no users in the DB, then create one before we start
    app.run(
        host=os.environ.get("WEB_HOST"),
        port=int(os.environ.get("WEB_PORT", 5000)),
        debug=(os.environ.get("WEB_DEBUG", "False").lower() == "true"),
    )
