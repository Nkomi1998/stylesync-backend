from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]  # Allow all for dev (frontend file://, etc.)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app = FastAPI(title="Stylesync Backend", version="1.0")  # Removed duplicate; middleware-applied app used

# ----------------------
# Data models
# ----------------------
class User(BaseModel):
    id: int
    name: str
    email: str

class Style(BaseModel):
    id: int
    name: str
    description: str

# ----------------------
# Fake in-memory data
# ----------------------
users_db: List[User] = [
    User(id=1, name="Alice", email="alice@example.com"),
    User(id=2, name="Bob", email="bob@example.com"),
]

styles_db: List[Style] = [
    Style(id=1, name="Casual", description="Everyday casual style"),
    Style(id=2, name="Formal", description="Professional/formal style"),
]

# ----------------------
# Routes
# ----------------------
@app.get("/")
def read_root():
    return {"message": "Stylesync backend is running!"}

@app.get("/users", response_model=List[User])
def get_users():
    return users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/styles", response_model=List[Style])
def get_styles():
    return styles_db

@app.get("/styles/{style_id}", response_model=Style)
def get_style(style_id: int):
    for style in styles_db:
        if style.id == style_id:
            return style
    raise HTTPException(status_code=404, detail="Style not found")

@app.post("/users", response_model=User)
def create_user(user: User):
    users_db.append(user)
    return user

@app.post("/styles", response_model=Style)
def create_style(style: Style):
    styles_db.append(style)
    return style

@app.get("/test")
def test():
    return {"message": "Backend is working!"}
