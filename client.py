import socket
import sys

#cria o socket UDP no cliente onde AF_INET é o endereço IPv4 e SOCK_DGRAM é o UDP
socketClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_name = socket.gethostbyname(socket.gethostname())
port = 7777
bufferSize = 1024

command = input("Digite um comando: ")


serverAddr = (server_name, port)
fileName = "client.txt"

sentCount = 0

while (sentCount < 6):

    socketClient.sendto(str(len(command)).encode(), serverAddr)

    socketClient.sendto(command.encode(), serverAddr)

    print("Enviado informações para o servidor.")

    socketClient.settimeout(10)
    try:
        ack, addr = socketClient.recvfrom(bufferSize)
    except socket.timeout:
        sentCount += 1
        continue
    else:
        if ack.decode() == "ACK":
            print("ACK recebido.")
            break
        else:
            sentCount += 1
            continue
            
if sentCount >= 6:
    print("Falha ao enviar comando. ")
    socketClient.close()
    sys.exit()

socketClient.settimeout(10)

data, addr = socketClient.recvfrom(bufferSize)
expectedLength = int(data.decode())
print("Tamanho esperado: ", expectedLength)

f = open(fileName, "w")
f.write("")
f.close()

currLength = 0

while currLength < expectedLength:

    socketClient.settimeout(10)
    
    try:
        packetFromServer, addr = socketClient.recvfrom(8)
    except socket.timeout:
        print("Falha ao receber a saída do comando do servidor")
        socketClient.close()
        sys.exit()
    else:
        print("Tamanho do pacote: ", len(packetFromServer), "recebido")
        print(packetFromServer)

        f = open(fileName, "a")
        f.write( packetFromServer.decode() )
        f.close()

        print("Enviando ACK")
        socketClient.sendto("ACK".encode(), addr)

        currLength += len(packetFromServer)

if not(currLength == expectedLength):
    print("Falha ao receber a saída do comando do servidor.")
    print("Espeado", expectedLength, "bytes. Recebido", currLength, "bytes")
    socketClient.close()
    sys.exit()

print("Arquivo", fileName, "salvo.")
socketClient.close()

