# tests/test_odoo_connector.py
import pytest
from app.core.odoo_connector import OdooConnector

class DummyModel:
    def __init__(self):
        self.store = {}
        self.next_id = 1

    def create(self, vals):
        new_id = self.next_id
        self.store[new_id] = vals
        self.next_id += 1
        return new_id

    def search(self, domain, **_):
        # domain = [["id","=",new_id]]
        _, _, val = domain[0]
        return [i for i in self.store if i == val]

    def unlink(self, ids):
        for i in ids:
            self.store.pop(i, None)
        return True

class DummyEnv:
    def __init__(self):
        self._models = {"res.partner": DummyModel()}

    def __getitem__(self, model):
        return self._models[model]

@pytest.fixture()
def connector(monkeypatch):
    # Instancia sin conectar
    conn = OdooConnector()
    # Reemplazamos su atributo .odoo por nuestro stub
    dummy = DummyEnv()
    # El env de odoorpc es accesible como conn.odoo.env
    conn.odoo = type("X", (), {"env": dummy})
    return conn

def test_create_and_unlink_partner(connector):
    new_id = connector.create("res.partner", {"name": "Prueba"})
    assert isinstance(new_id, int) and new_id > 0

    found = connector.search("res.partner", [["id", "=", new_id]])
    assert new_id in found

    assert connector.unlink("res.partner", [new_id]) is True
    assert connector.search("res.partner", [["id", "=", new_id]]) == []
