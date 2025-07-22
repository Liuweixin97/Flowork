from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db
from routes.resume_routes import resume_bp
from routes.debug_routes import debug_bp
from routes.chatflow_routes import chatflow_bp
from routes.notification_routes import notification_bp
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///resume_editor.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # 启用CORS，允许前端和Docker容器访问
    CORS(app, origins=[
        'http://localhost:3000', 
        'http://localhost:3001',
        'http://localhost:3002',
        'http://localhost:5173',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:3001', 
        'http://127.0.0.1:3002',
        'http://127.0.0.1:5173'
    ], 
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization', 'X-Client-ID'],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
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
            'message': '简历编辑器API服务',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'receive_from_dify': '/api/resumes/from-dify',
                'resumes': '/api/resumes',
                'resume_detail': '/api/resumes/<id>',
                'export_pdf': '/api/resumes/<id>/pdf',
                'preview': '/api/resumes/<id>/preview',
                'chatflow_start': '/api/chatflow/start',
                'chatflow_message': '/api/chatflow/message',
                'chatflow_stream': '/api/chatflow/stream',
                'chatflow_history': '/api/chatflow/history/<conversation_id>',
                'chatflow_end': '/api/chatflow/end',
                'chatflow_status': '/api/chatflow/status',
                'notification_events': '/api/notifications/events',
                'notification_test': '/api/notifications/test'
            }
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