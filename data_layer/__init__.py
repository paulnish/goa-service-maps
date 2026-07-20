"""
GoA Service Maps — Data Layer

Backend-agnostic data access for government service map data.
The static site consumes JSON files; this layer manages the canonical
data store and exports to JSON on demand.

Usage:
    from data_layer import get_backend

    db = get_backend("sqlite", path="data/service_maps.db")
    jurisdictions = db.list_jurisdictions()
    db.export_all_json("data/")
"""

from data_layer.interface import DataBackend
from data_layer.sqlite_backend import SQLiteBackend


def get_backend(backend_type: str = "sqlite", **kwargs) -> DataBackend:
    """Factory — swap backends without touching consuming code."""
    backends = {
        "sqlite": SQLiteBackend,
    }
    if backend_type not in backends:
        raise ValueError(f"Unknown backend: {backend_type}. Available: {list(backends.keys())}")
    return backends[backend_type](**kwargs)
