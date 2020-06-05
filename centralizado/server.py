import threading,socket,time,os,argparse,random,select,sys
import Queue

lista_socket_inputs = []
lista_socket_outputs = []
lista_node = []

#servidor nao reconhece quando no esta ocupado corretamente (client print "all nodes are occupied" instead other node is going to access you)

class Node():
    def __init__(self, node_address, descriptor):
        self.node_address = node_address
        self.descriptor = descriptor
        self.free = False
        self.message_queue = Queue.Queue()

#----------------------------------------------------------------------
def find_index_node(descriptor):
    global lista_node
    for i in range(len(lista_socket_inputs)-1):
        if lista_node[i].descriptor == descriptor:
            return i

def find_free_node(descriptor):
    for i in range(len(lista_socket_inputs)-1):
        if lista_node[i].descriptor !=descriptor and lista_node[i].free:
            return i,True
    return -1,False

def broadcast(descriptor,message):
    global lista_node
    for node in lista_node:
        if node.descriptor!=descriptor:
            node.descriptor.sendall(message)

def arguments():
    parse = argparse.ArgumentParser(description="Centralized Algorithm")
    parse.add_argument('--address','-a',type=str,required=True,help="Server node Address")
    parse.add_argument('--port','-p',type=int,required=True,help="Server node port")
    arg_parse = parse.parse_args()
    main(arg_parse.address,arg_parse.port)


def main(address,port):
    global lista_node,lista_socket_inputs,lista_socket_outputs
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setblocking(0)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((address,port))
    server_sock.listen(socket.SOMAXCONN)
    lista_socket_inputs.append(server_sock)
    print "********************************"
    print "*Centralized Algorithm - Server*"
    print "********************************\n\n"

    while True:
        readable, writable, exceptional = select.select(lista_socket_inputs,lista_socket_outputs,lista_socket_inputs)
        for reader in readable:
            if reader is server_sock:
                client_sock,client_address = server_sock.accept()
                print "#New connection from ", client_address,"#"
                client_sock.setblocking(0)
                lista_socket_inputs.append(client_sock)
                lista_node.append(Node(client_address,client_sock))
            else:
                message = reader.recv(1024)
                if message:
                    lista_node[find_index_node(reader)].message_queue.put(message)
                    if not reader in lista_socket_outputs:
                        lista_socket_outputs.append(reader)
                else:
                    if reader in lista_socket_outputs:
                        lista_socket_outputs.remove(reader)
                    lista_socket_inputs.remove(reader)
                    del lista_node[find_index_node(reader)]
                    reader.close()
        for writer in writable:
            try:
                node_index=find_index_node(writer)
                message =lista_node[node_index].message_queue.get_nowait()
                print lista_node[node_index].node_address ,"\t",message
            except Queue.Empty:
                lista_socket_outputs.remove(writer)
            else:
                if message == "free":
                    lista_node[node_index].free = True
                elif message == "access":
                    if len(lista_node)==1:
                        writer.send("null")
                    else:
                        index_node_free,free = find_free_node(writer)
                        if not free:
                            writer.send("occupied")
                        else:
                            lista_node[node_index].descriptor.sendall("ok")
                            lista_node[index_node_free].descriptor.sendall("access")
                            lista_node[node_index].free = False
                            lista_node[index_node_free].free = False


arguments()

