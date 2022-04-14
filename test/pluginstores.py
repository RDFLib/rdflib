# -*- coding=utf8 -*-
import shutil
import tempfile
import os

import pytest

from rdflib import Graph, Dataset, Namespace, URIRef, plugin
from rdflib.store import VALID_STORE

HOST = "http://localhost:3030"
DB = "/db/"
root = HOST + DB

#
# SQLAlchemy RDBS back-ends require a more extensive connection string which,
# for security reasons, should be specified via shell variables when running
# the test, e.g.
#
# $ PGDB=1 PGDBURI="postgresql+pg8000://vagrant:vagrant@localhost/testdb" \
# MYSQLDB=1 MYDBURI="mysql+pymysql://vagrant:vagrant@localhost/testdb" \
# ./run_tests.py test/test_store/test_store_auditable.py
#

dburis = {}

def get_plugin_stores():
    pluginstores = []

    for s in plugin.plugins(None, plugin.Store):
        if s.name in (
            "default",
            "Auditable",
            "Concurrent",
            "SimpleMemory",
            "SPARQLStore",
            "ZODB",
            "Shelving",
            "OxMemory",
            "OxSled",
        ):
            continue  # excluded from these tests

        try:
            graph = Graph(store=s.name)

            if s.name == "SQLAlchemy":
                if os.environ.get("PGDB"):
                    dburis["PGSQL"] = os.environ.get(
                        "PGDBURI",
                        "postgresql+pg8000://postgres@localhost/test")
                    pluginstores.append(s.name + ":PGSQL")
                if os.environ.get("MYSQLDB"):
                    dburis["MYSQL"] = os.environ.get(
                        "MYDBURI",
                        "mysql+pymysql://root@127.0.0.1:3306/test?charset=utf8")
                    pluginstores.append(s.name + ":MYSQL")
                if os.environ.get("SQLDB"):
                    dburis["SQLITE"] = os.environ.get(
                        "SQLDBURI",
                        "sqlite://")
                    pluginstores.append(s.name + ":SQLITE")
            elif s.name == "SPARQLUpdateStore":
                try:
                    assert len(urlopen(HOST).read()) > 0
                    pluginstores.append(s.name)
                except Exception:
                    pass
            else:
                pluginstores.append(s.name)

        except ImportError:
            pass

    return pluginstores

def set_store_and_path(storename):

    store = storename

    if storename == "SPARQLUpdateStore":
        path = (root + "sparql", root + "update")

    elif storename in ["SQLiteLSM", "LevelDB", "KyotoCabinet"]:
        path = os.path.join(tempfile.gettempdir(), f"test_{storename.lower()}")

    elif ":" in storename:
        store, backend = storename.split(":")
        path = dburis[backend]

    else:
        path = tempfile.mkdtemp()
        try:
            shutil.rmtree(path)
        except Exception:
            pass

    return store, path


def open_store(g, storename, path):
    if storename == "SPARQLUpdateStore":
        g.store.open(configuration=path, create=False)
    elif storename == "FileStorageZODB":
        g.store.open(configuration=path, create=True)
    elif storename != "Memory":
        # rt = g.store.open(configuration=path, create=True)
        rt = g.store.open(path, create=True)
        assert rt == VALID_STORE, "The underlying store is corrupt"
    return g


def cleanup(g, storename, path):
    try:
        g.store.commit()
    except Exception:
        pass

    if storename != "Memory":
        if storename == "SPARQLUpdateStore":
            g.remove((None, None, None))
            g.close()
        else:
            try:
                g.close()
                g.destroy(configuration=path)
            except Exception:
                pass
        try:
            shutil.rmtree(path)
        except Exception:
            pass

# @pytest.fixture(
#     scope="function",
#     params=get_plugin_stores(),
# )
# def get_graph(request):
#     storename = request.param

#     store, path = set_store_and_path(storename)

#     g = Graph(store=store, identifier=URIRef("urn:example:testgraph"))

#     g = open_store(g, storename, path)

#     yield g

#     cleanup(g, storename, path)

# @pytest.fixture(
#     scope="function",
#     params=get_plugin_stores(),
# )
# def get_dataset(request):
#     storename = request.param

#     store, path = set_store_and_path(storename)

#     g = Dataset(store=store, identifier=URIRef("urn:example:testgraph"))

#     g = open_store(g, storename, path)

#     yield g

#     cleanup(g, storename, path)
