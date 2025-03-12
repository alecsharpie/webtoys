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
        self, file_storage: StorageService, test_code: dict[str, str], test_metadata: dict[str, Any]
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
        self, file_storage: StorageService, test_code: dict[str, str], test_metadata: dict[str, Any]
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
        self, file_storage: StorageService, test_code: dict[str, str], test_metadata: dict[str, Any]
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
        self, file_storage: StorageService, test_code: dict[str, str], test_metadata: dict[str, Any]
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
        file_storage: StorageService, 
        test_code: dict[str, str], 
        test_metadata: dict[str, Any], 
        monkeypatch: MonkeyPatch
    ) -> None:
        """Test cleanup of old previews"""
        import time

        from freezegun import freeze_time

        # Create some previews with different timestamps
        with freeze_time("2023-01-01"):
            await file_storage.store_preview(
                preview_id="old-preview-1",
                code=test_code,
                metadata={"timestamp": time.time()},
            )

        with freeze_time("2023-01-02"):
            await file_storage.store_preview(
                preview_id="old-preview-2",
                code=test_code,
                metadata={"timestamp": time.time()},
            )

        # Create a recent preview
        recent_preview_id = "recent-preview"
        await file_storage.store_preview(
            preview_id=recent_preview_id,
            code=test_code,
            metadata={"timestamp": time.time()},
        )

        # Manually run cleanup
        with freeze_time("2023-01-04"):
            # Create a method to run a one-time cleanup
            async def run_once_cleanup() -> None:
                # Get all preview files
                preview_files = list(file_storage.previews_dir.glob("*.json"))

                # Current time
                current_time = time.time()

                # Use 1 day (86400 seconds) as max age
                max_age = 86400

                # Delete files older than max_age
                for file_path in preview_files:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age:
                        file_path.unlink()
            
            await run_once_cleanup()

        # Old previews should be gone
        old_preview_1 = await file_storage.get_preview("old-preview-1")
        old_preview_2 = await file_storage.get_preview("old-preview-2")
        recent_preview = await file_storage.get_preview(recent_preview_id)

        assert old_preview_1 is None
        assert old_preview_2 is None
        assert recent_preview is not None
