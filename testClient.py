from src.client import Client
import time


if __name__ == '__main__':
    server_host = '192.168.31.146'#'127.0.0.1'#
    server_port = 7777
    save_folder = 'C:/Users/usr/Desktop/p2py/save'#'C:\\Users\\usr\\Desktop\\p2py' #'./save'

    client = Client()
    client.setHost(server_host, server_port)
    client.setFolder(save_folder)

    client.start()
    client.askHeader()
    time.sleep(1)
    print(f'connection: {client.showConnection()}')
    time.sleep(1)
    client.askFile()
    client.stop()
    print(f'connection: {client.showConnection()}')