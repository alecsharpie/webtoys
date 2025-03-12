"""
Storage Service for WebToys

This service handles persistent storage of WebToy code and metadata.
It supports different storage backends (file system, S3, database).
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

# Setup logging
logger = logging.getLogger(__name__)


class StorageService:
    def __init__(
        self, storage_type: str = "file", connection_string: str | None = None
    ):
        """
        Initialize the storage service

        Args:
            storage_type: Type of storage ('file', 's3', or 'database')
            connection_string: Connection string for the storage (if applicable)
        """
        self.storage_type = storage_type.lower()
        self.connection_string = connection_string

        # Initialize storage backend
        if self.storage_type == "file":
            self._init_file_storage()
        elif self.storage_type == "s3":
            self._init_s3_storage()
        elif self.storage_type == "database":
            self._init_database_storage()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

        logger.info(f"Storage service initialized with type: {storage_type}")

    def _init_file_storage(self):
        """Initialize file system storage"""
        # Create storage directories
        self.base_dir = (
            Path(self.connection_string)
            if self.connection_string
            else Path("./storage")
        )
        self.previews_dir = self.base_dir / "previews"
        self.webtoys_dir = self.base_dir / "webtoys"

        # Ensure directories exist
        self.previews_dir.mkdir(parents=True, exist_ok=True)
        self.webtoys_dir.mkdir(parents=True, exist_ok=True)

        # Setup cleanup task for preview files
        cleanup_task = asyncio.create_task(self._cleanup_old_previews())
        # Prevent task from being garbage collected
        self._cleanup_task = cleanup_task

    def _init_s3_storage(self):
        """Initialize S3 storage"""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError

            # Parse connection string for S3
            if self.connection_string:
                # Format: endpoint,access_key,secret_key,bucket
                parts = self.connection_string.split(",")
                endpoint = parts[0] if len(parts) > 0 else None
                access_key = parts[1] if len(parts) > 1 else None
                secret_key = parts[2] if len(parts) > 2 else None
                self.bucket = parts[3] if len(parts) > 3 else "webtoys"
            else:
                endpoint = None
                access_key = None
                secret_key = None
                self.bucket = "webtoys"

            # Initialize S3 client
            self.s3 = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )

            # Check if bucket exists, create if not
            try:
                self.s3.head_bucket(Bucket=self.bucket)
            except Exception as e:
                logger.info(f"Creating bucket {self.bucket}: {e!s}")
                self.s3.create_bucket(Bucket=self.bucket)

            logger.info(f"S3 storage initialized with bucket: {self.bucket}")

        except (ImportError, NoCredentialsError) as e:
            logger.error(f"Failed to initialize S3 storage: {e!s}")
            raise RuntimeError(f"S3 storage initialization failed: {e!s}")

    def _init_database_storage(self):
        """Initialize database storage"""
        try:
            import sqlite3

            # Use SQLite for simplicity in this example
            # In production, you'd use a more robust database
            db_path = self.connection_string or "./storage/webtoys.db"

            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # Initialize database connection
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()

            # Create tables if they don't exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS previews (
                    id TEXT PRIMARY KEY,
                    html TEXT,
                    css TEXT,
                    js TEXT,
                    description TEXT,
                    created_at REAL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS webtoys (
                    id TEXT PRIMARY KEY,
                    html TEXT,
                    css TEXT,
                    js TEXT,
                    description TEXT,
                    preview_id TEXT,
                    created_at REAL
                )
            """)

            self.conn.commit()
            logger.info("Database storage initialized")

        except ImportError as e:
            logger.error(f"Failed to initialize database storage: {e!s}")
            raise RuntimeError(f"Database storage initialization failed: {e!s}")

    async def store_preview(
        self, preview_id: str, code: dict[str, str], metadata: dict[str, Any]
    ) -> str:
        """
        Store a WebToy preview

        Args:
            preview_id: Unique identifier for the preview
            code: Dictionary containing HTML, CSS, and JS code
            metadata: Additional metadata about the preview

        Returns:
            The preview ID
        """
        if self.storage_type == "file":
            await self._store_preview_file(preview_id, code, metadata)
        elif self.storage_type == "s3":
            await self._store_preview_s3(preview_id, code, metadata)
        elif self.storage_type == "database":
            await self._store_preview_db(preview_id, code, metadata)

        logger.info(f"Stored preview with ID: {preview_id}")
        return preview_id

    async def get_preview(self, preview_id: str) -> dict[str, Any] | None:
        """
        Retrieve a WebToy preview

        Args:
            preview_id: Unique identifier for the preview

        Returns:
            Dictionary with code and metadata, or None if not found
        """
        if self.storage_type == "file":
            return await self._get_preview_file(preview_id)
        elif self.storage_type == "s3":
            return await self._get_preview_s3(preview_id)
        elif self.storage_type == "database":
            return await self._get_preview_db(preview_id)

        return None

    async def publish_webtoy(
        self, webtoy_id: str, code: dict[str, str], metadata: dict[str, Any]
    ) -> str:
        """
        Publish a WebToy for permanent storage

        Args:
            webtoy_id: Unique identifier for the WebToy
            code: Dictionary containing HTML, CSS, and JS code
            metadata: Additional metadata about the WebToy

        Returns:
            The WebToy ID
        """
        if self.storage_type == "file":
            await self._publish_webtoy_file(webtoy_id, code, metadata)
        elif self.storage_type == "s3":
            await self._publish_webtoy_s3(webtoy_id, code, metadata)
        elif self.storage_type == "database":
            await self._publish_webtoy_db(webtoy_id, code, metadata)

        logger.info(f"Published WebToy with ID: {webtoy_id}")
        return webtoy_id

    async def get_webtoy(self, webtoy_id: str) -> dict[str, Any] | None:
        """
        Retrieve a published WebToy

        Args:
            webtoy_id: Unique identifier for the WebToy

        Returns:
            Dictionary with code and metadata, or None if not found
        """
        if self.storage_type == "file":
            return await self._get_webtoy_file(webtoy_id)
        elif self.storage_type == "s3":
            return await self._get_webtoy_s3(webtoy_id)
        elif self.storage_type == "database":
            return await self._get_webtoy_db(webtoy_id)

        return None

    async def list_webtoys(
        self, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        List published WebToys

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            List of WebToy metadata
        """
        if self.storage_type == "file":
            return await self._list_webtoys_file(limit, offset)
        elif self.storage_type == "s3":
            return await self._list_webtoys_s3(limit, offset)
        elif self.storage_type == "database":
            return await self._list_webtoys_db(limit, offset)

        return []

    # File storage implementation
    async def _store_preview_file(
        self, preview_id: str, code: dict[str, str], metadata: dict[str, Any]
    ):
        """Store preview in file system"""
        preview_path = self.previews_dir / f"{preview_id}.json"

        # Create preview data
        preview_data = {"code": code, "metadata": metadata}

        # Write to file
        with open(preview_path, "w") as f:
            json.dump(preview_data, f)

    async def _get_preview_file(self, preview_id: str) -> dict[str, Any] | None:
        """Get preview from file system"""
        preview_path = self.previews_dir / f"{preview_id}.json"

        if not preview_path.exists():
            return None

        try:
            with open(preview_path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse preview JSON for ID: {preview_id}")
            return None

    async def _publish_webtoy_file(
        self, webtoy_id: str, code: dict[str, str], metadata: dict[str, Any]
    ):
        """Publish WebToy to file system"""
        webtoy_path = self.webtoys_dir / f"{webtoy_id}.json"

        # Create WebToy data
        webtoy_data = {"code": code, "metadata": metadata}

        # Write to file
        with open(webtoy_path, "w") as f:
            json.dump(webtoy_data, f)

    async def _get_webtoy_file(self, webtoy_id: str) -> dict[str, Any] | None:
        """Get WebToy from file system"""
        webtoy_path = self.webtoys_dir / f"{webtoy_id}.json"

        if not webtoy_path.exists():
            return None

        try:
            with open(webtoy_path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse WebToy JSON for ID: {webtoy_id}")
            return None

    async def _list_webtoys_file(self, limit: int, offset: int) -> list[dict[str, Any]]:
        """List WebToys from file system"""
        # Get all webtoy files
        webtoy_files = list(self.webtoys_dir.glob("*.json"))

        # Sort by modification time (newest first)
        webtoy_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Apply pagination
        paginated_files = webtoy_files[offset : offset + limit]

        # Load each WebToy
        webtoys = []
        for file_path in paginated_files:
            try:
                with open(file_path) as f:
                    webtoy_data = json.load(f)

                    # Extract ID from filename
                    webtoy_id = file_path.stem

                    # Create summary
                    webtoys.append(
                        {
                            "id": webtoy_id,
                            "description": webtoy_data["metadata"].get(
                                "description", ""
                            ),
                            "created_at": webtoy_data["metadata"].get("created_at", 0),
                        }
                    )
            except (OSError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load WebToy file {file_path}: {e!s}")

        return webtoys

    async def _cleanup_old_previews(self):
        """Cleanup old preview files periodically"""
        while True:
            try:
                # Sleep for 1 hour
                await asyncio.sleep(3600)

                logger.info("Starting cleanup of old preview files")

                # Get all preview files
                preview_files = list(self.previews_dir.glob("*.json"))

                # Current time
                current_time = time.time()

                # Delete files older than 24 hours
                for file_path in preview_files:
                    try:
                        file_age = current_time - file_path.stat().st_mtime

                        # If older than 24 hours (86400 seconds)
                        if file_age > 86400:
                            file_path.unlink()
                            logger.info(f"Deleted old preview file: {file_path}")
                    except OSError as e:
                        logger.error(
                            f"Failed to process file {file_path} during cleanup: {e!s}"
                        )

                logger.info("Completed cleanup of old preview files")

            except asyncio.CancelledError:
                # Handle shutdown
                logger.info("Cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in preview cleanup task: {e!s}")

    # S3 storage implementation (simplified)
    async def _store_preview_s3(
        self, preview_id: str, code: dict[str, str], metadata: dict[str, Any]
    ):
        """Store preview in S3"""
        preview_data = {"code": code, "metadata": metadata}

        # Convert to JSON
        preview_json = json.dumps(preview_data)

        # Upload to S3
        self.s3.put_object(
            Bucket=self.bucket, Key=f"previews/{preview_id}.json", Body=preview_json
        )

    async def _get_preview_s3(self, preview_id: str) -> dict[str, Any] | None:
        """Get preview from S3"""
        try:
            response = self.s3.get_object(
                Bucket=self.bucket, Key=f"previews/{preview_id}.json"
            )

            # Parse JSON
            preview_json = response["Body"].read().decode("utf-8")
            return json.loads(preview_json)

        except Exception as e:
            logger.error(f"Failed to get preview from S3: {e!s}")
            return None

    async def _publish_webtoy_s3(
        self, webtoy_id: str, code: dict[str, str], metadata: dict[str, Any]
    ):
        """Publish WebToy to S3"""
        webtoy_data = {"code": code, "metadata": metadata}

        # Convert to JSON
        webtoy_json = json.dumps(webtoy_data)

        # Upload to S3
        self.s3.put_object(
            Bucket=self.bucket, Key=f"webtoys/{webtoy_id}.json", Body=webtoy_json
        )

    async def _get_webtoy_s3(self, webtoy_id: str) -> dict[str, Any] | None:
        """Get WebToy from S3"""
        try:
            response = self.s3.get_object(
                Bucket=self.bucket, Key=f"webtoys/{webtoy_id}.json"
            )

            # Parse JSON
            webtoy_json = response["Body"].read().decode("utf-8")
            return json.loads(webtoy_json)

        except Exception as e:
            logger.error(f"Failed to get WebToy from S3: {e!s}")
            return None

    async def _list_webtoys_s3(self, limit: int, offset: int) -> list[dict[str, Any]]:
        """List WebToys from S3 (simplified implementation)"""
        try:
            # List objects in the webtoys prefix
            response = self.s3.list_objects_v2(
                Bucket=self.bucket, Prefix="webtoys/", MaxKeys=limit + offset
            )

            # Skip offset and limit results
            contents = response.get("Contents", [])[offset : offset + limit]

            webtoys = []
            for item in contents:
                try:
                    # Get object
                    obj_response = self.s3.get_object(
                        Bucket=self.bucket, Key=item["Key"]
                    )

                    # Parse JSON
                    webtoy_json = obj_response["Body"].read().decode("utf-8")
                    webtoy_data = json.loads(webtoy_json)

                    # Extract ID from key
                    webtoy_id = item["Key"].split("/")[-1].split(".")[0]

                    # Create summary
                    webtoys.append(
                        {
                            "id": webtoy_id,
                            "description": webtoy_data["metadata"].get(
                                "description", ""
                            ),
                            "created_at": webtoy_data["metadata"].get("created_at", 0),
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to process S3 object {item['Key']}: {e!s}")

            return webtoys

        except Exception as e:
            logger.error(f"Failed to list WebToys from S3: {e!s}")
            return []

    # Database storage implementation (simplified)
    async def _store_preview_db(
        self, preview_id: str, code: dict[str, str], metadata: dict[str, Any]
    ):
        """Store preview in database"""
        # Extract code components
        html = code.get("html", "")
        css = code.get("css", "")
        js = code.get("js", "")
        description = metadata.get("description", "")
        created_at = metadata.get("timestamp", time.time())

        # Insert into database
        self.cursor.execute(
            "INSERT OR REPLACE INTO previews (id, html, css, js, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (preview_id, html, css, js, description, created_at),
        )
        self.conn.commit()

    async def _get_preview_db(self, preview_id: str) -> dict[str, Any] | None:
        """Get preview from database"""
        # Query database
        self.cursor.execute(
            "SELECT id, html, css, js, description, created_at FROM previews WHERE id = ?",
            (preview_id,),
        )

        row = self.cursor.fetchone()
        if not row:
            return None

        # Create preview data
        return {
            "code": {"html": row[1], "css": row[2], "js": row[3]},
            "metadata": {"description": row[4], "timestamp": row[5]},
        }

    async def _publish_webtoy_db(
        self, webtoy_id: str, code: dict[str, str], metadata: dict[str, Any]
    ):
        """Publish WebToy to database"""
        # Extract code components
        html = code.get("html", "")
        css = code.get("css", "")
        js = code.get("js", "")
        description = metadata.get("description", "")
        preview_id = metadata.get("preview_id", "")
        created_at = metadata.get("created_at", time.time())

        # Insert into database
        self.cursor.execute(
            "INSERT OR REPLACE INTO webtoys (id, html, css, js, description, preview_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (webtoy_id, html, css, js, description, preview_id, created_at),
        )
        self.conn.commit()

    async def _get_webtoy_db(self, webtoy_id: str) -> dict[str, Any] | None:
        """Get WebToy from database"""
        # Query database
        self.cursor.execute(
            "SELECT id, html, css, js, description, preview_id, created_at FROM webtoys WHERE id = ?",
            (webtoy_id,),
        )

        row = self.cursor.fetchone()
        if not row:
            return None

        # Create WebToy data
        return {
            "code": {"html": row[1], "css": row[2], "js": row[3]},
            "metadata": {
                "description": row[4],
                "preview_id": row[5],
                "created_at": row[6],
            },
        }

    async def _list_webtoys_db(self, limit: int, offset: int) -> list[dict[str, Any]]:
        """List WebToys from database"""
        # Query database
        self.cursor.execute(
            "SELECT id, description, created_at FROM webtoys ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )

        rows = self.cursor.fetchall()

        # Create summaries
        return [
            {"id": row[0], "description": row[1], "created_at": row[2]} for row in rows
        ]
