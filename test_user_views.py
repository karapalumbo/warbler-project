"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 0000
        self.testuser.id = self.testuser_id

        self.user1 = User.signup("user1", "user1@user1.com", "password1", None)
        self.user1_id = 1111
        self.user1.id = self.user1_id

        self.user2 = User.signup("user2", "user2@user2.com", "password2", None)
        self.user2_id = 2222
        self.user2.id = self.user2_id

        db.session.commit()


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_add_user(self):
        """Can use add a user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_list_user(self):
        """Get user list."""
        with app.test_client() as client:
            resp = client.get("/users")

            self.assertEqual(resp.status_code, 200)


    def test_show_user(self):
        """Show user."""

        with app.test_client() as client:
            url = f'/users/{self.testuser.id}'
            resp = client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("@testuser", str(resp.data))


    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.user1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.user2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.user1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()



    def test_show_following(self):
        """Show user follwing.""" 

        self.setup_followers()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            url = f'/users/{self.testuser_id}/following'
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))


    def test_show_followers(self):
        """Show user follows."""

        self.setup_followers()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
    
        url = f'/users/{self.testuser_id}/followers'
        resp = client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("@user1", str(resp.data))


    def test_unauthorized_following(self):
        """Testing user must be logged in to follow."""

        self.setup_followers()

        with app.test_client() as client:
            resp = client.get(f"/users/{self.testuser_id}/following", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthorized_followers(self):
        """Testing user must be logged in to see following."""

        self.setup_followers()

        with app.test_client() as client:
            resp = client.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))