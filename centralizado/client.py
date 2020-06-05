import socket,argparse,sys,random,time,threading

lock_send = threading.Lock()
lock_recieve = threading.lock()

def node_management_recieve(client_sock):
    global lock
    while True:
        while lock.locked():
            pass
        else:
            with lock:
                try:
                    client_sock.settimeout(4)
                    message=client_sock.recv(1024)
                    if message:
                        if message == "access":
                            time.sleep(2)
                            client_sock.send("free")
                    else:
                        client_sock.close()
                        print ("Servidor saiu")
                except socket.timeout:
                    client_sock.settimeout(None)



def node_management_send(client_sock):
    if lock.locked():
        print "Other node acessing you and processing some data.Try again later"
        threading.Timer(random.randint(2,5),node_management_send,[client_sock]).start()
    else:
        with lock:
            client_sock.send("access")
            print "Trying acessing some node"
            message = client_sock.recv(1024)
            if message:
                if message == "occupied":
                    print "All other nodes are occupied... Please try again later"
                    threading.Timer(random.randint(2,5),node_management_send,[client_sock]).start()
                elif message=="ok":
                    print "Gotta connection with some node and processing the data"
                    #como fazer pra dormir
                    time.sleep(2)
                elif message=="null":
                    print "There is no other node to process data... Wait for some time"
                    threading.Timer(random.randint(2,5),node_management_send,[client_sock]).start()
            else:
                print "Server went shutdown"
                sys.exit()

def arguments():
    parse = argparse.ArgumentParser(description="Centralized Algorithm")
    parse.add_argument('--server','-s',type=str,required=True,help="Server node Address")
    parse.add_argument('--port','-p',type=int,required=True,help="Server node port")
    arg_parse = parse.parse_args()
    execucao(arg_parse.server,arg_parse.port)

def execucao(server_address,server_port):
    print "********************************"
    print "*Centralized Algorithm - Client*"
    print "********************************\n\n"
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_sock.connect((server_address,server_port))
    client_sock.send("free")
    threading.Timer(random.randint(0,5),node_management_send,[client_sock]).start()#verificar se vai querer acessar recurso
    node_management_recieve(client_sock)

arguments()