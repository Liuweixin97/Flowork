#!/usr/bin/env python3
"""
测试HTML转PDF功能
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8080"

def test_html_pdf_functionality():
    """测试HTML转PDF功能"""
    
    # 1. 首先获取现有的简历列表
    print("1. 获取简历列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/resumes")
        if response.status_code != 200:
            print(f"获取简历列表失败: {response.status_code}")
            return False
        
        resumes = response.json().get('resumes', [])
        if not resumes:
            print("没有找到简历，创建一个测试简历...")
            # 创建测试简历
            test_resume = {
                "resume_markdown": """# 张三

📧 zhangsan@email.com | 📱 138-0000-0000 | 📍 北京市

---

## 工作经历

### **软件工程师** | ABC科技公司 | 2022-至今

- 负责开发和维护公司核心产品
- 参与技术架构设计和优化
- 协调团队完成项目交付

### **前端开发实习生** | XYZ公司 | 2021-2022

- 使用React开发用户界面
- 优化页面性能和用户体验

## 教育背景

### **计算机科学与技术学士** | 清华大学 | 2018-2022

- GPA: 3.8/4.0
- 相关课程：数据结构、算法设计、软件工程

## 技能

- **编程语言**: Python, JavaScript, Java
- **前端技术**: React, Vue.js, HTML/CSS
- **后端技术**: Flask, Django, Spring Boot
- **数据库**: MySQL, PostgreSQL, MongoDB
- **工具**: Git, Docker, Kubernetes

## 项目经验

### **个人博客系统**

- 使用Django和PostgreSQL开发的博客平台
- 支持Markdown编辑和语法高亮
- 实现了用户认证和评论系统
""",
                "title": "HTML转PDF测试简历"
            }
            
            response = requests.post(f"{BASE_URL}/api/resumes/from-dify", json=test_resume)
            if response.status_code not in [200, 201]:
                print(f"创建测试简历失败: {response.status_code}")
                return False
            
            resume_data = response.json()
            resume_id = resume_data.get('resume_id')
            print(f"✓ 创建测试简历成功，ID: {resume_id}")
        else:
            resume_id = resumes[0]['id']
            print(f"✓ 使用现有简历，ID: {resume_id}")
        
        # 2. 测试HTML内容生成
        print("\n2. 测试HTML内容生成...")
        response = requests.get(f"{BASE_URL}/api/resumes/{resume_id}/html")
        if response.status_code == 200:
            html_data = response.json()
            html_content = html_data.get('html_content', '')
            print(f"✓ HTML内容生成成功，长度: {len(html_content)} 字符")
            
            # 检查HTML内容是否包含关键元素
            if '<html>' in html_content and '<body>' in html_content:
                print("✓ HTML结构正确")
            else:
                print("⚠ HTML结构可能有问题")
        else:
            print(f"✗ HTML内容生成失败: {response.status_code}")
            print(response.text)
            return False
        
        # 3. 测试HTML转PDF（这可能会失败，因为wkhtmltopdf未安装）
        print("\n3. 测试HTML转PDF...")
        response = requests.get(f"{BASE_URL}/api/resumes/{resume_id}/pdf-html")
        if response.status_code == 200:
            pdf_data = response.content
            print(f"✓ HTML转PDF成功，PDF大小: {len(pdf_data)} 字节")
            
            # 保存PDF文件用于验证
            with open("test_html_output.pdf", "wb") as f:
                f.write(pdf_data)
            print("✓ PDF已保存为 test_html_output.pdf")
            
        else:
            print(f"⚠ HTML转PDF失败: {response.status_code}")
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"错误信息: {error_data}")
            print("这通常是因为wkhtmltopdf或Playwright未安装")
        
        # 4. 测试智能一页HTML转PDF
        print("\n4. 测试智能一页HTML转PDF...")
        response = requests.get(f"{BASE_URL}/api/resumes/{resume_id}/pdf-html?smart_onepage=true")
        if response.status_code == 200:
            pdf_data = response.content
            print(f"✓ 智能一页HTML转PDF成功，PDF大小: {len(pdf_data)} 字节")
            
            # 保存PDF文件用于验证
            with open("test_html_onepage_output.pdf", "wb") as f:
                f.write(pdf_data)
            print("✓ PDF已保存为 test_html_onepage_output.pdf")
            
        else:
            print(f"⚠ 智能一页HTML转PDF失败: {response.status_code}")
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"错误信息: {error_data}")
        
        # 5. 比较传统PDF导出
        print("\n5. 比较传统PDF导出...")
        response = requests.get(f"{BASE_URL}/api/resumes/{resume_id}/pdf")
        if response.status_code == 200:
            pdf_data = response.content
            print(f"✓ 传统PDF导出成功，PDF大小: {len(pdf_data)} 字节")
            
            # 保存PDF文件用于比较
            with open("test_traditional_output.pdf", "wb") as f:
                f.write(pdf_data)
            print("✓ PDF已保存为 test_traditional_output.pdf")
        else:
            print(f"✗ 传统PDF导出失败: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务，请确保后端服务已启动")
        return False
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {e}")
        return False

def install_dependencies_guide():
    """显示依赖安装指南"""
    print("\n=== HTML转PDF依赖安装指南 ===")
    print("\n选项1: 安装wkhtmltopdf (推荐)")
    print("macOS: brew install wkhtmltopdf")
    print("Ubuntu: sudo apt-get install wkhtmltopdf")
    print("Windows: 从 https://wkhtmltopdf.org/downloads.html 下载")
    
    print("\n选项2: 安装Playwright (备用)")
    print("pip install playwright")
    print("playwright install chromium")
    
    print("\n选项3: 使用Docker")
    print("在docker-compose.yml中已经包含了wkhtmltopdf")

if __name__ == "__main__":
    print("开始测试HTML转PDF功能...\n")
    
    success = test_html_pdf_functionality()
    
    if success:
        print("\n=== 测试完成 ===")
        print("✓ HTML内容生成功能正常")
        print("? HTML转PDF功能需要安装额外依赖")
        install_dependencies_guide()
    else:
        print("\n=== 测试失败 ===")
        print("请检查后端服务是否正常启动")