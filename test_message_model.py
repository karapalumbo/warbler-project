
import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app

db.create_all()


class MessageModelTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User.signup("user1", "user1@user1.com", "password1", None)
        user1_id = 111
        user1.id = user1_id

        db.session.commit()

        user1 = User.query.get(user1_id)

        self.user1 = user1
        self.user1_id = user1_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="Testing",
            user_id=self.user1_id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.user1.messages), 1)


    def test_delete_message(self):
        """Test to delete message."""

        m = Message(
            text="Testing",
            user_id=self.user1_id
        )

        db.session.add(m)
        db.session.commit()

        msg = Message.query.get(m.id)
        db.session.delete(msg)
        
        self.assertEqual(len(self.user1.messages), 0)


    def test_message_likes(self):
        """Test message likes."""

        m = Message(
            text="Testing",
            user_id=self.user1_id
        )

        db.session.add(m)
        db.session.commit()

        self.user1.likes.append(m)
        db.session.commit()

        self.assertEqual(len(self.user1.likes), 1)

    
    