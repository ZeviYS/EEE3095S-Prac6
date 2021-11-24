import socket
import os
import csv
import sys
import time
import threading
from flask import Flask
from flask import render_template, send_file
from flask import request

HOST = '0.0.0.0' # HOST = 192.168.0.161 # HOST = None  # Symbolic name meaning all available interfaces
PORT = 5003  # Arbitrary non-privileged port

# start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
client, address = server.accept()
#print for testing so I can see in logs
print("Connected to: ", address)

sensor_status = 'SensorOff'
status = False

app = Flask(__name__) # web page part
logData = [] # load log data

# this ended up not being simple lol, had to google so so much, no background in this

# don't allow sample - sensor is off
@app.route("/off")
def sensOFF():
    sensor_status = "SensorOff"
    client.send(sensor_status.encode())
    print("Sensor off")
    return sensor_status

# allow sample - sensor is on
@app.route("/on")
def sensON():
    sensor_status = "SensorOn"
    client.send(sensor_status.encode())
    print("Sensor on")
    return sensor_status

# receive status from client
@app.route("/status")
def clientStatus():
    global status

    sensor_status = "Status"
    client.send(sensor_status.encode())

    # do I need to set status to off here?
    print(status)
    return status

# for sys.exit
@app.route("/exit")
def exit():
    sensor_status = "Exit"
    client.send(sensor_status.encode())
    print("Exit request")
    return sensor_status

# logs from logData
@app.route("/log")
def log():
    global logData

    logs = "Time,LDR Value,Temparature Value,Temparature(C)<br>"
    for i in logData:
        split = i.split(",")
        logs = logs + split[0] + "," + split[1] + "," + split[2] + "," + split[3] + "<br>"

    print(logs)
    return logs

# this is not easy with no partner :(

# download the data
@app.route("/get-csv", methods=['GET','POST'])
def download_file():
    path="/sensorlog.csv"
    return send_file(path,as_attachment=True,mimetype="text/csv")

# need to start thread for web part
@app.route("/")
def main():
    thread = threading.Thread(target=receive_data) # receive method
    thread.start()
    return render_template('interface.html', title='Requests')

# when messages received from the client
def receive_data():

    global client, status, sensor_status, logData

    f = open("/sensorlog.csv", "w")
    f.write("Time,LDR Value,Temparature Value,Temparature(C)\n")
    f.close()

    with client:
        while True:
            data = client.recv(1024) # buffer size received
            data = data.decode("utf-8") # i think this is default, will check if i have time
            print("Data: ")
            print(data)

            # if status message
            #i've also returned an ACK in adc but i don't actually think it was necessary to
            if(data[0] == "S"): # Status
                sensor_status = data
                status = True # obvs because client is running and doing something, sensor is on
            else:
                if len(logData) == 10:
                    logData.pop(0)
                logData.append(data)

                f = open("/sensorlog.csv", "a")
                f.write(data + "\n")
                f.close() # flush accomplish same thing?
    quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)



## TEMPLATE CODE USED TO WORK OFF SLIGHTLY

# s = None
# f = open("/data/sensorlog.txt", "w+")
# for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
#                               socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
#     af, socktype, proto, canonname, sa = res
#     try:
#         s = socket.socket(af, socktype, proto)
#     except OSError as msg:
#         s = None
#         continue
#     try:
#         s.bind(sa)
#         s.listen(1)
#     except OSError as msg:
#         s.close()
#         s = None
#         continue
#     break

# if s is None:
#     print('could not open socket')
#     f.write("Could not open socket\n")
#     f.close()
#     sys.exit(1)

# conn, addr = s.accept()
# with conn:
#     print('Connected by', addr)
#     f.write("Connected by" + str(addr) + "\n")
#     f.flush()
#     while True:
#         data = conn.recv(1024)
#         print('Received', repr(data))
#         f.write("Received data\n")
#         f.flush()
#         time.sleep(1)
#         if not data: break

