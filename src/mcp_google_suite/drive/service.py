from typing import Any, Dict, Optional

from googleapiclient.errors import HttpError

from mcp_google_suite.base_service import BaseGoogleService


class DriveService(BaseGoogleService):
    """Google Drive service implementation."""

    def __init__(self, auth=None):
        super().__init__("drive", "v3", auth)

    def search_files(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        """Search for files in Google Drive."""
        try:
            results = (
                self.service.files()
                .list(q=query, pageSize=page_size, fields="files(id, name, mimeType, webViewLink)")
                .execute()
            )

            return {"success": True, "files": results.get("files", [])}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new folder in Google Drive."""
        try:
            file_metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}

            if parent_id:
                file_metadata["parents"] = [parent_id]

            folder = (
                self.service.files()
                .create(body=file_metadata, fields="id, name, webViewLink")
                .execute()
            )

            return {"success": True, "folder": folder}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}

    def move_file(self, file_id: str, new_parent_id: str) -> Dict[str, Any]:
        """Move a file to a different folder."""
        try:
            # Get the file's current parents
            file = self.service.files().get(fileId=file_id, fields="parents").execute()

            previous_parents = ",".join(file.get("parents", []))

            # Move the file
            file = (
                self.service.files()
                .update(
                    fileId=file_id,
                    addParents=new_parent_id,
                    removeParents=previous_parents,
                    fields="id, name, parents, webViewLink",
                )
                .execute()
            )

            return {"success": True, "file": file}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file."""
        try:
            file = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, mimeType, webViewLink, parents, createdTime, modifiedTime",
                )
                .execute()
            )

            return {"success": True, "file": file}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}
