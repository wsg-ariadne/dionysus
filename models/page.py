from database import db


class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    site_id = db.Column(db.BigInteger, db.ForeignKey('sites.id'), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    deceptive_design_types = db.Column(db.String(255), nullable=False)
    custom_deceptive_design_types = db.Column(db.String(255), nullable=True)
    num_reports = db.Column(db.Integer, nullable=False)
    last_report_timestamp = db.Column(db.DateTime, nullable=False)
