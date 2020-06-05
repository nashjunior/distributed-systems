import argparse,time,socket,threading,sys

lista_node=["10.0.0.1", "10.0.0.2","10.0.0.3","10.0.0.4","10.0.0.5"]
node_connections=[]
default_port = 7000
tamanho_lista=len(lista_node)
node_accepted = False
has_token = False

def find_node(address):
	global lista_node,tamanho_lista
	for i in range(tamanho_lista):
		if lista_node[i]== address:
			return i,True
	return -1,False

def arguments():
	global default_port,lista_node,tamanho_lista,node_connections
	parser = argparse.ArgumentParser(prog="Token ring",usage='%(prog)s [options]')
	parser.add_argument('--addr','-a',type=str,required=True,help='node address')
	args =parser.parse_args()
	index_node,node_found=find_node(args.addr)
	if not node_found:
		print ("Node not found in node list")
		sys.exit()

	if index_node==tamanho_lista-1:
		node_connections.append(lista_node[0])
	else:
		node_connections.append(lista_node[index_node+1])

	if index_node==0:
		node_connections.append(lista_node[tamanho_lista-1])
	else:
		node_connections.append(lista_node[index_node-1])


	thread2=threading.Thread(target=handle_accept,args=(index_node,))
	thread1=threading.Thread(target=handle_connect,args=(index_node,))
	#thread1.setDaemon(True)
	thread2.start()
	time.sleep(1)
	thread1.start()


def handle_connect(index_node):

	global default_port,node_connections,node_accepted
	socket_connect = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	socket_connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	if index_node==0:
		connection = (node_connections[0],default_port)
		socket_connect.connect(connection)
		thread=threading.Thread(target=handle_connect,args=(index_node,))
		thread.setDaemon(True)
		thread.start()
		while not has_token:
			pass
	else:
		while not node_accepted:
			continue
		socket_connect.connect((node_connections[0],default_port))

def handle_accept(index_node):
	global default_port,node_accepted,has_token,node_connections
	sock_id=None
	socket_accept = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	socket_accept.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	socket_accept.bind((lista_node[index_node],default_port))
	socket_accept.listen(2)
	while True:
		sock_id,client_address = socket_accept.accept()
		if client_address == node_connections[1]:
			node_accepted = False
			break
			sock_id.close()

		if index_node ==0:
			has_token = True
			print ("ok")

		print (sock_id.recv(1024))






arguments()