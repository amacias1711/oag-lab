# app/core/odoo_connector.py

from urllib.parse import urlparse
import odoorpc
from .config import settings

class OdooConnector:
    def __init__(self):
        # No conectamos aún, sólo guardamos datos
        parsed = urlparse(settings.ODOO_URL)
        self.host = parsed.hostname or settings.ODOO_URL
        self.port = parsed.port or 8069
        self.db   = settings.ODOO_DB
        self.user = settings.ODOO_USER
        self.pwd  = settings.ODOO_PASSWORD

        self.odoo = None  # se inicializará al llamar a _connect()

    def _connect(self):
        """Conecta a Odoo si aún no lo hemos hecho."""
        if self.odoo is None:
            self.odoo = odoorpc.ODOO(host=self.host, port=self.port)
            self.odoo.login(self.db, self.user, self.pwd)

    def create(self, model: str, vals: dict) -> int:
        self._connect()
        return self.odoo.env[model].create(vals)

    def search(self, model: str, domain: list, **kw):
        self._connect()
        return self.odoo.env[model].search(domain, **kw)

    def search_read(self, model: str, domain: list, fields: list, **kw):
        self._connect()
        return self.odoo.env[model].search_read(domain, fields=fields, **kw)

    def write(self, model: str, ids: list, vals: dict) -> bool:
        self._connect()
        return self.odoo.env[model].write(ids, vals)

    def unlink(self, model: str, ids: list) -> bool:
        self._connect()
        return self.odoo.env[model].unlink(ids)

    def execute(self, model: str, method: str, *args, **kwargs):
        self._connect()
        fn = getattr(self.odoo.env[model], method)
        return fn(*args, **(kwargs or {}))
    
# exportamos la instancia para usar en los routers
odoo = OdooConnector()
