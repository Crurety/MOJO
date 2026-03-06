"""数据库恢复脚本"""
import os
import shutil
import subprocess
from app.core.config import settings
from app.core.logging import logger

# 备份目录
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backups")


def list_backups():
    """列出所有备份"""
    logger.info("列出所有备份...")
    
    try:
        backups = []
        for item in os.listdir(BACKUP_DIR):
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isfile(item_path) or os.path.isdir(item_path):
                backups.append({
                    "name": item,
                    "path": item_path,
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else sum(
                        os.path.getsize(os.path.join(item_path, f)) 
                        for f in os.listdir(item_path) 
                        if os.path.isfile(os.path.join(item_path, f))
                    ),
                    "mtime": os.path.getmtime(item_path)
                })
        
        # 按修改时间排序
        backups.sort(key=lambda x: x["mtime"], reverse=True)
        
        for backup in backups:
            logger.info(f"备份: {backup['name']} - 大小: {backup['size']} bytes")
        
        return backups
    except Exception as e:
        logger.error(f"列出备份失败: {e}")
        return []


def restore_database(backup_file: str):
    """恢复数据库
    
    Args:
        backup_file: 备份文件路径
    """
    logger.info(f"开始恢复数据库: {backup_file}")
    
    try:
        # 从DATABASE_URL中提取数据库信息
        db_url = settings.DATABASE_URL
        if db_url.startswith("mysql+pymysql://"):
            # MySQL恢复
            db_url = db_url.replace("mysql+pymysql://", "")
            user, rest = db_url.split(":", 1)
            password, rest = rest.split("@", 1)
            host, rest = rest.split("/", 1)
            db_name = rest.split("?")[0]
            
            # 使用mysql命令恢复
            cmd = f"mysql -u {user} -p{password} -h {host} {db_name} < {backup_file}"
            subprocess.run(cmd, shell=True, check=True)
            logger.info(f"MySQL数据库恢复成功: {backup_file}")
        elif db_url.startswith("sqlite:///"):
            # SQLite恢复
            db_path = db_url.replace("sqlite:///", "")
            shutil.copy2(backup_file, db_path)
            logger.info(f"SQLite数据库恢复成功: {backup_file}")
        else:
            logger.warning(f"不支持的数据库类型: {db_url}")
    except Exception as e:
        logger.error(f"数据库恢复失败: {e}")


def restore_files(backup_dir: str):
    """恢复重要文件
    
    Args:
        backup_dir: 备份目录路径
    """
    logger.info(f"开始恢复文件: {backup_dir}")
    
    try:
        # 恢复配置文件
        for file_name in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, file_name)
            if os.path.isfile(file_path):
                # 确定目标路径
                if file_name == ".env":
                    target_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), file_name)
                else:
                    target_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", file_name)
                
                shutil.copy2(file_path, target_path)
                logger.info(f"恢复文件: {file_path} -> {target_path}")
    except Exception as e:
        logger.error(f"文件恢复失败: {e}")


def main():
    """主函数"""
    # 列出所有备份
    backups = list_backups()
    
    if not backups:
        logger.error("没有找到备份文件")
        return
    
    # 选择最新的备份
    latest_backup = backups[0]
    logger.info(f"选择最新备份: {latest_backup['name']}")
    
    # 恢复数据库
    if latest_backup['name'].endswith('.sql'):
        restore_database(latest_backup['path'])
    elif latest_backup['name'].endswith('.db'):
        restore_database(latest_backup['path'])
    # 恢复文件
    elif latest_backup['name'].endswith('_files'):
        restore_files(latest_backup['path'])


if __name__ == "__main__":
    main()
