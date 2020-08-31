import os
import socket
import struct
import time
import random

def gen_nonce():
    return os.urandom(16)


class BetterSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.settimeout(5)

    def connect(self, addr):
        self.sock.connect(addr)

    def close(self):
        self.sock.close()

    def settimeout(self, value):
        self.sock.settimeout(value)

    def gettimeout(self):
        return self.sock.gettimeout()

    def send(self, data):
        self.sock.sendall(struct.pack('>I', len(data)) + data)
        time.sleep(random.random()/50)

    def recv(self):
        total_bytes = 4
        recv_bytes = 0
        data = b""
        while recv_bytes < total_bytes:
            chunk = self.sock.recv(8192)
            if not chunk:
                raise socket.error("Socket connection error")
            data += chunk
            recv_bytes += len(chunk)
            if total_bytes == 4 and recv_bytes >= 4:
                total_bytes += struct.unpack('>I', data[:4])[0]
                data = data[4:]
            time.sleep(0.01)
        time.sleep(random.random()/50)
        return data

