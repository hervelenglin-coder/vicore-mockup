import os

import bcrypt
from eurotunnel_datamodel.DatabaseHelpers import get_session
from eurotunnel_datamodel.DataModel import Users
from loguru import logger
from sqlalchemy import select
from sqlalchemy.sql.expression import func

from eurotunnel_web.models.user import User


def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a user with username and password."""
    with get_session() as db_session:
        db_user_info = db_session.query(Users).filter(Users.user_name == username).first()

    if db_user_info:
        hashed_password = bcrypt.hashpw(password, db_user_info.password_salt.encode("utf-8"))
        if hashed_password.decode("utf-8") == db_user_info.password_hash:
            result = User(id=db_user_info.user_id, name=db_user_info.user_name)
            return result

    return None


def create_users_if_none():
    """
    Create a default user only in development mode.

    SECURITY (P0-2 fix): Default credentials are NOT created in production.
    In production, use the create_user() function or a CLI script to create users.

    Environment variables:
        VICORE_ENV: Set to 'development' to enable default user creation
        VICORE_DEFAULT_USER: Username for default user (default: 'admin')
        VICORE_DEFAULT_PASS: Password for default user (required in dev mode)
    """
    # SECURITY: Never create default users in production
    vicore_env = os.environ.get("VICORE_ENV", "production").lower()

    if vicore_env == "production":
        logger.info("Production mode: skipping default user creation")
        return

    with get_session() as session:
        qry = func.count().select().select_from(Users)
        n_users = session.execute(qry).scalar()
        logger.info(f"There are {n_users} users on this system")

        if n_users == 0:
            # Get credentials from environment variables
            default_user = os.environ.get("VICORE_DEFAULT_USER", "admin")
            default_pass = os.environ.get("VICORE_DEFAULT_PASS")

            if not default_pass:
                logger.error(
                    "VICORE_DEFAULT_PASS not set. Cannot create default user. "
                    "Set VICORE_DEFAULT_PASS environment variable or create user manually."
                )
                return

            logger.warning(f"Development mode: Creating default user '{default_user}'")
            create_user(default_user, default_pass, "Default Admin")


def create_user(user_name: str, password: str, display_name_str: str):
    with get_session() as session:
        stmt = select(Users).where(Users.user_name == user_name)
        existing_user = session.execute(stmt).first()
        if existing_user:
            raise ValueError("User already present")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        new_user = Users(
            user_name=user_name,
            display_name=display_name_str,
            password_hash=hashed_password.decode("utf-8"),
            password_salt=salt.decode("utf-8"),
        )
        session.add(new_user)
        session.commit()
