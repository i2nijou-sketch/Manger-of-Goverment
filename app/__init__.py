"""
Flask 应用初始化
"""
from flask import Flask
from pathlib import Path
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY, DEBUG

def create_app():
    """创建并配置 Flask 应用"""
    # 获取项目根目录
    base_dir = Path(__file__).parent.parent
    
    app = Flask(__name__, 
                template_folder=str(base_dir / 'templates'),
                static_folder=str(base_dir / 'static'))
    
    # 配置
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    # 注册蓝图
    from app.routes import bp
    app.register_blueprint(bp)
    
    # 初始化数据库
    from app.models import db
    db.init_app(app)
    
    # 创建数据库表和初始化数据
    with app.app_context():
        db.create_all()
        from app.auth import init_default_data
        init_default_data()
    
    return app

