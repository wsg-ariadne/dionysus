from database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    domain = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    deceptive_design_type = db.Column(db.String(255), nullable=False)
    is_custom_type = db.Column(db.Boolean, nullable=False)
    num_reports = db.Column(db.Integer, nullable=False)
    last_report_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
