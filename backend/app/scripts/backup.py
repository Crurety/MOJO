"""数据库备份脚本"""
import os
import time
import shutil
from datetime import datetime
import subprocess
from app.core.config import settings
from app.core.logging import logger

# 备份目录
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backups")
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# 备份文件名格式
BACKUP_FILENAME = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def backup_database():
    """备份数据库"""
    logger.info("开始备份数据库...")
    
    try:
        # 从DATABASE_URL中提取数据库信息
        db_url = settings.DATABASE_URL
        if db_url.startswith("mysql+pymysql://"):
            # MySQL备份
            db_url = db_url.replace("mysql+pymysql://", "")
            user, rest = db_url.split(":", 1)
            password, rest = rest.split("@", 1)
            host, rest = rest.split("/", 1)
            db_name = rest.split("?")[0]
            
            # 使用mysqldump命令备份
            backup_file = os.path.join(BACKUP_DIR, f"{BACKUP_FILENAME}_mysql.sql")
            cmd = f"mysqldump -u {user} -p{password} -h {host} {db_name} > {backup_file}"
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"MySQL数据库备份成功: {backup_file}")
        elif db_url.startswith("sqlite:///"):
            # SQLite备份
            db_path = db_url.replace("sqlite:///", "")
            backup_file = os.path.join(BACKUP_DIR, f"{BACKUP_FILENAME}_sqlite.db")
            shutil.copy2(db_path, backup_file)
            logger.info(f"SQLite数据库备份成功: {backup_file}")
        else:
            logger.warning(f"不支持的数据库类型: {db_url}")
    except Exception as e:
        logger.error(f"数据库备份失败: {e}")


def backup_files():
    """备份重要文件"""
    logger.info("开始备份重要文件...")
    
    try:
        # 备份配置文件
        config_files = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", ".env")
        ]
        
        # 备份目录
        backup_files_dir = os.path.join(BACKUP_DIR, f"{BACKUP_FILENAME}_files")
        if not os.path.exists(backup_files_dir):
            os.makedirs(backup_files_dir)
        
        for file_path in config_files:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_files_dir)
                logger.info(f"备份文件: {file_path}")
    except Exception as e:
        logger.error(f"文件备份失败: {e}")


def cleanup_old_backups(days: int = 7):
    """清理旧备份
    
    Args:
        days: 保留天数
    """
    logger.info(f"清理{days}天前的旧备份...")
    
    try:
        current_time = time.time()
        for item in os.listdir(BACKUP_DIR):
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                if current_time - os.path.getmtime(item_path) > days * 24 * 60 * 60:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    else:
                        shutil.rmtree(item_path)
                    logger.info(f"清理旧备份: {item}")
    except Exception as e:
        logger.error(f"清理旧备份失败: {e}")


def main():
    """主函数"""
    backup_database()
    backup_files()
    cleanup_old_backups()
    logger.info("备份任务完成")


if __name__ == "__main__":
    main()
