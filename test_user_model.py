"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User.signup("user1", "user1@user1.com", "password1", None)
        user1_id = 111
        user1.id = user1_id

        user2 = User.signup("user2", "user2@user2.com", "password2", None)
        user2_id = 222
        user2.id = user2_id

        db.session.commit()

        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)

        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_follows(self):
        self.user1.following.append(self.user2)

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.followers), 0)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)


    def test_user_credentials(self):
        self.assertEqual(self.user1.username, "user1")
        self.assertEqual(self.user1.email, "user1@user1.com")
        self.assertNotEqual(self.user1.password, "password1")

    
    def test_invalid_username(self):
        self.assertNotEqual(self.user1.username, "user4")


    def test_user_authentication(self):
        u = User.authenticate(self.user1.username, "password1")
        self.assertEqual(u.id, self.user1.id)


    def test_invalid_username_authentication(self):
        self.assertFalse(User.authenticate("wrong", "password1"))
    
    
    def test_invalid_password_authentication(self):
        self.assertFalse(User.authenticate(self.user1.username, "wrong"))