from ..models.linked_list import LinkedList

def init_ll(app):
    app.linked_list = LinkedList()

def get_ll(app)->LinkedList:
    return app.linked_list

def override_ll(app, new_ll)->LinkedList:
    app.linked_list=new_ll
    return app.linked_list