from database import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    deceptive_design_type = db.Column(db.String(255), nullable=False)
    is_custom_type = db.Column(db.Boolean, nullable=False)
    num_reports = db.Column(db.Integer, nullable=False)
    last_report_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
