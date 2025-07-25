from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import json
import uuid
from email_validator import validate_email, EmailNotValidError

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(200), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # 关联简历
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, full_name=None):
        """初始化用户"""
        self.username = username
        self.email = self.validate_email(email)
        self.set_password(password)
        self.full_name = full_name or username
        
    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError:
            raise ValueError("无效的邮箱格式")
    
    def set_password(self, password):
        """设置密码哈希"""
        if len(password) < 6:
            raise ValueError("密码长度不能少于6位")
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_private=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'public_id': self.public_id,
            'username': self.username,
            'email': self.email if include_private else None,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'resume_count': len(self.resumes)
        }
        
        if include_private:
            data.update({
                'is_admin': self.is_admin,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
        
        return data
    
    @staticmethod
    def find_by_username(username):
        """根据用户名查找用户"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        """根据邮箱查找用户"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_public_id(public_id):
        """根据公开ID查找用户"""
        return User.query.filter_by(public_id=public_id).first()

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='我的简历')
    raw_markdown = db.Column(db.Text, nullable=False)
    structured_data = db.Column(db.Text, nullable=True)  # JSON格式的结构化数据
    is_public = db.Column(db.Boolean, default=False)  # 是否公开
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 关联用户
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_content=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'is_public': self.is_public,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_content:
            data.update({
                'raw_markdown': self.raw_markdown,
                'structured_data': json.loads(self.structured_data) if self.structured_data else None
            })
        
        # 包含用户信息（如果有）
        if hasattr(self, 'user') and self.user:
            data['author'] = {
                'username': self.user.username,
                'full_name': self.user.full_name,
                'avatar_url': self.user.avatar_url
            }
        
        return data
    
    def set_structured_data(self, data):
        """设置结构化数据"""
        self.structured_data = json.dumps(data, ensure_ascii=False)
    
    def get_structured_data(self):
        """获取结构化数据"""
        return json.loads(self.structured_data) if self.structured_data else None
    
    def can_access(self, user):
        """检查用户是否可以访问此简历"""
        if not user:
            return self.is_public
        return self.user_id == user.id or self.is_public or user.is_admin
    
    def can_edit(self, user):
        """检查用户是否可以编辑此简历"""
        if not user:
            return False
        return self.user_id == user.id or user.is_admin