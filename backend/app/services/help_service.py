"""帮助中心服务"""
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.help import HelpCategory, HelpArticle, FAQ


class HelpService:
    """帮助中心服务"""

    def __init__(self, db: Session):
        self.db = db

    # 分类管理
    def create_category(self, name: str, slug: str, description: str = None, icon: str = None) -> HelpCategory:
        """创建帮助分类"""
        category = HelpCategory(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            status=1
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_categories(self, status: int = 1) -> List[HelpCategory]:
        """获取分类列表"""
        query = self.db.query(HelpCategory)
        if status is not None:
            query = query.filter(HelpCategory.status == status)
        return query.order_by(HelpCategory.sort_order).all()

    def get_category_by_slug(self, slug: str) -> Optional[HelpCategory]:
        """根据标识获取分类"""
        return self.db.query(HelpCategory).filter(HelpCategory.slug == slug).first()

    # 文章管理
    def create_article(
        self,
        category_id: int,
        title: str,
        slug: str,
        content: str,
        summary: str = None,
        tags: str = None
    ) -> HelpArticle:
        """创建帮助文章"""
        article = HelpArticle(
            category_id=category_id,
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            tags=tags,
            status=1
        )
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def get_articles(
        self,
        category_id: int = None,
        status: int = 1,
        skip: int = 0,
        limit: int = 20
    ) -> List[HelpArticle]:
        """获取文章列表"""
        query = self.db.query(HelpArticle)

        if category_id:
            query = query.filter(HelpArticle.category_id == category_id)

        if status is not None:
            query = query.filter(HelpArticle.status == status)

        return query.order_by(HelpArticle.sort_order).offset(skip).limit(limit).all()

    def get_article_by_slug(self, slug: str) -> Optional[HelpArticle]:
        """根据标识获取文章"""
        return self.db.query(HelpArticle).filter(HelpArticle.slug == slug).first()

    def increment_article_view(self, article_id: int):
        """增加文章浏览次数"""
        article = self.db.query(HelpArticle).filter(HelpArticle.id == article_id).first()
        if article:
            article.view_count += 1
            self.db.commit()

    def mark_article_helpful(self, article_id: int):
        """标记文章有帮助"""
        article = self.db.query(HelpArticle).filter(HelpArticle.id == article_id).first()
        if article:
            article.helpful_count += 1
            self.db.commit()

    def search_articles(self, keyword: str, limit: int = 10) -> List[HelpArticle]:
        """搜索文章"""
        return self.db.query(HelpArticle).filter(
            HelpArticle.status == 1,
            (HelpArticle.title.contains(keyword) | HelpArticle.content.contains(keyword))
        ).limit(limit).all()

    # FAQ管理
    def create_faq(
        self,
        question: str,
        answer: str,
        category_id: int = None,
        tags: str = None
    ) -> FAQ:
        """创建FAQ"""
        faq = FAQ(
            category_id=category_id,
            question=question,
            answer=answer,
            tags=tags,
            status=1
        )
        self.db.add(faq)
        self.db.commit()
        self.db.refresh(faq)
        return faq

    def get_faqs(
        self,
        category_id: int = None,
        status: int = 1,
        skip: int = 0,
        limit: int = 50
    ) -> List[FAQ]:
        """获取FAQ列表"""
        query = self.db.query(FAQ)

        if category_id:
            query = query.filter(FAQ.category_id == category_id)

        if status is not None:
            query = query.filter(FAQ.status == status)

        return query.order_by(FAQ.sort_order).offset(skip).limit(limit).all()

    def get_faq_by_id(self, faq_id: int) -> Optional[FAQ]:
        """根据ID获取FAQ"""
        return self.db.query(FAQ).filter(FAQ.id == faq_id).first()

    def increment_faq_view(self, faq_id: int):
        """增加FAQ浏览次数"""
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        if faq:
            faq.view_count += 1
            self.db.commit()

    def mark_faq_helpful(self, faq_id: int):
        """标记FAQ有帮助"""
        faq = self.db.query(FAQ).filter(FAQ.id == faq_id).first()
        if faq:
            faq.helpful_count += 1
            self.db.commit()

    def search_faqs(self, keyword: str, limit: int = 10) -> List[FAQ]:
        """搜索FAQ"""
        return self.db.query(FAQ).filter(
            FAQ.status == 1,
            (FAQ.question.contains(keyword) | FAQ.answer.contains(keyword))
        ).limit(limit).all()

    def get_popular_articles(self, limit: int = 10) -> List[HelpArticle]:
        """获取热门文章"""
        return self.db.query(HelpArticle).filter(
            HelpArticle.status == 1
        ).order_by(HelpArticle.view_count.desc()).limit(limit).all()

    def get_popular_faqs(self, limit: int = 10) -> List[FAQ]:
        """获取热门FAQ"""
        return self.db.query(FAQ).filter(
            FAQ.status == 1
        ).order_by(FAQ.view_count.desc()).limit(limit).all()
