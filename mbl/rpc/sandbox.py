
class LemiClient(object):
	def __init__(self, address):
		pass

	# tady de nastavit uplne vsechno kolem LEMI naraz


	def connect(self):
		pass

tcpClient = TcpClient(address)
socket = tcpClient.connect()
inputStream = socket.inputStream()
outputStream = socket.outputStream()

packetReceiver = PacketReceiver(inputStream)
packetSender = PacketSender(outputStream)
transactionTable = TransactionTable()
lemiCamel = LemiCamel(packetReceiver, packetSender, transactionTable)

lemiCamel.start()
packetSender.start()


class LemiRpcClient(object):
	def __init__(self, lemiCamel, rpcContext):
		self.__rpcClient = RpcClient(rpcContext, callback)
		self.__lemiCamel = lemiCamel


	def callback(self, jsonData):
		tid = self.__lemiCamel.sendRequest(jsonData, timeout)
		response = getResponse(self, tid, timeout)
		return response


	def call(self, method, args, timeout):
		pass


class LemiProxy(object):
	def __init__(self, rpcClient):
		self.__rpcClient = rpcClient
		self.__createInterface()


	def __createInterface(self):
		for method in self.__rpcClient.call('~~getInterface~~'):
			methodName = method['name']
			self.__createMethod(methodName)


	def __createMethod(self, methodName):
		pass








lemiCamel - obal pro RPC

LemiRpcClient.call(method, args, timeout = Timeout.BLOCK)
LemiRpcClient.signal(method, args)

createProxy()
call('~~getInterface~~')

# toto je treba udelat jeste pred vybudovanim spojeni

kolik bude vyhrazeno vlaken pro obsluhu?

nemuzem sem primo narvat JsonRpcServer?

LemiRpcServer.registerMethod()
LemiRpcServer.registerInterface

# pdoporovat automatickou vymenu API ?
# mozna az o vrstvu dale

Command
Proxy

je to zavadejici?