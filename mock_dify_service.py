#!/usr/bin/env python3
"""
模拟Dify服务用于测试Chatflow集成
"""
from flask import Flask, request, jsonify
import json
import uuid
import time

app = Flask(__name__)

# 模拟会话数据存储
sessions = {}

# 模拟对话流程步骤
CONVERSATION_STEPS = [
    {
        "step": 1,
        "question": "您好！我是AI简历助手。首先，请告诉我您的姓名？",
        "required_info": "name"
    },
    {
        "step": 2,
        "question": "很好！现在请告诉我您的联系方式，包括邮箱和电话？",
        "required_info": "contact"
    },
    {
        "step": 3,
        "question": "请描述您的工作经历，包括公司名称、职位和主要职责？",
        "required_info": "experience"
    },
    {
        "step": 4,
        "question": "请介绍您的教育背景，包括学校、专业和毕业时间？",
        "required_info": "education"
    },
    {
        "step": 5,
        "question": "最后，请列出您的主要技能和专长？",
        "required_info": "skills"
    }
]

@app.route('/v1/workflows/run', methods=['POST'])
def run_workflow():
    """模拟Dify工作流执行"""
    try:
        data = request.get_json()
        inputs = data.get('inputs', {})
        user_message = inputs.get('user_message', '')
        conversation_id = inputs.get('conversation_id', '')
        
        print(f"[MOCK DIFY] 收到消息: {user_message}")
        print(f"[MOCK DIFY] 会话ID: {conversation_id}")
        
        # 获取或创建会话
        if conversation_id not in sessions:
            sessions[conversation_id] = {
                'step': 0,
                'collected_info': {},
                'created_at': time.time()
            }
        
        session = sessions[conversation_id]
        current_step = session['step']
        
        # 处理用户输入
        if current_step > 0 and current_step <= len(CONVERSATION_STEPS):
            step_info = CONVERSATION_STEPS[current_step - 1]
            required_info = step_info['required_info']
            session['collected_info'][required_info] = user_message
        
        # 移动到下一步
        session['step'] = current_step + 1
        next_step = session['step']
        
        # 生成响应
        if next_step <= len(CONVERSATION_STEPS):
            # 还有更多问题要问
            next_question = CONVERSATION_STEPS[next_step - 1]['question']
            response = {
                "code": 200,
                "data": {
                    "outputs": {
                        "answer": next_question
                    },
                    "metadata": {
                        "status": "active",
                        "step": next_step,
                        "total_steps": len(CONVERSATION_STEPS)
                    }
                }
            }
        else:
            # 所有信息收集完毕，生成简历
            resume_markdown = generate_resume_markdown(session['collected_info'])
            response = {
                "code": 200,
                "data": {
                    "outputs": {
                        "answer": "太棒了！我已经为您生成了一份专业的简历。简历创建完成！",
                        "resume_markdown": resume_markdown
                    },
                    "metadata": {
                        "status": "completed",
                        "resume_ready": True,
                        "resume_content": resume_markdown
                    }
                }
            }
            
            # 清理会话
            del sessions[conversation_id]
        
        print(f"[MOCK DIFY] 返回响应: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"[MOCK DIFY] 错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"处理请求时出错: {str(e)}"
        }), 500

def generate_resume_markdown(collected_info):
    """根据收集的信息生成简历Markdown"""
    name = collected_info.get('name', '姓名')
    contact = collected_info.get('contact', '联系方式')
    experience = collected_info.get('experience', '工作经历')
    education = collected_info.get('education', '教育背景')
    skills = collected_info.get('skills', '技能专长')
    
    resume_template = f"""# {name}

## 个人信息
{contact}

## 工作经历
{experience}

## 教育背景
{education}

## 技能专长
{skills}

## 自我评价
我是一位积极进取的专业人士，具备扎实的专业技能和丰富的工作经验。善于学习新技术，具有良好的团队协作能力和沟通技巧。致力于在工作中创造价值，追求卓越的工作成果。
"""
    
    return resume_template

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "mock-dify",
        "active_sessions": len(sessions)
    })

if __name__ == '__main__':
    print("🎭 启动模拟Dify服务...")
    print("监听端口: 8001")
    print("工作流端点: http://localhost:8001/v1/workflows/run")
    app.run(host='localhost', port=8001, debug=True)