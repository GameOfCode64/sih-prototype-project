from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Endpoint to receive logs
@app.route('/logs', methods=['POST'])
def receive_logs():
    log_data = request.json
    print("Received log data:")
    print(json.dumps(log_data, indent=4))

    # Basic alert system based on conditions (e.g., detecting abnormal traffic)
    if len(log_data["traffic"]) > 10:
        return jsonify({"status": "alert", "message": "High number of connections detected"}), 200

    return jsonify({"status": "ok", "message": "Logs received successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
