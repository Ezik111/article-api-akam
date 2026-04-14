from pydantic import BaseModel, EmailStr
from typing import List

class ArticleBase(BaseModel):
    title: str
    content: str

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int
    author_id: int
   
    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_subscribed: bool  
    
    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str

class UserSubscriptionUpdate(BaseModel):
    is_subscribed: bool

class ArticleImport(BaseModel):
    articles: List[ArticleCreate]