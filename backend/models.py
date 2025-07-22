from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='我的简历')
    raw_markdown = db.Column(db.Text, nullable=False)
    structured_data = db.Column(db.Text, nullable=True)  # JSON格式的结构化数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'raw_markdown': self.raw_markdown,
            'structured_data': json.loads(self.structured_data) if self.structured_data else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def set_structured_data(self, data):
        self.structured_data = json.dumps(data, ensure_ascii=False)
    
    def get_structured_data(self):
        return json.loads(self.structured_data) if self.structured_data else None