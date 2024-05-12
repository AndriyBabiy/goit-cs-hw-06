import socket
import logging
from pathlib import Path
from urllib.parse import unquote_plus
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import datetime

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI_DB = "mongodb://mongodb:27017/mongodb-1"
BASE_DIR = Path(__file__).parent
CHUNK_SIZE = 1024
HTTP_PORT = 3000
SOCKET_PORT = 5000
HTTP_HOST = "0.0.0.0"
SOCKET_HOST = "127.0.0.1"

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class HttpHandler(BaseHTTPRequestHandler):
    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
    
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('./front/index.html')
        elif pr_url.path == '/message':
            self.send_html_file('./front/message.html')
        else:
            self.send_html_file('./front/error.html', 404)


    def do_POST(self):
      data = self.rfile.read(int(self.headers['Content-Length']))
      data_parse = urllib.parse.unquote_plus(data.decode())
      data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
      current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
      data_dict = {'date': current_date, **data_dict}

      try:
        client_socket = socket. socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT)) 
        client_socket.close()
      except socket.error:
        self.send_html_file('./front/error.html', 404)
        logging.error("failed to send data")
      
      self.send_response(302)
      self.send_header('Location', '/')
      self.end_headers()

def run_http_server():
    http = HTTPServer((HTTP_HOST, HTTP_PORT), HttpHandler)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
    

def save_to_db(data):
    client = MongoClient(URI_DB, server_api=ServerApi('1'))
    db = client.homework
    try:
        data = unquote_plus(data)
        parse_data = dict([i.split('=') for i in data.split('&')])
        db.messages.insert_one(parse_data)
    except Exception as e:
        logging.error(e)
    finally:
        client.close()

    db.posts.insert_one({'data': data})



def run_socket_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((SOCKET_HOST, SOCKET_PORT))
    try:
        while True:
            data, addr = s.recvfrom(CHUNK_SIZE)
            logging.info(f'Received from {addr}: {data.decode()}')
            save_to_db(data.decode())
    except Exception as e:
        logging.error(e)
    finally:
        logging.info('Server socket stopped')
        s.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(threadName)s - %(message)s")
    Thread(target=run_http_server, name="HTTP_server").start()
    Thread(target=run_socket_server, name="SOCKET_server").start()
