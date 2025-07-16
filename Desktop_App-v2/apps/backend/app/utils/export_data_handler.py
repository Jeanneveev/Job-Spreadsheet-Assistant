from ..models import ExportData

def init_export_data(app):
    app.exportdata = ExportData()

def get_export_data(app)->ExportData:
    return app.exportdata

def override_export_data(app, new_ed)->ExportData:
    app.exportdata=new_ed
    return app.exportdata