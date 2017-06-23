from occrp.database import db
from occrp import models
from occrp import create_app

if __name__ == "__main__":
    fake_app = create_app()

    with fake_app.test_request_context():

        db.create_all()
