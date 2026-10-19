from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine("sqlite:///app.db", echo=False)
#DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/nmo"

class Base(DeclarativeBase):
    """Базовый класс моделей."""

class User(Base):
    __table__ = Table("Users", Base.metadata, autoload_with=engine)

def find_user(login, password):
    with Session(engine) as session:
        user = session.scalars(
            select(User).where(User.login == login, User.password == password)
        ).first()
        if user is None:
            return  None
        return {"login": user.login, "role": user.role}
    
def _to_dict(user):
    """Преобразует объект User в словарь для GUI."""

    if user is None:
        return None
    return {
        "id": user.id,
        "login": user.login,
        "password": user.password,
        "role": user.role,
        "full_name": user.full_name,
        "locked": bool(user.is_locked),
    "attempts": user.attempts,
    }
"""Возвращает список всех пользователей."""

def all_users():
    with Session(engine) as session:
        users = session.scalars(select(User).order_by(User.id)).all()
        return [_to_dict(u) for u in users]

"""Ищет пользователя по логину и паролю. Если нет — None."""
def find_user(login, password):
    with Session(engine) as session:
        user = session.scalars(
            select(User).where(User.login == login, User.password == password)
        ).first()
        return _to_dict(user)
"""Возвращает пользователя по логину (или None)."""

def user_by_login(login):
    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        return _to_dict(user)
    
def login_exists(login):
    return user_by_login(login) is not None

def add_user(login, password, role, full_name):
    with Session(engine) as session:
        session.add(
            User(
                login=login,
                password=password,
                full_name=full_name,
                role=role,
                is_locked=0,
                attempts=0,
                is_active=1,
            )
        )
        session.commit()

def update_user(login, password, role, full_name):
    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.password = password
        user.role = role
        user.full_name = full_name
        session.commit()
        return True
    
"""Удаляет пользователя."""
def delete_user(login):
    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        session.delete(user)
        session.commit()
        return True
    
def register_fail(login):
    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.attempts = user.attempts + 1
        if user.attempts >= 3:
            user.is_locked = 1
            session.commit()
            return True
        session.commit()
        return False
    
"""Сбрасывает счётчик неудачных попыток входа."""
def reset_attempts(login):

    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.attempts = 0
        session.commit()
        return True
    
"""Разблокирует пользователя и сбрасывает попытки."""
def unlock_user(login):
    with Session(engine) as session:
        user = session.scalars(select(User).where(User.login == login)).first()
        if user is None:
            return False
        user.is_locked = 0
        user.attempts = 0
        session.commit()
        return True
    