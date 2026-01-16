from eurotunnel_datamodel.DatabaseHelpers import get_session
from eurotunnel_datamodel.DataModel import HumanConfirmations
from flask import Response, abort, jsonify, session
from loguru import logger
from sqlalchemy import exists, func, select

from eurotunnel_web.common_consts import USER_DETAILS_SESSION_VAR
from eurotunnel_web.db_iface import get_all_image_paths_for_spring as db_spring_images
from eurotunnel_web.models.user import User


def get_all_images_for_spring(spring_location: int):
    if not session.get(USER_DETAILS_SESSION_VAR):
        abort(403)

    res = db_spring_images(spring_location)
    return jsonify(res)


def put_confirmation_status(spring_location: int, human_says: str):
    user_json = session.get(USER_DETAILS_SESSION_VAR)
    if not user_json:
        abort(403)
    user_model = User.model_validate_json(user_json)

    # present not absent is a string, following the
    # JS convention, not python
    # using a JSON libary for this seems...overkill
    present_not_absent = False
    if human_says.lower() == "true":
        present_not_absent = True

    logger.debug("Human confirm for: {}", spring_location)
    with get_session() as db_session:
        stmt = exists().where(HumanConfirmations.spring_location_id == spring_location)
        exstmt = select(True).where(stmt)
        res = db_session.scalar(exstmt)
        if res:
            # there is already a confirmation for this spring
            # the interface shouldn't be letting you overwrite it
            return Response(status=409)

        # Postgres function does the donkey work of marking as confirmed
        # It returns the number of unconfirmed missing springs
        # if there are none left (by definition there must have been one)
        # we need to update the UI
        func_statement = func.public.mark_human_confirmed(spring_location, present_not_absent, user_model.name)
        n_remaining = db_session.scalar(func_statement)
        logger.debug("Remaining springs:{}", n_remaining)
        db_session.commit()
        return {"n_remaining": n_remaining}
