import sys
import socket
import logging
import json
import dicttoxml
import os
import ssl
import threading

alldata = dict()
alldata["1"] = dict(nomor=1, nama="Alisson Becker", posisi="Goalkeeper")
alldata["2"] = dict(nomor=2, nama="Fabinho", posisi="Midfielders")
alldata["3"] = dict(nomor=3, nama="Virgil van Dijk", posisi="Defenders")
alldata["4"] = dict(nomor=4, nama="Ibrahima Konate", posisi="Defenders")
alldata["5"] = dict(nomor=5, nama="Thiago Alcantara", posisi="Midfielders")
alldata["6"] = dict(nomor=6, nama="James Milner", posisi="Midfielders")
alldata["7"] = dict(nomor=7, nama="Naby Keita", posisi="Midfielders")
alldata["8"] = dict(nomor=8, nama="Roberto Firminio", posisi="Forwards")
alldata["9"] = dict(nomor=9, nama="Sadio Mane", posisi="Forwards")
alldata["10"] = dict(nomor=10, nama="Mohamed Salah", posisi="Forwards")
alldata["11"] = dict(nomor=11, nama="Joe Gomez", posisi="Defenders")
alldata["12"] = dict(nomor=12, nama="Adrian", posisi="Goalkeeper")
alldata["13"] = dict(nomor=13, nama="Jordan Henderson", posisi="Midfielders")
alldata["14"] = dict(nomor=14, nama="Alex Oxlade-Chamberlain", posisi="Midfielders")
alldata["15"] = dict(nomor=15, nama="Curtis Jones", posisi="Midfielders")
alldata["16"] = dict(nomor=16, nama="Takumi Minamino", posisi="Forwards")
alldata["17"] = dict(nomor=17, nama="Kostas Tsimikas", posisi="Defenders")
alldata["18"] = dict(nomor=18, nama="Luis Diaz", posisi="Forwards")
alldata["19"] = dict(nomor=19, nama="Andy Robertson", posisi="Defenders")
alldata["20"] = dict(nomor=20, nama="Divock Origi", posisi="Forwards")

def versi():
    return "versi 0.0.1"

def proses_request(request_string):
    # format request
    # NAMACOMMAND spasi PARAMETER
    cstring = request_string.split(" ")
    hasil = None
    try:
        command = cstring[0].strip()
        if command == "getdatapemain":
            # getdata spasi parameter1
            # parameter1 harus berupa nomor pemain
            logging.warning("getdata")
            nomorpemain = cstring[1].strip()
            try:
                logging.warning(f"data {nomorpemain} ketemu")
                hasil = alldata[nomorpemain]
            except:
                hasil = None
        elif command == "versi":
            hasil = versi()
    except:
        hasil = None
    return hasil

def serialisasi(a):
    # print(a)
    # serialized = str(dicttoxml.dicttoxml(a))
    serialized = json.dumps(a)
    logging.warning("serialized data")
    logging.warning(serialized)
    return serialized

def run_server(server_address, is_secure=False):
    # ------------------------------ SECURE SOCKET INITIALIZATION ----
    if is_secure == True:
        print(os.getcwd())
        cert_location = os.getcwd() + "/certs/"
        socket_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        socket_context.load_cert_chain(
            certfile=cert_location + "domain.crt", keyfile=cert_location + "domain.key"
        )
    # ---------------------------------

    # --- INISIALISATION ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    logging.warning(f"starting up on {server_address}")
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1000)

    threads = dict()
    count_threads = 0

    while True:
        # Wait for a connection
        logging.warning("waiting for a connection")
        koneksi, client_address = sock.accept()
        logging.warning(f"Incoming connection from {client_address}")
        # Receive the data in small chunks and retransmit it

        try:
            if is_secure == True:
                connection = socket_context.wrap_socket(koneksi, server_side=True)
            else:
                connection = koneksi
            threads[count_threads] = threading.Thread(
                target=proc_connection, args=(client_address, connection)
            )
            threads[count_threads].start()
            count_threads += 1
            # Clean up the connection
        except ssl.SSLError as error_ssl:
            logging.warning(f"SSL error: {str(error_ssl)}")

def proc_connection(client_address, connection):
    selesai = False
    data_received = ""  # string
    while True:
        data = connection.recv(32)
        logging.warning(f"received {data}")
        if data:
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                selesai = True

            if selesai == True:
                hasil = proses_request(data_received)
                logging.warning(f"hasil proses: {hasil}")
                hasil = serialisasi(hasil)
                hasil += "\r\n\r\n"
                connection.sendall(hasil.encode())
                selesai = False
                data_received = ""  # string
                break

        else:
            logging.warning(f"no more data from {client_address}")
            break

if __name__ == "__main__":
    try:
        run_server(("0.0.0.0", 12000), is_secure=False)
    except KeyboardInterrupt:
        logging.warning("Control-C: Program berhenti")
        exit(0)
    finally:
        logging.warning("seelsai")
