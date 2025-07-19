from ..models import ExportData

def init_export_data(app):
    app.export_data = ExportData()

def get_export_data(app)->ExportData:
    return app.export_data

def override_export_data(app, new_ed)->ExportData:
    app.export_data=new_ed
    return app.export_data