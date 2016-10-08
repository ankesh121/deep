from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.styles import Font


class ExcelWriter:
    def __init__(self):
        self.wb = Workbook()

    def get_active(self):
        return self.wb.active

    def get_http_response(self, title):
        vwb = save_virtual_workbook(self.wb)
        response = HttpResponse(content=vwb, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename = %s' % (title+".xls")
        return response

    def auto_fit_cells_in_row(self, row_id):
        ws = self.get_active()
        row = ws.rows[row_id-1]
        for cell in row:
            ws.column_dimensions[cell.column].width = max(len(cell.value), 15)

    def append(self, rows):
        for row in rows:
            self.get_active().append(row)


class RowCollection:
    def __init__(self, n):
        self.rows = []
        for i in range(n):
            self.rows.append([])

    def permute_and_add(self, values):
        n = len(values)
        if n == 0:
            self.add_value("")
            return
        if n == 1:
            self.add_value(values[0])

        oldrows = self.rows[:]
        for i in range(1, n):
            for j, row in enumerate(oldrows):
                self.rows.insert(i*len(oldrows)+j, row.copy())

        for i in range(0, n):
            for j in range(0, len(oldrows)):
                self.rows[i*len(oldrows)+j].append(str(values[i]))
                print(self.rows[i*len(oldrows)+j], values[i])

    def add_value(self, value):
        for row in self.rows:
            row.append(str(value))

    def add_values(self, values):
        for val in values:
            self.add_value(val)