from database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Detection(db.Model):
    __tablename__ = 'detections'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    domain = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    calliope_tripped = db.Column(db.Boolean, default=False)
    janus_result = db.Column(db.Integer, default=False)
    calliope_text = db.Column(db.String(255), nullable=True)
    janus_screenshot = db.Column(db.Text, nullable=True)
    vote = db.Column(db.Boolean, nullable=False)
