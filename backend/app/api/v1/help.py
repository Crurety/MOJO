"""Help center API routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rate_limit import RATE_LIMITS, limiter
from app.schemas import BaseResponse
from app.services.help_service import HelpService

router = APIRouter()


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    sort_order: int
    status: int
    created_at: datetime


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    title: str
    slug: str
    content: str
    summary: Optional[str]
    tags: Optional[str]
    view_count: int
    helpful_count: int
    sort_order: int
    status: int
    created_at: datetime


class FAQResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: Optional[int]
    question: str
    answer: str
    tags: Optional[str]
    view_count: int
    helpful_count: int
    sort_order: int
    status: int
    created_at: datetime


class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None


class ArticleCreate(BaseModel):
    category_id: int
    title: str
    slug: str
    content: str
    summary: Optional[str] = None
    tags: Optional[str] = None


class FAQCreate(BaseModel):
    category_id: Optional[int] = None
    question: str
    answer: str
    tags: Optional[str] = None


@limiter.limit(RATE_LIMITS["general"])
@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    help_service = HelpService(db)
    return [CategoryResponse.model_validate(c) for c in help_service.get_categories()]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/categories/{slug}", response_model=CategoryResponse)
def get_category(slug: str, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    category = help_service.get_category_by_slug(slug)
    if not category:
        raise NotFoundException(detail="Category not found")
    return CategoryResponse.model_validate(category)


@limiter.limit(RATE_LIMITS["general"])
@router.get("/articles", response_model=List[ArticleResponse])
def get_articles(
    category_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    help_service = HelpService(db)
    articles = help_service.get_articles(category_id, skip=skip, limit=limit)
    return [ArticleResponse.model_validate(a) for a in articles]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/articles/{slug}", response_model=ArticleResponse)
def get_article(slug: str, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    article = help_service.get_article_by_slug(slug)
    if not article:
        raise NotFoundException(detail="Article not found")

    help_service.increment_article_view(article.id)
    return ArticleResponse.model_validate(article)


@limiter.limit(RATE_LIMITS["general"])
@router.post("/articles/{article_id}/helpful", response_model=BaseResponse)
def mark_article_helpful(article_id: int, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    help_service.mark_article_helpful(article_id)
    return BaseResponse(message="Thanks for your feedback")


@limiter.limit(RATE_LIMITS["general"])
@router.get("/faqs", response_model=List[FAQResponse])
def get_faqs(
    category_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    help_service = HelpService(db)
    faqs = help_service.get_faqs(category_id, skip=skip, limit=limit)
    return [FAQResponse.model_validate(f) for f in faqs]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/faqs/{faq_id}", response_model=FAQResponse)
def get_faq(faq_id: int, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    faq = help_service.get_faq_by_id(faq_id)
    if not faq:
        raise NotFoundException(detail="FAQ not found")

    help_service.increment_faq_view(faq_id)
    return FAQResponse.model_validate(faq)


@limiter.limit(RATE_LIMITS["general"])
@router.post("/faqs/{faq_id}/helpful", response_model=BaseResponse)
def mark_faq_helpful(faq_id: int, db: Session = Depends(get_db)):
    help_service = HelpService(db)
    help_service.mark_faq_helpful(faq_id)
    return BaseResponse(message="Thanks for your feedback")


@limiter.limit(RATE_LIMITS["general"])
@router.get("/search")
def search_help_content(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    help_service = HelpService(db)
    articles = help_service.search_articles(keyword, limit)
    faqs = help_service.search_faqs(keyword, limit)

    return {
        "articles": [ArticleResponse.model_validate(a) for a in articles],
        "faqs": [FAQResponse.model_validate(f) for f in faqs],
        "total": len(articles) + len(faqs),
    }


@limiter.limit(RATE_LIMITS["general"])
@router.get("/popular")
def get_popular_content(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    help_service = HelpService(db)
    articles = help_service.get_popular_articles(limit)
    faqs = help_service.get_popular_faqs(limit)

    return {
        "articles": [ArticleResponse.model_validate(a) for a in articles],
        "faqs": [FAQResponse.model_validate(f) for f in faqs],
    }


@router.post("/admin/categories", response_model=BaseResponse)
def create_category(
    category_in: CategoryCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    help_service = HelpService(db)
    category = help_service.create_category(
        name=category_in.name,
        slug=category_in.slug,
        description=category_in.description,
        icon=category_in.icon,
    )
    return BaseResponse(message="Category created", data={"category_id": category.id})


@router.post("/admin/articles", response_model=BaseResponse)
def create_article(
    article_in: ArticleCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    help_service = HelpService(db)
    article = help_service.create_article(
        category_id=article_in.category_id,
        title=article_in.title,
        slug=article_in.slug,
        content=article_in.content,
        summary=article_in.summary,
        tags=article_in.tags,
    )
    return BaseResponse(message="Article created", data={"article_id": article.id})


@router.post("/admin/faqs", response_model=BaseResponse)
def create_faq(
    faq_in: FAQCreate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    help_service = HelpService(db)
    faq = help_service.create_faq(
        category_id=faq_in.category_id,
        question=faq_in.question,
        answer=faq_in.answer,
        tags=faq_in.tags,
    )
    return BaseResponse(message="FAQ created", data={"faq_id": faq.id})
