import socket
import time
from utils import netutils, cryptoutils
from utils.netconst import *


def check_datafile_authkey(authfilepath, datafile_name, authkey_nonce, nonce):
    with open(authfilepath, "rb") as authfile:
        for line in authfile.readlines():
            datafile_name_candidate, authkey = line.strip().split()
            if datafile_name_candidate != datafile_name:
                continue
            authkey_nonce_candidate = cryptoutils.gen_hash(authkey, nonce, cryptoutils.hashes.SHA256())
            if authkey_nonce_candidate == authkey_nonce:
                return datafile_name, authkey
            else:
                return datafile_name, None
    return None, None


def handle_pull(client_socket, fernet, datafilepath):
    with open(datafilepath, "rb") as datafile:
        data = datafile.read()
    encr_data = fernet.encrypt(data)
    client_socket.send(encr_data)


def handle_push(client_socket, fernet, datafilepath):
    encr_data = client_socket.recv()
    data = fernet.decrypt(encr_data)
    with open(datafilepath, "wb") as datafile:
        datafile.write(data)


def keep_alive(client_socket):
    interval = client_socket.gettimeout() / 2
    while True:
        status = client_socket.recv()
        if status == STAT_ALIVE:
            time.sleep(interval)
        elif status == STAT_READY:
            client_socket.send(STAT_READY)
            return


def connection_auth(client_socket, nonce, authfilepath):
    client_socket.send(nonce)
    print("[*] Sent nonce: {}".format(nonce))
    datafile_name = client_socket.recv()
    authkey_nonce = client_socket.recv()
    print("[*] Received authkey with nonce, verifying authentication")
    datafilepath, authkey = check_datafile_authkey(authfilepath, datafile_name, authkey_nonce, nonce)
    if datafilepath is None:
        print("[*] Wrong data file name, closing connection")
        client_socket.send(AUTH_DATAFILE)
        client_socket.close()
        return None, None
    elif authkey is None:
        print("[*] Authentication failed, closing connection")
        client_socket.send(AUTH_FAILED)
        client_socket.close()
        return None, None
    print("[*] Authenticaion successful")
    client_socket.send(AUTH_OK)
    return authkey, datafilepath


def perform_command(client_socket, datafilepath, fernet):
    command = client_socket.recv()
    if command == CMD_PULL:
        print("[*] Client requested pull operation")
        handle_pull(client_socket, fernet, datafilepath)
    elif command == CMD_PUSH:
        print("[*] Client requested push operation")
        handle_pull(client_socket, fernet, datafilepath)
        keep_alive(client_socket)
        handle_push(client_socket, fernet, datafilepath)
    print("[*] Operation performed successfully, ending client's session\n")


def client_handle(client_socket, authfilepath):
    nonce = netutils.gen_nonce()
    authkey, datafilepath = connection_auth(client_socket, nonce, authfilepath)
    if authkey is None or datafilepath is None:
        return
    fernet = cryptoutils.gen_fernet(authkey, b"", cryptoutils.hashes.SHA256())
    perform_command(client_socket, datafilepath, fernet)

def server(host, port, authfilepath):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((host, port))
    except OSError as e:
        print("[-] Exception during address binding:")
        print(e)
        return e
    server_socket.listen()
    print("[*] Listening at {}:{}".format(host,port))
    
    while True:
        client_sock, addr = server_socket.accept()
        client_socket = netutils.BetterSocket(client_sock)
        print()
        print("[*] Received connection from {}:{}".format(addr[0], addr[1]))
        try:
            client_handle(client_socket, authfilepath)
        except OSError as e:
            print("[-] Exception with socket connection:")
            print(e)
        client_socket.close()


if __name__ == "__main__":
    server('localhost',
           2137,
           'authfile')
