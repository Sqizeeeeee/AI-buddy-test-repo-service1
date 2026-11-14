import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import create_app


class NotesAppTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(TemporaryDirectory())
        self.database = Path(directory) / "notes.sqlite3"
        self.client = create_app(self.database).test_client()

    def test_create_and_read_note_after_restart(self):
        response = self.client.post("/notes", data={"title": "Демо", "body": "<b>текст</b>"})
        self.assertEqual(response.status_code, 303)

        client = create_app(self.database).test_client()
        detail = client.get(response.location)
        self.assertEqual(detail.status_code, 200)
        self.assertIn("&lt;b&gt;текст&lt;/b&gt;", detail.get_data(as_text=True))
        self.assertIn("Демо", client.get("/").get_data(as_text=True))

    def test_reject_empty_title(self):
        response = self.client.post("/notes", data={"title": " ", "body": "Демо"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/notes/1").status_code, 404)
