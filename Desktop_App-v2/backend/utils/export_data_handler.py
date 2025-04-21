from classes import ExportData

def init_exportdata(app):
    app.exportdata = ExportData()

def get_exportdata(app)->ExportData:
    return app.exportdata

def override_exportdata(app, new_ed)->ExportData:
    app.exportdata=new_ed
    return app.exportdata