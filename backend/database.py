from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL接続情報
DATABASE_URL = "postgresql://postgres:mydataproject@localhost:5432/minidatacoach"

# エンジン作成（DBとつなぐ）
engine = create_engine(DATABASE_URL)

# セッション作成（DB操作するためのもの）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデル作成用のベースクラス
Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベースURL（SQLiteならこれでOK！）
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# エンジン作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# セッション作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()
