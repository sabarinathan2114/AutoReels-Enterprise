import os
import re
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status

class UploadSecurityService:
    """
    Asset Upload Security & Content-Type Hardening Service (SEC-14).
    Validates file magic bytes (file signature), sanitizes filenames to prevent
    path traversal, and bounds upload payload sizes.
    """

    # Magic byte signatures
    MAGIC_SIGNATURES = {
        "png": [b"\x89PNG\r\n\x1a\n"],
        "jpeg": [b"\xff\xd8\xff"],
        "jpg": [b"\xff\xd8\xff"],
        "mp3": [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"],
        "wav": [b"RIFF"],
        "mp4": [b"ftyp"]
    }

    # Maximum file size limits (bytes)
    MAX_SIZE_BYTES = {
        "image": 5 * 1024 * 1024,    # 5 MB
        "audio": 15 * 1024 * 1024,   # 15 MB
        "video": 100 * 1024 * 1024   # 100 MB
    }

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitizes input filenames to protect against Path Traversal and Null Byte Injection.
        """
        if not filename or "\0" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "INVALID_FILENAME", "message": "Filename contains illegal null bytes or is empty."}
            )

        # Remove directory paths (both Unix and Windows style)
        clean = os.path.basename(filename.replace("\\", "/"))

        # Strip dangerous path traversal patterns
        clean = re.sub(r"\.\.+[/]?", "", clean)

        # Disallow hidden files
        if clean.startswith("."):
            clean = "upload_" + clean.lstrip(".")

        # Keep only alphanumeric and safe characters
        clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean)

        if not clean or clean == ".":
            clean = "safe_upload.bin"

        return clean

    @staticmethod
    def verify_magic_bytes(content: bytes, extension: str) -> bool:
        """
        Verifies that the raw byte header matches the declared file extension.
        """
        ext = extension.lower().lstrip(".")
        if ext not in UploadSecurityService.MAGIC_SIGNATURES:
            return False

        if ext == "wav":
            return content.startswith(b"RIFF") and len(content) > 12 and content[8:12] == b"WAVE"

        if ext == "mp4":
            # MP4 containers have 'ftyp' in bytes 4..8
            return len(content) > 12 and b"ftyp" in content[:16]

        expected_signatures = UploadSecurityService.MAGIC_SIGNATURES[ext]
        for sig in expected_signatures:
            if content.startswith(sig):
                return True
        return False

    @staticmethod
    def validate_upload(
        file_bytes: bytes,
        filename: str,
        category: str = "image"
    ) -> Dict[str, Any]:
        """
        Comprehensive upload gate verifying size, extension, and binary magic bytes.
        """
        # 1. Filename sanitization
        clean_name = UploadSecurityService.sanitize_filename(filename)
        _, ext = os.path.splitext(clean_name)
        ext = ext.lower().lstrip(".")

        allowed_extensions = {
            "image": ["png", "jpg", "jpeg"],
            "audio": ["mp3", "wav"],
            "video": ["mp4"]
        }

        if ext not in allowed_extensions.get(category, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "UNSUPPORTED_FILE_TYPE",
                    "message": f"Extension .{ext} is not allowed for category '{category}'."
                }
            )

        # 2. Size check
        max_size = UploadSecurityService.MAX_SIZE_BYTES.get(category, 10 * 1024 * 1024)
        if len(file_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": "FILE_TOO_LARGE",
                    "message": f"File size {len(file_bytes)} bytes exceeds limit {max_size} bytes."
                }
            )

        # 3. Magic bytes validation
        if not UploadSecurityService.verify_magic_bytes(file_bytes, ext):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_FILE_SIGNATURE",
                    "message": f"File magic bytes do not match declared format .{ext}."
                }
            )

        return {
            "valid": True,
            "sanitized_filename": clean_name,
            "extension": ext,
            "size_bytes": len(file_bytes)
        }
