from mbl.net import TcpClient
#from mbl.io import LineReader, LineWriter
from mbl.io import LineInputStream, LineOutputStream
from mbl.io import CachedInputStream

# buffer na vstup
# buffer na vsytup mozna
# readline + writeline
# sdruzit to pod IOStream

bufferSize = 2 ** 14
address = ('192.168.4.101', 80)
client = TcpClient(address)
client.setConnectTimeout(2)
socket = client.connect()

reader = socket.inputStream()
reader = CachedInputStream(reader)
reader = LineInputStream(reader)

writer = LineOutputStream(socket.outputStream())
writer.setEol('\r\n')

writer.writeLine('GET / HTTP/1.0')
writer.newLine()

while True:
	line = reader.readLine()
	if not line:
		break
	print repr(line)

socket.close()



