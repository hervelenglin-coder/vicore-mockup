from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import bcrypt
from loguru import logger

from eurotunnel_datamodel.DataModel import Users
from eurotunnel_datamodel.DatabaseHelpers import get_session

from eurotunnel_web.models.user import User




def authenticate_user(username:str, password:str) -> User | None:
    with get_session() as db_session:
        db_user_info = db_session.query(Users).filter(Users.user_name == username).first()
    if db_user_info:
        hashed_password = bcrypt.hashpw(password, db_user_info.password_salt.encode('utf-8'))
        if hashed_password.decode('utf-8') == db_user_info.password_hash:
            result = User(id=db_user_info.user_id,name=db_user_info.user_name)            
            return result
        else:
            return None

   
def create_users_if_none():
    """I create the default users if there aren't any in the DB"""
    #Definitely needs to be better if anyone has the time
    with get_session() as session:
        qry = func.count().select().select_from(Users)        
        n_users = session.execute(qry).scalar()
        logger.info(f"There are {n_users} setup on this system")
        if(n_users == 0):
            logger.info(f"Creating user")
            create_user("eurotunnel","Spr1ngs","Euro Tunnel")

    

def create_user(user_name:str, password: str,display_name_str: str):
     with get_session() as session:
        stmt = select(Users).where(Users.user_name == user_name)
        existing_user =  session.execute(stmt).first()
        if existing_user:
            raise ValueError("User already present")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        new_user = Users(user_name=user_name, display_name=display_name_str,
                         password_hash=hashed_password.decode('utf-8'),
                            password_salt=salt.decode('utf-8'))
        session.add(new_user)
        session.commit()
