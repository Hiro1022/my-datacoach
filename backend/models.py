from pydantic import BaseModel

# ユーザー登録時に受け取るデータ
class UserCreate(BaseModel):
    email: str
    password: str

# ログイン時に受け取るデータ
class UserLogin(BaseModel):
    email: str
    password: str

# ユーザー情報を保存するための内部モデル
class UserInDB(BaseModel):
    email: str
    hashed_password: str
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"  # テーブル名

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
