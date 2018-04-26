import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import app, db
from pim.models import Product
from pim import views 
import datetime

migrate = Migrate(app, db)
manager = Manager(app)
app.register_blueprint(views.pim_app)
manager.add_command('db', MigrateCommand)


@manager.command
def resetdb():
    """Destroys and creates the database + tables."""

    from sqlalchemy_utils import database_exists, create_database, drop_database
    from sqlalchemy import text

    DB_URL = app.config['SQLALCHEMY_DATABASE_URI']
    if database_exists(DB_URL):
        print('Deleting database..')
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)

    print('Creating tables.')
    from pim.models import Product
    db.create_all()
    db.session.commit()
    print ("done!")

@manager.command
def seed():
    "Add seed data to the database."
    product = Product(
        name="Mac book Pro",
        sku="mac-b-p-0123",
        description="this is test product",
        is_active=True
    )
    db.session.add(product)
    db.session.commit()

if __name__ == '__main__':
    manager.run()