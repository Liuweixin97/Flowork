from flask import Blueprint, request, jsonify
import json
from datetime import datetime

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/api/debug/dify-test', methods=['POST', 'GET', 'PUT', 'DELETE'])
def dify_debug():
    """Dify连接调试端点"""
    
    debug_info = {
        'timestamp': datetime.utcnow().isoformat(),
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'content_type': request.content_type,
        'content_length': request.content_length,
        'headers': dict(request.headers),
        'success': True
    }
    
    # 处理请求数据
    try:
        if request.method in ['POST', 'PUT']:
            # 获取原始数据
            raw_data = request.get_data(as_text=True)
            debug_info['raw_data_length'] = len(raw_data)
            debug_info['raw_data_preview'] = raw_data[:200] + '...' if len(raw_data) > 200 else raw_data
            
            # 尝试解析JSON
            if raw_data:
                try:
                    json_data = json.loads(raw_data)
                    debug_info['json_parsed'] = True
                    debug_info['json_type'] = str(type(json_data))
                    
                    if isinstance(json_data, dict):
                        debug_info['json_keys'] = list(json_data.keys())
                        debug_info['has_resume_markdown'] = 'resume_markdown' in json_data
                        debug_info['has_title'] = 'title' in json_data
                        
                        # 检查数据内容
                        if 'resume_markdown' in json_data:
                            markdown_content = json_data['resume_markdown']
                            debug_info['markdown_length'] = len(str(markdown_content))
                            debug_info['markdown_preview'] = str(markdown_content)[:100]
                        
                        if 'title' in json_data:
                            debug_info['title_value'] = json_data['title']
                    
                    debug_info['parsed_data'] = json_data
                    
                except json.JSONDecodeError as e:
                    debug_info['json_parsed'] = False
                    debug_info['json_error'] = str(e)
                    debug_info['success'] = False
            else:
                debug_info['raw_data_empty'] = True
        
        # 处理查询参数
        if request.args:
            debug_info['query_params'] = dict(request.args)
        
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['success'] = False
    
    # 返回调试信息
    return jsonify({
        'message': 'Dify调试端点',
        'debug_info': debug_info,
        'recommendations': {
            'dify_url': 'http://host.docker.internal:8080/api/resumes/from-dify',
            'backup_url': 'http://172.18.0.1:8080/api/resumes/from-dify',
            'method': 'POST',
            'content_type': 'application/json',
            'sample_body': {
                'resume_markdown': '# 简历标题\\n\\n## 个人信息\\n- 姓名: 张三',
                'title': '张三的简历'
            }
        }
    }), 200

@debug_bp.route('/api/debug/echo', methods=['POST'])
def echo():
    """简单的回声端点，用于测试连接"""
    try:
        data = request.get_json()
        return jsonify({
            'success': True,
            'echo': data,
            'timestamp': datetime.utcnow().isoformat(),
            'message': '回声测试成功'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 400