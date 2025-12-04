"""
配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "data.db"}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 密钥配置
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# 调试模式
DEBUG = True

