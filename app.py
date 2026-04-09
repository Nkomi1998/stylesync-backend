from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import select
from db import ScrapedSite, DesignToken
from fastapi.middleware.cors import CORSMiddleware
from db import get_db, init_db
from sqlalchemy.ext.asyncio import AsyncSession
from scraper import scrape_site

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

class ScrapedSiteCreate(BaseModel):
    url: str

class DesignTokenCreate(BaseModel):
    colors: List[str] = []
    typography: dict = {}
    spacing: List[str] = []
    image_palette: List[str] = []

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

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/sites/", response_model=dict)
async def create_site(site: ScrapedSiteCreate, db: AsyncSession = Depends(get_db)):
    # Create site
    new_site = ScrapedSite(url=site.url, extraction_status="scraped")
    db.add(new_site)
    await db.commit()
    await db.refresh(new_site)
    return {"id": new_site.id, "url": new_site.url}

@app.get("/sites/")
async def get_sites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScrapedSite))
    sites = result.scalars().all()
    return sites

@app.post("/scrape/")
async def scrape_and_save(scrape_data: ScrapedSiteCreate, db: AsyncSession = Depends(get_db)):
    url = scrape_data.url
    data = await scrape_site(url)
    # Create site
    new_site = ScrapedSite(url=url, extraction_status=data['status'])
    db.add(new_site)
    await db.commit()
    await db.refresh(new_site)
    
    # Create token
    new_token = DesignToken(
        site_id=new_site.id,
        colors=data.get('colors', []),
        typography=data.get('typography', {}),
        spacing=data.get('spacing', [])
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return {"site_id": new_site.id, "token_id": new_token.id, "tokens_saved": True, "data": data}
