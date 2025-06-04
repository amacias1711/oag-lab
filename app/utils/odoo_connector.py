from __future__ import annotations

"""Utility to connect to Odoo using the OdooRPC library."""

from urllib.parse import urlparse

import odoorpc
from loguru import logger

from app.core.config import settings


class OdooConnector:
    """Simple connector for Odoo using OdooRPC."""

    def __init__(self) -> None:
        self._odoo: odoorpc.ODOO | None = None

    def connect(self) -> odoorpc.ODOO:
        """Initialize the Odoo RPC client if needed and return it."""
        if self._odoo is None:
            parsed = urlparse(settings.ODOO_URL)
            host = parsed.hostname or "localhost"
            protocol = parsed.scheme or "http"
            port = parsed.port or (443 if protocol == "https" else 80)
            try:
                logger.info(
                    "Connecting to Odoo host=%s db=%s user=%s", host, settings.ODOO_DB, settings.ODOO_USER
                )
                self._odoo = odoorpc.ODOO(host, protocol=protocol, port=port)
                self._odoo.login(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD)
            except Exception:
                logger.exception("Failed to connect to Odoo")
                raise
        return self._odoo

    def search_products(
        self, domain: list | None = None, fields: list | None = None, limit: int | None = None, offset: int = 0
    ) -> list[dict]:
        """Return a list of products from Odoo given a search domain."""
        odoo = self.connect()
        product_model = odoo.env["product.product"]
        domain = domain or []
        default_fields = [
            "default_code",
            "name",
            "standard_price",
            "list_price",
            "uom_id",
            "categ_id",
            "write_date",
            "active",
        ]
        fields = fields or default_fields
        ids = product_model.search(domain, limit=limit, offset=offset)
        return product_model.read(ids, fields)

    def get_product_by_sku(self, sku: str, fields: list | None = None) -> dict | None:
        """Retrieve a single product by SKU (default_code)."""
        results = self.search_products(domain=[("default_code", "=", sku)], fields=fields, limit=1)
        return results[0] if results else None
