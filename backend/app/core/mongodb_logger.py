"""MongoDB日志处理器"""
import logging
from pymongo import MongoClient
from datetime import datetime, timezone
from app.core.config import settings

class MongoDBHandler(logging.Handler):
    """MongoDB日志处理器"""
    
    def __init__(self, collection_name: str = "logs"):
        """初始化MongoDB日志处理器
        
        Args:
            collection_name: 集合名称
        """
        super().__init__()
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        self.collection = self.db[collection_name]
    
    def emit(self, record):
        """发送日志到MongoDB
        
        Args:
            record: 日志记录
        """
        try:
            # 格式化日志记录
            log_entry = {
                "timestamp": datetime.now(timezone.utc),
                "level": record.levelname,
                "message": record.getMessage(),
                "name": record.name,
                "filename": record.filename,
                "lineno": record.lineno,
                "funcName": record.funcName,
                "process": record.process,
                "thread": record.thread,
                "module": record.module,
                "pathname": record.pathname
            }
            
            # 添加异常信息
            if record.exc_info:
                import traceback
                log_entry["exc_info"] = traceback.format_exc()
            
            # 插入到MongoDB
            self.collection.insert_one(log_entry)
        except Exception as e:
            # 避免日志处理器本身出错导致程序崩溃
            print(f"MongoDB日志写入失败: {e}")
    
    def close(self):
        """关闭MongoDB连接"""
        if hasattr(self, "client"):
            self.client.close()
        super().close()
