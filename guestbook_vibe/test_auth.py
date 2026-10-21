from contextlib import closing
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('vibe', Path(__file__).with_name('app.py'))
vibe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vibe)


class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = vibe.DB_FILE, vibe.JSON_FILE
        vibe.DB_FILE = Path(self.tmp.name) / 'test.db'
        vibe.JSON_FILE = Path(self.tmp.name) / 'data.json'
        with closing(sqlite3.connect(vibe.DB_FILE)) as db:
            db.execute('CREATE TABLE entries (id INTEGER PRIMARY KEY, name TEXT, message TEXT, page INTEGER, x REAL, y REAL, rot REAL, color INTEGER)')
            db.execute("INSERT INTO entries VALUES (1,'old','legacy',1,0,0,0,0)")
            db.commit()
        vibe.app.config.update(TESTING=True, SECRET_KEY='test-secret')
        vibe.init_db()
        vibe.init_db()
        self.a = vibe.app.test_client()
        self.b = vibe.app.test_client()

    def tearDown(self):
        vibe.DB_FILE, vibe.JSON_FILE = self.old
        self.tmp.cleanup()

    def post(self, client, path, **data):
        client.get('/')
        with client.session_transaction() as session:
            data['csrf_token'] = session['csrf_token']
        return client.post(path, data=data)

    def note(self, client):
        response = self.post(client, '/add', name='same name', message='hello', page=1, x=10, y=10)
        self.assertEqual(response.status_code, 302)
        with closing(sqlite3.connect(vibe.DB_FILE)) as db:
            return db.execute('SELECT max(id) FROM entries').fetchone()[0]

    def register(self, client, username):
        self.assertEqual(self.post(client, '/register', username=username, password='password123').status_code, 302)

    def test_guest_ownership_and_csrf(self):
        note = self.note(self.a)
        self.assertIn(f'/delete/{note}?'.encode(), self.a.get('/').data)
        self.assertNotIn(f'/delete/{note}?'.encode(), self.b.get('/').data)
        self.assertEqual(self.post(self.b, f'/delete/{note}').status_code, 403)
        self.assertEqual(self.a.post(f'/delete/{note}').status_code, 400)
        self.assertEqual(self.post(self.a, '/delete/1').status_code, 403)
        self.register(self.a, 'alice')
        self.assertEqual(self.post(self.a, f'/delete/{note}').status_code, 302)

    def test_account_ownership_survives_login(self):
        self.register(self.a, 'alice')
        note = self.note(self.a)
        self.register(self.b, 'bob')
        self.assertEqual(self.post(self.b, f'/delete/{note}').status_code, 403)
        self.post(self.a, '/logout')
        self.assertEqual(self.post(self.a, f'/delete/{note}').status_code, 403)
        self.assertEqual(self.post(self.a, '/login', username='alice', password='wrong').status_code, 400)
        self.assertEqual(self.post(self.a, '/login', username='ALICE', password='password123').status_code, 302)
        self.assertEqual(self.post(self.a, f'/delete/{note}').status_code, 302)

    def test_admin_and_registration(self):
        note = self.note(self.b)
        runner = vibe.app.test_cli_runner()
        result = runner.invoke(args=['create-admin', 'admin'], input='password123\npassword123\n')
        self.assertEqual(result.exit_code, 0, result.output)
        self.post(self.a, '/login', username='admin', password='password123')
        for id in (1, note):
            self.assertEqual(self.post(self.a, f'/delete/{id}').status_code, 302)
        self.assertEqual(self.post(self.a, '/delete/999').status_code, 404)
        self.assertEqual(self.post(self.b, '/register', username='ADMIN', password='password123').status_code, 400)
        for path in ('/login', '/register', '/add'):
            self.assertEqual(self.a.get(path).status_code, 200)


if __name__ == '__main__':
    unittest.main()
