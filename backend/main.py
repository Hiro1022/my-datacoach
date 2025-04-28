# 必要なライブラリをインポート
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd

import models
from database import SessionLocal, engine

# アプリケーション作成
app = FastAPI(title="Mini DataCoach API")

# データベースにテーブルを作成
models.Base.metadata.create_all(bind=engine)

# セキュリティ設定
SECRET_KEY = "your_secret_key_here"  # 本番では環境変数を使おう！
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2用スキーマ
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# モデル
class UserCreate(BaseModel):
    email: str
    password: str

class UserInDB(BaseModel):
    email: str
    hashed_password: str

class ProtectedResponse(BaseModel):
    msg: str

# DBセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# パスワード関連関数
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# トークン作成関数
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# トークンからユーザー取得
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# エンドポイント定義✍️

# ヘルスチェック
@app.get("/")
def health_check():
    return {"status": "ok"}

# ユーザー登録
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "User registered successfully!"}

# ログイン
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# CSVプレビュー
@app.post("/preview")
async def preview_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    return {
        "columns": list(df.columns),
        "head": df.head().to_dict(orient="records")
    }

# 認証必須エンドポイント
@app.get("/protected", response_model=ProtectedResponse)
def protected_route(current_user: models.User = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.email}! You are authenticated."}

# マイページ（認証必須）
@app.get("/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "user_id": current_user.id
    }

from pydantic import BaseModel

# パスワード更新用のリクエストボディ
class PasswordUpdate(BaseModel):
    new_password: str

# パスワード更新エンドポイント
@app.put("/update-password")
def update_password(password_update: PasswordUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password_update.new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    return {"msg": "Password updated successfully!"}
c:\Users\ki6hi\AppData\Local\Packages\MicrosoftWindows.Client.Core_cw5n1h2txyewy\TempState\ScreenClip\{AC83E345-59B7-4F47-A13B-5FAA9F9C6A7B}.png