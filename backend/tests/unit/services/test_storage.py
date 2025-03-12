"""
Unit tests for storage service
"""

import os
import json
import pytest
import tempfile
import shutil
from typing import Dict, Any

from services.storage import StorageService


@pytest.mark.unit
class TestStorageService:
    """Test cases for storage service"""

    @pytest.fixture
    def storage_dir(self):
        """Create a temporary storage directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_storage(self, storage_dir):
        """Create a file-based storage service for testing"""
        return StorageService(
            storage_type="file",
            connection_string=storage_dir
        )

    @pytest.fixture
    def test_code(self):
        """Sample WebToy code for testing"""
        return {
            "html": "<canvas></canvas>",
            "css": "body { margin: 0; }",
            "js": "console.log('Hello');"
        }

    @pytest.fixture
    def test_metadata(self):
        """Sample metadata for testing"""
        return {
            "description": "Test WebToy",
            "timestamp": 1234567890
        }

    @pytest.mark.asyncio
    async def test_store_preview(self, file_storage, test_code, test_metadata):
        """Test storing a preview"""
        preview_id = "test-preview-123"
        
        # Store preview
        await file_storage.store_preview(
            preview_id=preview_id,
            code=test_code,
            metadata=test_metadata
        )
        
        # Verify directory structure
        preview_dir = os.path.join(file_storage.base_path, "previews")
        assert os.path.isdir(preview_dir)
        
        # Verify preview file exists
        preview_file = os.path.join(preview_dir, f"{preview_id}.json")
        assert os.path.isfile(preview_file)
        
        # Verify file contents
        with open(preview_file, "r") as f:
            stored_data = json.load(f)
            
        assert stored_data["code"] == test_code
        assert stored_data["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_preview(self, file_storage, test_code, test_metadata):
        """Test retrieving a preview"""
        preview_id = "test-preview-456"
        
        # Store preview first
        await file_storage.store_preview(
            preview_id=preview_id,
            code=test_code,
            metadata=test_metadata
        )
        
        # Retrieve preview
        preview = await file_storage.get_preview(preview_id)
        
        # Verify retrieved data
        assert preview is not None
        assert preview["code"] == test_code
        assert preview["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_nonexistent_preview(self, file_storage):
        """Test retrieving a non-existent preview"""
        preview = await file_storage.get_preview("non-existent-id")
        assert preview is None

    @pytest.mark.asyncio
    async def test_publish_webtoy(self, file_storage, test_code, test_metadata):
        """Test publishing a WebToy"""
        webtoy_id = "test-webtoy-789"
        
        # Publish WebToy
        await file_storage.publish_webtoy(
            webtoy_id=webtoy_id,
            code=test_code,
            metadata=test_metadata
        )
        
        # Verify directory structure
        webtoys_dir = os.path.join(file_storage.base_path, "webtoys")
        assert os.path.isdir(webtoys_dir)
        
        # Verify webtoy file exists
        webtoy_file = os.path.join(webtoys_dir, f"{webtoy_id}.json")
        assert os.path.isfile(webtoy_file)
        
        # Verify file contents
        with open(webtoy_file, "r") as f:
            stored_data = json.load(f)
            
        assert stored_data["code"] == test_code
        assert stored_data["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_webtoy(self, file_storage, test_code, test_metadata):
        """Test retrieving a published WebToy"""
        webtoy_id = "test-webtoy-abc"
        
        # Publish WebToy first
        await file_storage.publish_webtoy(
            webtoy_id=webtoy_id,
            code=test_code,
            metadata=test_metadata
        )
        
        # Retrieve WebToy
        webtoy = await file_storage.get_webtoy(webtoy_id)
        
        # Verify retrieved data
        assert webtoy is not None
        assert webtoy["code"] == test_code
        assert webtoy["metadata"] == test_metadata

    @pytest.mark.asyncio
    async def test_get_nonexistent_webtoy(self, file_storage):
        """Test retrieving a non-existent WebToy"""
        webtoy = await file_storage.get_webtoy("non-existent-id")
        assert webtoy is None
        
    @pytest.mark.asyncio
    async def test_cleanup_old_previews(self, file_storage, test_code, test_metadata, monkeypatch):
        """Test cleanup of old previews"""
        import time
        from freezegun import freeze_time
        
        # Create some previews with different timestamps
        with freeze_time("2023-01-01"):
            await file_storage.store_preview(
                preview_id="old-preview-1",
                code=test_code,
                metadata={"timestamp": time.time()}
            )
            
        with freeze_time("2023-01-02"):
            await file_storage.store_preview(
                preview_id="old-preview-2",
                code=test_code,
                metadata={"timestamp": time.time()}
            )
            
        # Create a recent preview
        recent_preview_id = "recent-preview"
        await file_storage.store_preview(
            preview_id=recent_preview_id,
            code=test_code,
            metadata={"timestamp": time.time()}
        )
        
        # Set the max age to 1 day
        file_storage.preview_max_age = 86400  # 1 day in seconds
        
        # Run cleanup with current time as 2023-01-04
        with freeze_time("2023-01-04"):
            await file_storage.cleanup_old_previews()
        
        # Old previews should be gone
        old_preview_1 = await file_storage.get_preview("old-preview-1")
        old_preview_2 = await file_storage.get_preview("old-preview-2")
        recent_preview = await file_storage.get_preview(recent_preview_id)
        
        assert old_preview_1 is None
        assert old_preview_2 is None
        assert recent_preview is not None