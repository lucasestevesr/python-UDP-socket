import socket
import sys
import subprocess


def messagePackets(message, packetSize):
    packetList = []

    messageSize = len(message)  
    while messageSize > 0:
        beg = len(message) - messageSize
        end = beg + packetSize  
        packet = message[beg : end]
        packetList.append(packet)
        messageSize -= packetSize 
    
    return packetList

server_name = socket.gethostbyname(socket.gethostname())
port = 7777
bufferSize = 1024 

#cria o socket UDP no servidor onde AF_INET é o endereço IPv4 e SOCK_DGRAM é o UDP
socketServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketServer.bind(('', port))
print("UDP Server is running!")

fileName = "server.txt"

while True:
    socketServer.setblocking(True)
    cmdLength, addr = socketServer.recvfrom(bufferSize)
    socketServer.settimeout(5)
    try:
        cmdFromClient, addr = socketServer.recvfrom(bufferSize)
    except socket.timeout:
        print("Conexão com o cliente falhou.")
        continue
    else:
        if len(cmdFromClient) == int(cmdLength.decode()):
            print("Enviando ACK")
            socketServer.sendto("ACK".encode(), addr)
        else:
            print("Conexão com o cliente falhou.")
            continue
    
    cmdStr = cmdFromClient.decode()
    notStdOut = False
    cmdList = []

    if '>' in cmdStr:
        notStdOut = True
        cmdList = cmdStr.split('>')
        fileSpecified = cmdList[1][1:]  
    
 
    stdout = subprocess.check_output(cmdFromClient.decode(), shell=True)
    
    f = open(fileName, "w")

    if notStdOut == False:
        f.write(stdout.decode())
    else:
        fTemp = open(fileSpecified, "r")
        f.write(fTemp.read() )
        fTemp.close()

    f.close()
 
    f = open(fileName, "r")
    output = f.read().encode()
    f.close()

    socketServer.sendto(str(len(output)).encode(), addr)

    timesSent = 0

    packetList = messagePackets(output, 8)

    for packet in packetList:

        while timesSent < 4:

            socketServer.sendto(packet, addr)

            socketServer.settimeout(10)

            print("Enviado pacote de tam: ", len(packet) )
        
            try:
                ack, addr = socketServer.recvfrom(bufferSize)
            except socket.timeout:
                timesSent += 1
                continue
            else:
                if ack.decode() == "ACK":
                    print("ACK recebido.")
                    break
                else:
                    timesSent += 1
                    continue
        
        if timesSent >= 4:
            print("Não foi possível enviar o arquivo.")
            continue
