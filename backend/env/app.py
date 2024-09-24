from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from scapy.all import sniff
import os
import logging

logging.basicConfig(filename='firewall_log.txt', level=logging.INFO)

# Flask app setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") 

BLOCKED_IPS = ['']


def block_ip(ip):
    command = f'netsh advfirewall firewall add rule name="Block {ip}" dir=in action=block remoteip={ip}'
    os.system(command)
    logging.info(f"Blocked IP: {ip}")
    socketio.emit('log', {'message': f"Blocked IP: {ip}"})  


def packet_handler(packet):
    if packet.haslayer('IP'):
        src_ip = packet['IP'].src
        dst_ip = packet['IP'].dst
        if src_ip in BLOCKED_IPS:
            logging.info(f"Blocked packet from {src_ip} to {dst_ip}")
            block_ip(src_ip)
            return
        logging.info(f"Allowed packet: {src_ip} -> {dst_ip}")
        socketio.emit('log', {'message': f"Allowed packet: {src_ip} -> {dst_ip}"})  # Send to frontend

@app.route('/')
def index():
    return "Packet Sniffer is Running!"
def start_packet_sniffing():
    interface_name = 'Wi-Fi' 
    print(f"\nStarting packet capture on interface: {interface_name}")
    sniff(iface=interface_name, filter='ip', prn=packet_handler)


if __name__ == "__main__":
    from threading import Thread
    sniff_thread = Thread(target=start_packet_sniffing)
    sniff_thread.start()
    socketio.run(app, host='0.0.0.0', port=5000)
