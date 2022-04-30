from main.models.models import Dummy


def get_dummy_data_from_database(**kwargs):
    response =  Dummy.query.filter_by(column1 = 1).first()
    return {"colum1": response.column1 , "column2": response.column2}


import socket


def is_connected_to_internet():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False