from database import db


class Site(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Site {self.name} ({self.hostname})>'
