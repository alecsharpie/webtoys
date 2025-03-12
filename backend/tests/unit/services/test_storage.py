"""
Unit tests for storage service
"""

import json
import os
import shutil
import tempfile
from collections.abc import Generator
from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch

from services.storage import StorageService


@pytest.mark.unit
class TestStorageService:
    """Test cases for storage service"""

    @pytest.fixture
    def storage_dir(self) -> Generator[str, None, None]:
        """Create a temporary storage directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_storage(self, storage_dir: str) -> StorageService:
        """Create a file-based storage service for testing"""
        return StorageService(storage_type="file", connection_string=storage_dir)

    @pytest.fixture
    def test_code(self) -> dict[str, str]:
        """Sample WebToy code for testing"""
        return {
            "html": "<canvas></canvas>",
            "css": "body { margin: 0; }",
            "js": "console.log('Hello');",
        }

    @pytest.fixture
    def test_metadata(self) -> dict[str, Any]:
        """Sample metadata for testing"""
        return {"description": "Test WebToy", "timestamp": 1234567890}

    @pytest.mark.asyncio
    async def test_store_preview(
        self,
        file_storage: StorageService,
        test_code: dict[str, str],
        test_metadata: dict[str, Any],
    ) -> None:
        """Test storing a preview"""
        preview_id = "test-preview-123"

        # Store preview
        await file_storage.store_preview(
            preview_id=preview_id, code=test_code, metadata=test_metadata
        )

        # Verify directory structure
        preview_dir = file_storage.previews_dir
        assert os.path.isdir(preview_dir)

        # Verify preview file exists
        preview_file = preview_dir / f"{preview_id}.json"
        assert os.path.isfile(preview_file)

        # Verify file contents
        with open(preview_file) as f:
            stored_data = json.load(f)

        assert stored_data["code"] == test_code
        assert stored_data["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_preview(
        self,
        file_storage: StorageService,
        test_code: dict[str, str],
        test_metadata: dict[str, Any],
    ) -> None:
        """Test retrieving a preview"""
        preview_id = "test-preview-456"

        # Store preview first
        await file_storage.store_preview(
            preview_id=preview_id, code=test_code, metadata=test_metadata
        )

        # Retrieve preview
        preview = await file_storage.get_preview(preview_id)

        # Verify retrieved data
        assert preview is not None
        assert preview["code"] == test_code
        assert preview["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_nonexistent_preview(self, file_storage: StorageService) -> None:
        """Test retrieving a non-existent preview"""
        preview = await file_storage.get_preview("non-existent-id")
        assert preview is None

    @pytest.mark.asyncio
    async def test_publish_webtoy(
        self,
        file_storage: StorageService,
        test_code: dict[str, str],
        test_metadata: dict[str, Any],
    ) -> None:
        """Test publishing a WebToy"""
        webtoy_id = "test-webtoy-789"

        # Publish WebToy
        await file_storage.publish_webtoy(
            webtoy_id=webtoy_id, code=test_code, metadata=test_metadata
        )

        # Verify directory structure
        webtoys_dir = file_storage.webtoys_dir
        assert os.path.isdir(webtoys_dir)

        # Verify webtoy file exists
        webtoy_file = webtoys_dir / f"{webtoy_id}.json"
        assert os.path.isfile(webtoy_file)

        # Verify file contents
        with open(webtoy_file) as f:
            stored_data = json.load(f)

        assert stored_data["code"] == test_code
        assert stored_data["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_webtoy(
        self,
        file_storage: StorageService,
        test_code: dict[str, str],
        test_metadata: dict[str, Any],
    ) -> None:
        """Test retrieving a published WebToy"""
        webtoy_id = "test-webtoy-abc"

        # Publish WebToy first
        await file_storage.publish_webtoy(
            webtoy_id=webtoy_id, code=test_code, metadata=test_metadata
        )

        # Retrieve WebToy
        webtoy = await file_storage.get_webtoy(webtoy_id)

        # Verify retrieved data
        assert webtoy is not None
        assert webtoy["code"] == test_code
        assert webtoy["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_nonexistent_webtoy(self, file_storage: StorageService) -> None:
        """Test retrieving a non-existent WebToy"""
        webtoy = await file_storage.get_webtoy("non-existent-id")
        assert webtoy is None

    @pytest.mark.asyncio
    async def test_cleanup_old_previews(
        self,
        storage_dir: str,
        test_code: dict[str, str],
        test_metadata: dict[str, Any],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test cleanup of old previews"""
        import os
        import time

        # Create a special storage service for this test
        file_storage = StorageService(
            storage_type="file", connection_string=storage_dir
        )

        # Manually set file times instead of using freeze_time since it doesn't affect os.path.getmtime
        # Create old preview files with backdated timestamps
        old_preview_1 = "old-preview-1"
        old_preview_2 = "old-preview-2"
        recent_preview_id = "recent-preview"

        # Store the previews
        await file_storage.store_preview(
            preview_id=old_preview_1,
            code=test_code,
            metadata={"timestamp": time.time()},
        )

        await file_storage.store_preview(
            preview_id=old_preview_2,
            code=test_code,
            metadata={"timestamp": time.time()},
        )

        await file_storage.store_preview(
            preview_id=recent_preview_id,
            code=test_code,
            metadata={"timestamp": time.time()},
        )

        # Manually backdate the old preview files
        old_time = time.time() - 172800  # 2 days ago (more than the 1 day threshold)
        os.utime(
            file_storage.previews_dir / f"{old_preview_1}.json", (old_time, old_time)
        )
        os.utime(
            file_storage.previews_dir / f"{old_preview_2}.json", (old_time, old_time)
        )

        # Now create and run the cleanup function
        async def run_once_cleanup() -> None:
            # Use the actual cleanup method to test
            await file_storage._cleanup_old_previews(run_once=True)

        await run_once_cleanup()

        # Old previews should be gone
        old_preview_1_result = await file_storage.get_preview(old_preview_1)
        old_preview_2_result = await file_storage.get_preview(old_preview_2)
        recent_preview = await file_storage.get_preview(recent_preview_id)

        assert old_preview_1_result is None
        assert old_preview_2_result is None
        assert recent_preview is not None
