import io

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response


EXPORT_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


def header_map(values) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, value in enumerate(values):
        if value is None:
            continue
        mapping[str(value).strip()] = idx
    return mapping


class OpenpyxlXlsxMixin:
    export_sheet_title = "Sheet1"
    export_filename = "export.xlsx"

    def get_export_headers(self):
        raise NotImplementedError

    def get_export_rows(self, request):
        raise NotImplementedError

    def get_export_sheet_title(self):
        return self.export_sheet_title

    def get_export_filename(self):
        return self.export_filename

    def get_import_required_headers(self):
        return []

    def get_import_row_value(self, row, header_mapping, key):
        idx = header_mapping.get(key)
        return row[idx] if idx is not None else None

    def handle_import_row(self, row, header_mapping):
        raise NotImplementedError

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser], url_path="export-xlsx")
    def export_xlsx(self, request):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = self.get_export_sheet_title()
        ws.append(self.get_export_headers())

        for row in self.get_export_rows(request):
            ws.append(row)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type=EXPORT_CONTENT_TYPE,
        )
        response["Content-Disposition"] = (
            f"attachment; filename={self.get_export_filename()}"
        )
        return response

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser], url_path="import-xlsx")
    def import_xlsx(self, request):
        from openpyxl import load_workbook

        upload = request.FILES.get("xlsx_file") or request.FILES.get("file")
        if not upload:
            return Response(
                {"detail": "Missing XLSX file (field: xlsx_file or file)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        wb = load_workbook(upload)
        ws = wb.active
        header_mapping = header_map([cell.value for cell in ws[1]])
        required = self.get_import_required_headers()
        missing = [name for name in required if name not in header_mapping]
        if missing:
            return Response(
                {"detail": f"Missing columns: {', '.join(missing)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = 0
        updated = 0
        skipped = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            result = self.handle_import_row(row, header_mapping)
            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1
            else:
                skipped += 1

        return Response({"created": created, "updated": updated, "skipped": skipped})
