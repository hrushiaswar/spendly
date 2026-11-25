import pytest

from database import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))

    import app as app_module

    app_module.app.config.update(TESTING=True)
    db.init_db()
    db.seed_db()

    with app_module.app.test_client() as test_client:
        yield test_client
