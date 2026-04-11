from extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    records = db.relationship('StockRecord', backref='user', lazy=True,
                              foreign_keys='StockRecord.user_id')


class Cabinet(db.Model):
    __tablename__ = 'cabinets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), default='')
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.now)

    reagents = db.relationship('Reagent', backref='cabinet', lazy=True,
                               cascade='all, delete-orphan')
    alerts = db.relationship('DepletionAlert', backref='cabinet', lazy=True,
                             cascade='all, delete-orphan')


class Reagent(db.Model):
    __tablename__ = 'reagents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    cas_number = db.Column(db.String(50), nullable=True)
    product_number = db.Column(db.String(100), nullable=True)   # 新增
    specification = db.Column(db.String(100), nullable=False)
    note = db.Column(db.Text, default='')   # 新增
    quantity = db.Column(db.Float, default=0.0)
    cabinet_id = db.Column(db.Integer, db.ForeignKey('cabinets.id'), nullable=False)
    last_stock_in = db.Column(db.DateTime, nullable=True)
    last_withdrawal = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class StockRecord(db.Model):
    __tablename__ = 'stock_records'

    id = db.Column(db.Integer, primary_key=True)
    reagent_id = db.Column(db.Integer, db.ForeignKey('reagents.id', ondelete='SET NULL'),
                           nullable=True)
    reagent_name = db.Column(db.String(200), nullable=False)
    cas_number = db.Column(db.String(50), nullable=True)
    product_number = db.Column(db.String(100), nullable=True)   # 新增
    specification = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, default='')   # 新增
    cabinet_name = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                        nullable=True)
    user_name = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    operation_type = db.Column(db.String(10), nullable=False)  # 'in' or 'out'
    timestamp = db.Column(db.DateTime, default=datetime.now)


class DepletionAlert(db.Model):
    __tablename__ = 'depletion_alerts'

    id = db.Column(db.Integer, primary_key=True)
    reagent_name = db.Column(db.String(200), nullable=False)
    cas_number = db.Column(db.String(50), nullable=True)
    product_number = db.Column(db.String(100), nullable=True)   # 新增
    specification = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, default='')   # 新增
    cabinet_id = db.Column(db.Integer, db.ForeignKey('cabinets.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
