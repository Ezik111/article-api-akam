from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List
from fastapi.openapi.docs import get_redoc_html

from app import models, schemas, security, database
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Article Management API",
    description="Secure API for managing articles and users with a notification system",
    version="1.0.0",
    redoc_url=None
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# -----Middleware-----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

# -----Helper functions-----
def notify_subscribers(db: Session, message: str):
    subscribers = db.query(models.User).filter(models.User.is_subscribed == True).all()
    for sub in subscribers:
        print(f"--- NOTIFICATION TO {sub.email}: {message} ---")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise credentials_exception
    return user

# -----Auth-----
@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# -----Users------
@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(email=user.email, hashed_password=security.get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.put("/users/subscribe", response_model=schemas.UserResponse, tags=["Users"])
def update_subscription(
    subscription: schemas.UserSubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    current_user.is_subscribed = subscription.is_subscribed
    db.commit()
    db.refresh(current_user)
    return current_user

# -----Articles-----
@app.get("/articles/", response_model=List[schemas.ArticleResponse], tags=["Articles"])
def read_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Article).offset(skip).limit(limit).all()

@app.post("/articles/", response_model=schemas.ArticleResponse, status_code=status.HTTP_201_CREATED, tags=["Articles"])
def create_article(
    article: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_article = models.Article(**article.model_dump(), author_id=current_user.id)
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    notify_subscribers(db, f"New article: {new_article.title}")
    return new_article

@app.put("/articles/{article_id}", response_model=schemas.ArticleResponse, tags=["Articles"])
def update_article(
    article_id: int,
    article_update: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for key, value in article_update.model_dump().items():
        setattr(db_article, key, value)
    db.commit()
    db.refresh(db_article)
    return db_article

@app.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Articles"])
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_article)
    db.commit()

@app.post("/articles/import", status_code=status.HTTP_201_CREATED, tags=["Articles"])
def bulk_import_articles(
    data: schemas.ArticleImport,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    for art_data in data.articles:
        db.add(models.Article(**art_data.model_dump(), author_id=current_user.id))
    
    db.commit()
    notify_subscribers(db, f"Imported {len(data.articles)} new articles")
    return {"message": f"Successfully imported {len(data.articles)} articles"}

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js",
    )