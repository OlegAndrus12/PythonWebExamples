
from .models import Todo, User
from .db import db_session
from utils import hash_password

# CRUD operations on TODO/USER

def get_all_todos(user_id):
    return db_session.query(Todo).filter(Todo.user_id == user_id).all()

def create_todo(title, description, user_id):
    todo = Todo(title=title, description=description, user_id=user_id)
    db_session.add(todo)
    db_session.commit()


def get_user(username):
    user = db_session.query(User).filter(User.username == username).first()
    return user


def create_user(username: str, password: str):
    user = User(username=username, password=hash_password(password))
    db_session.add(user)
    db_session.commit()
    return user

def validate_user(username: str, password: str):
    user = get_user(username)
    if user and user.password == hash_password(password):
        return user
    return None