# -*- encoding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from main import db
import sys

sys.path.append("..")

# db = app.db
# db = SQLAlchemy(app)

Base = declarative_base()


class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    sku = db.Column(db.String(120), nullable=False)
    # sku = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500))
    is_active = db.Column(db.Boolean)

    def __init__(self, name, sku, description, is_active):
        self.name = name
        self.sku = sku
        self.is_active = is_active
        self.description = description

    def __repr__(self):
        return '<Product %r>' % self.name
