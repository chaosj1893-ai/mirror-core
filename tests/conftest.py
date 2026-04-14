import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_data_dir():
    """Create a temporary data directory for tests."""
    d = tempfile.mkdtemp(prefix="mirrorcore_test_")
    for sub in ["soul/versions", "faculty", "body/chroma_db", "timeline", "feedback"]:
        os.makedirs(os.path.join(d, sub))
    yield Path(d)
    shutil.rmtree(d)
