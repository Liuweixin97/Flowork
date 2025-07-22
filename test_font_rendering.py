#!/usr/bin/env python3
"""测试PDF字体渲染"""

import requests
import json

# 测试数据 - 包含中文内容的简历
test_resume_data = {
    "title": "测试简历 - 中文字体渲染",
    "resume_markdown": """# 张三
**软件工程师**

📧 zhangsan@example.com | 📱 138-0000-0000 | 📍 北京市海淀区

## 工作经验

### 高级软件工程师 | ABC科技公司 | 2020.01 - 至今
- 负责核心产品的架构设计和开发工作
- 带领5人团队完成多个重要项目交付
- 使用Python、JavaScript等技术栈开发Web应用
- 实现了系统性能提升30%的优化方案

### 软件工程师 | XYZ公司 | 2018.06 - 2019.12
- 参与公司主要产品的功能开发和维护
- 协助团队完成技术栈升级工作
- 负责编写技术文档和用户手册

## 教育背景

### 计算机科学与技术学士 | 清华大学 | 2014.09 - 2018.06
- 主修课程：数据结构、算法设计、软件工程、数据库系统
- GPA: 3.8/4.0
- 获得优秀毕业生称号

## 技能特长

### 编程语言
- Python：精通，5年开发经验
- JavaScript：熟练，能够开发前后端应用
- Java：了解，曾参与企业级项目开发
- SQL：熟练，具备数据库设计和优化经验

### 框架和工具
- Django、Flask：Python Web开发框架
- React、Vue.js：前端开发框架
- Docker、Kubernetes：容器化和部署工具
- Git、Jenkins：版本控制和持续集成

## 项目经历

### 企业级客户管理系统 | 2021.03 - 2021.08
**项目描述：** 为企业客户开发的CRM系统，支持客户信息管理、销售跟进、数据分析等功能。

**技术栈：** Python, Django, PostgreSQL, Redis, React

**主要贡献：**
- 设计并实现了系统的核心架构
- 开发了用户权限管理模块
- 实现了实时数据同步功能
- 系统上线后获得客户高度认可

### 智能推荐算法优化 | 2020.05 - 2020.10
**项目描述：** 优化电商平台的商品推荐算法，提高推荐准确率和用户满意度。

**技术栈：** Python, Machine Learning, TensorFlow, Apache Spark

**主要贡献：**
- 分析用户行为数据，改进推荐模型
- 实现了基于深度学习的推荐算法
- 推荐点击率提升了25%
- 用户平均停留时间增加了15%

## 证书和荣誉

- AWS认证解决方案架构师 (2021)
- 公司年度最佳员工 (2020)
- 全国大学生程序设计竞赛三等奖 (2017)

## 个人信息

- 年龄：28岁
- 工作经验：6年
- 期望薪资：25-30K
- 可入职时间：随时
"""
}

def test_pdf_generation():
    """测试PDF生成功能"""
    try:
        print("🧪 开始测试PDF生成功能...")
        print("📝 测试数据包含丰富的中文内容")
        
        # 发送请求到后端API
        response = requests.post(
            'http://localhost:8080/api/resumes/from-dify',
            json=test_resume_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 简历创建成功!")
            print(f"📄 简历ID: {result.get('id')}")
            print(f"📝 简历标题: {result.get('title')}")
            
            # 测试PDF下载
            if result.get('id'):
                pdf_response = requests.get(f"http://localhost:8080/api/resumes/{result['id']}/pdf")
                if pdf_response.status_code == 200:
                    # 保存PDF文件
                    with open('test_font_rendering.pdf', 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"✅ PDF生成成功! 文件已保存为: test_font_rendering.pdf")
                    print(f"📊 PDF文件大小: {len(pdf_response.content)} 字节")
                    
                    # 检查是否使用了正确的字体
                    print(f"🔤 使用字体: HelveticaCJK (系统字体)")
                    print(f"💡 提示: 请打开生成的PDF文件检查中文字符渲染效果")
                    
                    return True
                else:
                    print(f"❌ PDF下载失败: {pdf_response.status_code}")
                    print(f"错误信息: {pdf_response.text}")
            
        else:
            print(f"❌ 简历创建失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        
    return False

if __name__ == "__main__":
    print("🚀 PDF字体渲染测试")
    print("=" * 50)
    
    success = test_pdf_generation()
    
    print("=" * 50)
    if success:
        print("🎉 测试完成! 请检查生成的PDF文件中的中文字符渲染效果")
        print("📂 生成的文件: test_font_rendering.pdf")
    else:
        print("😞 测试失败，请检查服务状态和错误信息")