import os
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def test():
    # Run unit tests
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def recreate_db():
    # Recreates local db. Do not use in production
    db.drop_all()
    db.create_all()
    db.session.commit()

# @manager.command
# def setup_dev():
#     # Runs the set-up needed for local development
#     setup_general()
#
#
# @manager.command
# def setup_prod():
#     # Runs the set-up needed for production
#     setup_general()
#
# @manager.command
# def setup_general():
#     # Runs initial set up for local dev and production
#

#
# Launch point
#
if __name__=='__main__':
    # Initialize DB
    manager.run()
