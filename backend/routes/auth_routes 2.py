"""
用户认证相关路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from services.auth_service import AuthService, logout_user, is_token_blacklisted
from models import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'errors': ['请提供注册信息']
            }), 400
        
        result = AuthService.register_user(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['注册失败，请稍后重试']
        }), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'errors': ['请提供登录信息']
            }), 400
        
        result = AuthService.login_user(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['登录失败，请稍后重试']
        }), 500

@auth_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        # 检查refresh token是否在黑名单中
        jti = get_jwt()['jti']
        if is_token_blacklisted(jti):
            return jsonify({
                'success': False,
                'errors': ['令牌已失效，请重新登录']
            }), 401
        
        result = AuthService.refresh_token()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['令牌刷新失败']
        }), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        # 检查access token是否在黑名单中
        jti = get_jwt()['jti']
        if is_token_blacklisted(jti):
            return jsonify({
                'success': False,
                'errors': ['令牌已失效']
            }), 401
        
        result = logout_user()
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['登出失败']
        }), 500

@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    try:
        # 检查token是否在黑名单中
        jti = get_jwt()['jti']
        if is_token_blacklisted(jti):
            return jsonify({
                'success': False,
                'errors': ['令牌已失效，请重新登录']
            }), 401
        
        user = AuthService.get_current_user()
        
        if user:
            return jsonify({
                'success': True,
                'user': user.to_dict(include_private=True)
            }), 200
        else:
            return jsonify({
                'success': False,
                'errors': ['用户不存在或已被禁用']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['获取用户信息失败']
        }), 500

@auth_bp.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户资料"""
    try:
        # 检查token是否在黑名单中
        jti = get_jwt()['jti']
        if is_token_blacklisted(jti):
            return jsonify({
                'success': False,
                'errors': ['令牌已失效，请重新登录']
            }), 401
        
        user = AuthService.get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'errors': ['用户不存在']
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'errors': ['请提供更新信息']
            }), 400
        
        result = AuthService.update_user_profile(user, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['更新失败，请稍后重试']
        }), 500

@auth_bp.route('/api/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        # 检查token是否在黑名单中
        jti = get_jwt()['jti']
        if is_token_blacklisted(jti):
            return jsonify({
                'success': False,
                'errors': ['令牌已失效，请重新登录']
            }), 401
        
        user = AuthService.get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'errors': ['用户不存在']
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'errors': ['请提供密码信息']
            }), 400
        
        result = AuthService.change_password(user, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['修改密码失败，请稍后重试']
        }), 500

@auth_bp.route('/api/auth/check-username', methods=['POST'])
def check_username():
    """检查用户名是否可用"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'available': False,
                'message': '用户名不能为空'
            }), 400
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'success': False,
                'available': False,
                'message': '用户名长度必须在3-20个字符之间'
            }), 400
        
        # 检查是否已存在
        existing_user = User.find_by_username(username)
        available = existing_user is None
        
        return jsonify({
            'success': True,
            'available': available,
            'message': '用户名可用' if available else '用户名已存在'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'available': False,
            'message': '检查失败'
        }), 500

@auth_bp.route('/api/auth/check-email', methods=['POST'])
def check_email():
    """检查邮箱是否可用"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'available': False,
                'message': '邮箱不能为空'
            }), 400
        
        try:
            # 验证邮箱格式
            User.validate_email(email)
        except ValueError as e:
            return jsonify({
                'success': False,
                'available': False,
                'message': str(e)
            }), 400
        
        # 检查是否已存在
        existing_user = User.find_by_email(email)
        available = existing_user is None
        
        return jsonify({
            'success': True,
            'available': available,
            'message': '邮箱可用' if available else '邮箱已被使用'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'available': False,
            'message': '检查失败'
        }), 500

# 用户统计信息（管理员可用）
@auth_bp.route('/api/auth/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """获取用户统计信息（管理员）"""
    try:
        # 检查token是否在黑名单中
        jti = get_jwt()['jti']
        if is_token_blacklisted(jti):
            return jsonify({
                'success': False,
                'errors': ['令牌已失效，请重新登录']
            }), 401
        
        user = AuthService.get_current_user()
        if not user or not user.is_admin:
            return jsonify({
                'success': False,
                'errors': ['权限不足']
            }), 403
        
        # 统计用户数量
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        
        # 最近注册用户
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'admin_users': admin_users,
                'recent_users': [user.to_dict() for user in recent_users]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'errors': ['获取统计信息失败']
        }), 500