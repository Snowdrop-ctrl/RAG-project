import tempfile

import pytest

from app.config import settings

# Keep tests off the real index: point Chroma at a throwaway directory before
# anything imports/creates the collection.
_tmp_dir = tempfile.mkdtemp(prefix="rag-test-chroma-")
settings.chroma_dir = _tmp_dir


@pytest.fixture
def clean_index():
    from app.services import vector_store

    vector_store.reset()
    yield
    vector_store.reset()
