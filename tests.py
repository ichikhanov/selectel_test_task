import json
from unittest import TestCase
from utils import get_db_cursor
from main import app


class AppTestCase(TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.ticket = self.create_test_ticket()
        self.comment = self.create_test_comment()

    def tearDown(self):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("TRUNCATE tickets CASCADE;")
            cursor.execute("TRUNCATE comments;")

    def create_test_ticket(self):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO tickets (theme, text, email, status)
                        VALUES('test_theme', 'test_text', 'test@email.com',
                        'open') RETURNING id;"""
            )
            ticket = cursor.fetchone()
            return ticket["id"]

    def create_test_comment(self):
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO comments (text, email, ticket_id)
                        VALUES('test_text', 'comments@email.com',
                         %s) RETURNING id;""",
                (self.ticket,),
            )
            comment = cursor.fetchone()
            return comment["id"]

    def test_get_ticket_by_id_200(self):
        ticket = self.client.get("/tickets/{0}".format(self.ticket))
        self.assertEqual(200, ticket.status_code)
        ticket_body = json.loads(ticket.data.decode("utf-8"))
        self.assertEqual(1, len(ticket_body.get("comments")))

    def test_get_ticket_404(self):
        ticket = self.client.get("/tickets/{0}".format((self.ticket + 1)))
        self.assertEqual(404, ticket.status_code)

    def test_post_ticket_201(self):
        ticket_post_data = {
            "theme": "this is a theme",
            "text": "this is the ticket task",
            "email": "this@test.email",
            "status": "open",
        }
        ticket = self.client.post("/tickets", data=ticket_post_data)
        self.assertEqual(201, ticket.status_code)
        ticket_body = json.loads(ticket.data.decode("utf-8"))
        self.assertEqual("this is a theme", ticket_body["theme"])

    def test_post_ticket_400(self):
        ticket_post_data = {
            "theme": "this is a theme",
            "text": "this is the ticket task",
            "email": "this@test.email",
            "status": "closed",
        }
        ticket = self.client.post("/tickets", data=ticket_post_data)
        self.assertEqual(400, ticket.status_code)

    def test_patch_ticket_200(self):
        ticket_patch_data = {"status": "responded"}
        ticket = self.client.patch(
            "/tickets/{0}".format(self.ticket), data=ticket_patch_data
        )
        self.assertEqual(200, ticket.status_code)
        ticket_body = json.loads(ticket.data.decode("utf-8"))
        self.assertEqual("responded", ticket_body["status"])

    def test_patch_ticket_400(self):
        ticket_patch_data = {"status": "open"}
        ticket = self.client.patch(
            "/tickets/{0}".format(self.ticket), data=ticket_patch_data
        )
        self.assertEqual(400, ticket.status_code)

    def test_patch_404(self):
        ticket_patch_data = {"status": "open"}
        ticket = self.client.patch(
            "/tickets/{0}".format((self.ticket + 1)), data=ticket_patch_data
        )
        self.assertEqual(404, ticket.status_code)

    def test_post_comment_201(self):
        comment_post_data = {
            "ticket_id": self.ticket,
            "email": "test@test.com",
            "text": "comment for the ticket",
        }
        comment = self.client.post("/comments", data=comment_post_data)
        self.assertEqual(201, comment.status_code)
        comment_body = json.loads(comment.data.decode("utf-8"))
        self.assertEqual(self.ticket, comment_body["ticket_id"])
        ticket = self.client.get("/tickets/{0}".format(self.ticket))
        self.assertEqual(200, ticket.status_code)
        ticket_body = json.loads(ticket.data.decode("utf-8"))
        self.assertEqual(2, len(ticket_body.get("comments")))

    def test_post_comment_ticket_closed(self):
        ticket_patch_data = {"status": "closed"}
        ticket = self.client.patch(
            "/tickets/{0}".format(self.ticket), data=ticket_patch_data
        )
        self.assertEqual(200, ticket.status_code)
        ticket_body = json.loads(ticket.data.decode("utf-8"))
        self.assertEqual("closed", ticket_body["status"])
        comment_post_data = {
            "ticket_id": self.ticket,
            "email": "test@test.com",
            "text": "comment for the ticket",
        }
        comment = self.client.post("/comments", data=comment_post_data)
        self.assertEqual(400, comment.status_code)
