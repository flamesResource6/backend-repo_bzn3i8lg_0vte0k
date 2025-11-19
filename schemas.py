"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Community app schemas

TopicType = Literal[
    "Perimenopause",
    "Menopause",
    "Post-menopause",
    "Mental Health",
    "Nutrition",
    "Sleep",
    "Fitness",
    "Relationships",
    "Caregiving",
]

class Post(BaseModel):
    """
    Community posts created by members
    Collection: "post"
    """
    display_name: str = Field(..., min_length=2, max_length=60, description="Name to show with the post")
    title: str = Field(..., min_length=3, max_length=120)
    content: str = Field(..., min_length=8, max_length=5000)
    topic: TopicType
    likes: int = Field(0, ge=0)

class Comment(BaseModel):
    """
    Comments on posts
    Collection: "comment"
    """
    post_id: str = Field(..., description="Associated post id")
    display_name: str = Field(..., min_length=2, max_length=60)
    content: str = Field(..., min_length=2, max_length=2000)
