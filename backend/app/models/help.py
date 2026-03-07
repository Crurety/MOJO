"""帮助中心模型"""
from sqlalchemy import Column, Integer, BigInteger, String, Text
from app.models.base import Base, TimestampMixin


class HelpCategory(Base, TimestampMixin):
    """帮助分类表"""
    __tablename__ = "help_categories"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    slug = Column(String(100), unique=True, nullable=False, index=True, comment="分类标识")
    description = Column(Text, nullable=True, comment="分类描述")
    icon = Column(String(100), nullable=True, comment="图标")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0禁用 1启用")


class HelpArticle(Base, TimestampMixin):
    """帮助文章表"""
    __tablename__ = "help_articles"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    category_id = Column(BigInteger, nullable=False, index=True, comment="分类ID")
    title = Column(String(200), nullable=False, comment="文章标题")
    slug = Column(String(200), unique=True, nullable=False, index=True, comment="文章标识")
    content = Column(Text, nullable=False, comment="文章内容")
    summary = Column(String(500), nullable=True, comment="文章摘要")
    tags = Column(String(200), nullable=True, comment="标签，逗号分隔")
    view_count = Column(Integer, default=0, nullable=False, comment="浏览次数")
    helpful_count = Column(Integer, default=0, nullable=False, comment="有帮助次数")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0草稿 1发布")


class FAQ(Base, TimestampMixin):
    """常见问题表"""
    __tablename__ = "faqs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    category_id = Column(BigInteger, nullable=True, index=True, comment="分类ID")
    question = Column(String(500), nullable=False, comment="问题")
    answer = Column(Text, nullable=False, comment="答案")
    tags = Column(String(200), nullable=True, comment="标签，逗号分隔")
    view_count = Column(Integer, default=0, nullable=False, comment="浏览次数")
    helpful_count = Column(Integer, default=0, nullable=False, comment="有帮助次数")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    status = Column(Integer, default=1, nullable=False, comment="状态: 0禁用 1启用")
