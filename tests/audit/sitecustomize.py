import socket
_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex

def _allowed(address):
    return isinstance(address, tuple) and address[0] in ('127.0.0.1', '::1', 'localhost')

def _connect(self, address):
    if not _allowed(address):
        raise RuntimeError('Audit offline guard: external network disabled')
    return _original_connect(self, address)

def _connect_ex(self, address):
    if not _allowed(address):
        raise RuntimeError('Audit offline guard: external network disabled')
    return _original_connect_ex(self, address)

socket.socket.connect = _connect
socket.socket.connect_ex = _connect_ex
