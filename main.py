import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Post, Comment

app = FastAPI(title="Women50+ Community API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PostOut(BaseModel):
    id: str
    display_name: str
    title: str
    content: str
    topic: str
    likes: int
    created_at: Optional[str] = None

class CommentOut(BaseModel):
    id: str
    post_id: str
    display_name: str
    content: str
    created_at: Optional[str] = None


def to_post_out(doc: dict) -> PostOut:
    return PostOut(
        id=str(doc.get("_id")),
        display_name=doc.get("display_name", ""),
        title=doc.get("title", ""),
        content=doc.get("content", ""),
        topic=doc.get("topic", ""),
        likes=doc.get("likes", 0),
        created_at=str(doc.get("created_at")) if doc.get("created_at") else None,
    )


def to_comment_out(doc: dict) -> CommentOut:
    return CommentOut(
        id=str(doc.get("_id")),
        post_id=str(doc.get("post_id")),
        display_name=doc.get("display_name", ""),
        content=doc.get("content", ""),
        created_at=str(doc.get("created_at")) if doc.get("created_at") else None,
    )


@app.get("/")
def root():
    return {"message": "Women 50+ Community Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.post("/api/posts", response_model=PostOut)
def create_post(payload: Post):
    post_id = create_document("post", payload)
    doc = db["post"].find_one({"_id": ObjectId(post_id)})
    return to_post_out(doc)


@app.get("/api/posts", response_model=List[PostOut])
def list_posts(topic: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    filter_query = {}
    if topic:
        filter_query["topic"] = topic
    if q:
        filter_query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
        ]
    docs = get_documents("post", filter_query, limit)
    docs_sorted = sorted(docs, key=lambda d: d.get("created_at", 0), reverse=True)
    return [to_post_out(d) for d in docs_sorted]


class LikeIn(BaseModel):
    inc: int = 1


@app.post("/api/posts/{post_id}/like", response_model=PostOut)
def like_post(post_id: str, body: LikeIn):
    try:
        oid = ObjectId(post_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid post id")
    result = db["post"].find_one_and_update(
        {"_id": oid},
        {"$inc": {"likes": body.inc}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return to_post_out(result)


@app.post("/api/posts/{post_id}/comments", response_model=CommentOut)
def add_comment(post_id: str, payload: Comment):
    # enforce post_id from path
    payload_dict = payload.model_dump()
    payload_dict["post_id"] = post_id
    comment_id = create_document("comment", payload_dict)
    doc = db["comment"].find_one({"_id": ObjectId(comment_id)})
    return to_comment_out(doc)


@app.get("/api/posts/{post_id}/comments", response_model=List[CommentOut])
def list_comments(post_id: str, limit: int = 100):
    docs = get_documents("comment", {"post_id": post_id}, limit)
    docs_sorted = sorted(docs, key=lambda d: d.get("created_at", 0))
    return [to_comment_out(d) for d in docs_sorted]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
