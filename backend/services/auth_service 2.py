"""
用户认证服务
"""

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from datetime import timedelta
from models import User, db
import re

class AuthService:
    """用户认证服务类"""
    
    @staticmethod
    def validate_registration_data(data):
        """验证注册数据"""
        errors = []
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field) or not data.get(field).strip():
                errors.append(f'{field}不能为空')
        
        if errors:
            return errors
            
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        
        # 验证用户名
        if len(username) < 3 or len(username) > 20:
            errors.append('用户名长度必须在3-20个字符之间')
        
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            errors.append('用户名只能包含字母、数字、下划线和中文')
        
        # 验证密码强度
        if len(password) < 6:
            errors.append('密码长度不能少于6位')
        
        if len(password) > 128:
            errors.append('密码长度不能超过128位')
        
        # 检查用户名是否已存在
        if User.find_by_username(username):
            errors.append('用户名已存在')
        
        # 检查邮箱是否已存在
        if User.find_by_email(email):
            errors.append('邮箱已被使用')
        
        return errors
    
    @staticmethod
    def register_user(data):
        """注册新用户"""
        # 验证数据
        errors = AuthService.validate_registration_data(data)
        if errors:
            return {'success': False, 'errors': errors}
        
        try:
            # 创建用户
            user = User(
                username=data['username'].strip(),
                email=data['email'].strip(),
                password=data['password'],
                full_name=data.get('full_name', '').strip() or data['username'].strip()
            )
            
            db.session.add(user)
            db.session.commit()
            
            # 生成token
            access_token = create_access_token(
                identity=user.public_id,
                expires_delta=timedelta(days=1)
            )
            refresh_token = create_refresh_token(
                identity=user.public_id,
                expires_delta=timedelta(days=30)
            )
            
            return {
                'success': True,
                'user': user.to_dict(include_private=True),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except ValueError as e:
            db.session.rollback()
            return {'success': False, 'errors': [str(e)]}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'errors': ['注册失败，请稍后重试']}
    
    @staticmethod
    def login_user(data):
        """用户登录"""
        # 验证必填字段
        if not data.get('login') or not data.get('password'):
            return {'success': False, 'errors': ['用户名/邮箱和密码不能为空']}
        
        login = data['login'].strip()
        password = data['password']
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.find_by_username(login) or User.find_by_email(login)
        
        if not user:
            return {'success': False, 'errors': ['用户不存在']}
        
        if not user.is_active:
            return {'success': False, 'errors': ['账户已被禁用']}
        
        if not user.check_password(password):
            return {'success': False, 'errors': ['密码错误']}
        
        try:
            # 更新最后登录时间
            user.update_last_login()
            
            # 生成token
            access_token = create_access_token(
                identity=user.public_id,
                expires_delta=timedelta(days=1)
            )
            refresh_token = create_refresh_token(
                identity=user.public_id,
                expires_delta=timedelta(days=30)
            )
            
            return {
                'success': True,
                'user': user.to_dict(include_private=True),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            return {'success': False, 'errors': ['登录失败，请稍后重试']}
    
    @staticmethod
    def refresh_token():
        """刷新访问令牌"""
        try:
            current_user_id = get_jwt_identity()
            user = User.find_by_public_id(current_user_id)
            
            if not user or not user.is_active:
                return {'success': False, 'errors': ['用户不存在或已被禁用']}
            
            # 生成新的访问令牌
            new_access_token = create_access_token(
                identity=user.public_id,
                expires_delta=timedelta(days=1)
            )
            
            return {
                'success': True,
                'access_token': new_access_token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'errors': ['令牌刷新失败']}
    
    @staticmethod
    def get_current_user():
        """获取当前用户"""
        try:
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return None
            
            user = User.find_by_public_id(current_user_id)
            return user if user and user.is_active else None
            
        except:
            return None
    
    @staticmethod
    def update_user_profile(user, data):
        """更新用户资料"""
        try:
            # 验证邮箱格式（如果要更新）
            if 'email' in data and data['email'] != user.email:
                new_email = data['email'].strip()
                if User.find_by_email(new_email):
                    return {'success': False, 'errors': ['邮箱已被使用']}
                user.email = User.validate_email(new_email)
            
            # 更新其他字段
            if 'full_name' in data:
                user.full_name = data['full_name'].strip()
            
            if 'avatar_url' in data:
                user.avatar_url = data['avatar_url'].strip() if data['avatar_url'] else None
            
            db.session.commit()
            
            return {
                'success': True,
                'user': user.to_dict(include_private=True)
            }
            
        except ValueError as e:
            db.session.rollback()
            return {'success': False, 'errors': [str(e)]}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'errors': ['更新失败，请稍后重试']}
    
    @staticmethod
    def change_password(user, data):
        """修改密码"""
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return {'success': False, 'errors': ['当前密码和新密码不能为空']}
        
        if not user.check_password(current_password):
            return {'success': False, 'errors': ['当前密码错误']}
        
        try:
            user.set_password(new_password)
            db.session.commit()
            
            return {'success': True, 'message': '密码修改成功'}
            
        except ValueError as e:
            db.session.rollback()
            return {'success': False, 'errors': [str(e)]}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'errors': ['密码修改失败，请稍后重试']}

# JWT黑名单存储（生产环境建议使用Redis）
blacklisted_tokens = set()

def is_token_blacklisted(jti):
    """检查token是否在黑名单中"""
    return jti in blacklisted_tokens

def blacklist_token(jti):
    """将token加入黑名单"""
    blacklisted_tokens.add(jti)

def logout_user():
    """用户登出"""
    try:
        jti = get_jwt()['jti']
        blacklist_token(jti)
        return {'success': True, 'message': '登出成功'}
    except:
        return {'success': False, 'errors': ['登出失败']}