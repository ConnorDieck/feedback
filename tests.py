from unittest import TestCase

from app import app
from models import db, User, Feedback

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

USER_DATA = {
    username = "test_user",
    password = "test_password",
    email = "test@email.com",
    first_name = "Test",
    last_name = "User"
}

FEEDBACK_DATA = {
    title = "test title",
    content = "this content is for a test",
    username = 
}

class FeedbackViewsTestCase(TestCase):
    """Tests for app.py views"""


    def setUp(self):
        """Make demo data."""

        User.query.delete()

        user = User(**USER_DATA)
        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
