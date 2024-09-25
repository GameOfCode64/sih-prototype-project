from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from scapy.all import sniff, Packet
import threading

app = Flask(__name__)
CORS(app, resources={r"/socket.io/*": {"origins": "*"}})
socketio = SocketIO(app)

# Function to handle packets
def packet_handler(packet):
    # Extract relevant packet information
    packet_info = {
        "version": packet.version if hasattr(packet, "version") else "N/A",
        "ihl": packet.ihl if hasattr(packet, "ihl") else "N/A",
        "tos": packet.tos if hasattr(packet, "tos") else "N/A",
        "total_length": len(packet),
        "identification": packet.id if hasattr(packet, "id") else "N/A",
        "flags": packet.flags if hasattr(packet, "flags") else "N/A",
        "ttl": packet.ttl if hasattr(packet, "ttl") else "N/A",
        "protocol": packet.proto if hasattr(packet, "proto") else "N/A",
        "header_checksum": packet.chksum if hasattr(packet, "chksum") else "N/A",
        "src_ip": packet[1].src if packet.haslayer(1) else "N/A",
        "dst_ip": packet[1].dst if packet.haslayer(1) else "N/A",
        "options": packet.options if hasattr(packet, "options") else None,
        "payload": str(packet.payload) if hasattr(packet, "payload") else "N/A"
    }

    # Emit the log to the frontend
    socketio.emit("log", {"message": packet_info})

# Function to start sniffing in a separate thread
def start_sniffing():
   sniff(iface='Wi-Fi', filter='ip', prn=packet_handler)
 # Change 'Ethernet' to your network interface name

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Network Logger!"})

if __name__ == "__main__":
    # Start the packet sniffing in a separate thread
    thread = threading.Thread(target=start_sniffing)
    thread.start()
    
    # Run the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
