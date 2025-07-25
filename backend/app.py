from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from models import db, bcrypt
from routes.resume_routes import resume_bp
from routes.debug_routes import debug_bp
from routes.chatflow_routes import chatflow_bp
from routes.notification_routes import notification_bp
from routes.auth_routes import auth_bp
from services.auth_service import is_token_blacklisted
import os
from dotenv import load_dotenv
from datetime import timedelta

# 加载环境变量
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 基础配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # 数据库配置
    database_url = os.getenv('DATABASE_URL', 'sqlite:///resume_editor.db')
    # 处理Heroku PostgreSQL URL格式
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    # 生产环境安全配置
    if os.getenv('FLASK_ENV') == 'production':
        app.config['JWT_COOKIE_SECURE'] = True  # HTTPS only
        app.config['JWT_COOKIE_CSRF_PROTECT'] = True
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True

    # ==================== CORS 调试修改 ====================
    # 为了解决花生壳等隧道工具的跨域问题，我们暂时允许所有来源的请求。
    # 原始的复杂判断逻辑已被暂时替换为下面这一行简单的配置。
    CORS(app, supports_credentials=True, origins="*")
    # ========================================================
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 初始化数据库迁移
    migrate = Migrate(app, db)
    
    # JWT黑名单检查
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return is_token_blacklisted(jti)
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'errors': ['令牌已过期，请重新登录']
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'errors': ['无效的令牌']
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'errors': ['需要登录才能访问']
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'errors': ['令牌已被撤销，请重新登录']
        }), 401
    
    # 注册蓝图
    app.register_blueprint(auth_bp)  # 认证路由放在最前面
    app.register_blueprint(resume_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(chatflow_bp)
    app.register_blueprint(notification_bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '资源未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': '服务器内部错误'}), 500
    
    @app.before_request
    def before_request():
        # 记录请求日志
        if request.endpoint:
            print(f"[{request.method}] {request.url}")
    
    # 根路径
    @app.route('/')
    def home():
        return jsonify({
            'message': '简历编辑器API服务 - 多用户生产版',
            'version': '1.3.0',
            'features': ['用户认证', 'JWT会话', '多用户隔离', 'HTML转PDF', '智能一页'],
            'endpoints': {
                'auth_register': '/api/auth/register',
                'auth_login': '/api/auth/login',
                'auth_refresh': '/api/auth/refresh',
                'auth_logout': '/api/auth/logout',
                'auth_me': '/api/auth/me',
                'auth_profile': '/api/auth/profile',
                'auth_change_password': '/api/auth/change-password',
                'health': '/api/health',
                'receive_from_dify': '/api/resumes/from-dify',
                'resumes': '/api/resumes',
                'resume_detail': '/api/resumes/<id>',
                'export_pdf': '/api/resumes/<id>/pdf',
                'export_pdf_html': '/api/resumes/<id>/pdf-html',
                'resume_html': '/api/resumes/<id>/html',
                'preview': '/api/resumes/<id>/preview',
                'chatflow_start': '/api/chatflow/start',
                'chatflow_message': '/api/chatflow/message',
                'chatflow_stream': '/api/chatflow/stream',
                'chatflow_history': '/api/chatflow/history/<conversation_id>',
                'chatflow_end': '/api/chatflow/end',
                'chatflow_status': '/api/chatflow/status',
                'notification_events': '/api/notifications/events',
                'notification_test': '/api/notifications/test'
            },
            'database': 'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite',
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # 开发模式配置
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"简历编辑器后端服务启动中...")
    print(f"访问地址: http://{host}:{port}")
    print(f"Dify接收端点: http://{host}:{port}/api/resumes/from-dify")
    
    app.run(host=host, port=port, debug=debug)