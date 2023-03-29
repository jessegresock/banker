from sqlalchemy.sql import func
from .extensions import db


class CitiTransactionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    date = db.Column(db.DateTime)
    description = db.Column(db.String(100))
    debit = db.Column(db.Float)
    credit = db.Column(db.Float)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    category = db.Column(db.String(50))
