import socket
import time
import threading
from utils import netutils, cryptoutils
from utils.netconst import *


#------------
def dummy_merge(download_filepath, upload_filepath):
    input("This is test merging function. It only waits for input.\n")
#------------


def pull(client_socket, fernet, download_filepath):
    encrypted_data = client_socket.recv()
    data = fernet.decrypt(encrypted_data)
    with open(download_filepath, "wb") as datafile:
        datafile.write(data)


def push(client_socket, fernet, download_filepath, upload_filepath):
    with open(upload_filepath, "rb") as datafile:
        data = datafile.read()
    encrypted_data = fernet.encrypt(data)
    client_socket.send(encrypted_data)


def wait_for_merge(client_socket, merge_thread):
    interval = client_socket.gettimeout() / 2
    while True:
        status = STAT_ALIVE if merge_thread.is_alive() else STAT_READY
        client_socket.send(status)
        if status == STAT_ALIVE:
            time.sleep(interval)
        elif status == STAT_READY:
            client_socket.recv()
            return


def connection_auth(client_socket, datafile_name, authkey):
    nonce = client_socket.recv()
    print("[*] Received nonce: {}".format(nonce))
    authkey_nonce = cryptoutils.gen_hash(authkey, nonce, cryptoutils.hashes.SHA256())
    client_socket.send(datafile_name)
    client_socket.send(authkey_nonce)
    print("[*] Sent authkey with nonce, waiting for verification")
    auth_status = client_socket.recv()
    if auth_status == AUTH_DATAFILE:
        print("[*] Wrong data file name, closing connection")
        client_socket.close()
        return None
    elif auth_status == AUTH_FAILED:
        print("[*] Authentication failed, closing connection")
        client_socket.close()
        return None
    print("[*] Authentication successful")
    return nonce
    

def perform_command(client_socket, command, fernet, download_filepath="", upload_filepath=""):
    if command == "pull":
        print("[*] Requesting pull operation")
        client_socket.send(CMD_PULL)
        pull(client_socket, fernet, download_filepath)
    elif command == "push":
        print("[*] Requesting push operation")
        client_socket.send(CMD_PUSH)
        pull(client_socket, fernet, download_filepath)
        #-------
        merge_thread = threading.Thread(target=dummy_merge, args=(download_filepath, upload_filepath))
        merge_thread.start()
        #-------
        wait_for_merge(client_socket, merge_thread)
        push(client_socket, fernet, download_filepath, upload_filepath)
    print("[*] Operation performed successfully, ending session")


def server_handle(client_socket, datafile_name, authkey, command, download_filepath, upload_filepath):
    nonce = connection_auth(client_socket, datafile_name, authkey)
    if nonce is None:
        return
    fernet = cryptoutils.gen_fernet(authkey, b"", cryptoutils.hashes.SHA256())
    perform_command(client_socket, command, fernet, download_filepath, upload_filepath)


def client(host, port, datafile_name, authkey, command, download_filepath="", upload_filepath=""):
    client_socket = netutils.BetterSocket()
    try:
        client_socket.connect((host, port))
    except OSError as e:
        print("[-] Exception during connection to server:")
        print(e)
        return e
    print("[*] Connected to server at {}:{}".format(host,port))
    try:
        server_handle(client_socket, datafile_name, authkey, command, download_filepath, upload_filepath)
    except OSError as e:
        print("[-] Exception with socket connection:")
        print(e)
        return e
    client_socket.close()

pwd_hash = b"\xef\x92\xb7x\xba\xfew\x1e\x89$[\x89\xec\xbc\x08\xa4JN\x16l\x06e\x99\x11\x88\x1f8=Ds\xe9O"


if __name__ == "__main__":
    client('localhost',
           2137,
           b'datafile1',
           pwd_hash,
           'push',
           download_filepath="ftdl",
           upload_filepath="ftul")
