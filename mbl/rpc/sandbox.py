
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
lemiCamel = LemiCamel(packetReceiver, packetSender, rpcServer.call)

lemiCamel.start()
packetSender.start()


class LemiRpcClient(object):
	def __init__(self, rpcContext, lemiCamel):
		self.__rpcClient = RpcClient(rpcContext)
		self.__lemiCamel = lemiCamel


	def call(self, method, args, timeout = Timeout.BLOCK):
		data = self.__rpcClient.prepare(method, args)
		response = self.__lemiCamel.call(data, timeout)
		return self.__rpcClient.evalute(response)


	def signal(self, method, args):
		data = self.__rpcClient.prepare(method, *args)
		self.__lemiCamel.signal(data)


class LemiRpcServer(object):
	def __init__(self, rpcContext):
		self.__rpcContext = rpcContext
		self.setThreadCount(1)


	def setThreadCount(self, threadCount):
		self.__threadCount = threadCount


	#def request(lemiCamel, tid, jsonData):
	#def signal(lemiCamel, tid, jsonData):

	def call(self, lemiCamel, tid, jsonData):
		# pockej na volne vlakno
		# zaloz do fronty pozadavek a pockej az vlakno vrati vysledek
		rpcServer = ThreadRpcServer()
		rpcServer.call(lemiCamel, tid, jsonData)

		#self.__lemiCamel.putResponse(data)




# toto je treba udelat jeste pred vybudovanim spojeni

kolik bude vyhrazeno vlaken pro obsluhu?


LemiRpcServer.registerMethod()
LemiRpcServer.registerInterface

# pdoporovat automatickou vymenu API ?
# mozna az o vrstvu dale

Command
Proxy

je to zavadejici?

