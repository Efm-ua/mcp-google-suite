from typing import Any, Dict, List, Optional

from googleapiclient.errors import HttpError

from mcp_google_suite.base_service import BaseGoogleService


class SheetsService(BaseGoogleService):
    """Google Sheets service implementation."""

    def __init__(self, auth=None):
        super().__init__("sheets", "v4", auth)

    def create_spreadsheet(self, title: str, sheets: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new Google Spreadsheet with optional sheets."""
        try:
            spreadsheet_body = {"properties": {"title": title}}

            if sheets:
                spreadsheet_body["sheets"] = [
                    {"properties": {"title": sheet_name}} for sheet_name in sheets
                ]

            spreadsheet = self.service.spreadsheets().create(body=spreadsheet_body).execute()

            return {"success": True, "spreadsheet": spreadsheet}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}

    def get_values(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """Get values from a specific range in a spreadsheet."""
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )

            return {"success": True, "values": result.get("values", [])}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}

    def update_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        major_dimension: str = "ROWS",
    ) -> Dict[str, Any]:
        """Update values in a specific range of a spreadsheet."""
        try:
            body = {"values": values, "majorDimension": major_dimension}

            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )

            return {"success": True, "result": result}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}

    def append_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        major_dimension: str = "ROWS",
    ) -> Dict[str, Any]:
        """Append values to a spreadsheet."""
        try:
            body = {"values": values, "majorDimension": major_dimension}

            result = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )

            return {"success": True, "result": result}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}

    def clear_values(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """Clear values from a specific range in a spreadsheet."""
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .clear(spreadsheetId=spreadsheet_id, range=range_name, body={})
                .execute()
            )

            return {"success": True, "result": result}
        except HttpError as error:
            return {"success": False, **self.handle_error(error)}
