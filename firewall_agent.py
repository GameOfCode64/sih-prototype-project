import click
import psutil
import requests
import json
import time
import os
import openai
# import nmap

# File to store firewall rules persistently
FIREWALL_RULES_FILE = 'firewall_rules.json'
# File to store traffic logs persistently
TRAFFIC_LOGS_FILE = 'traffic_logs.json'

# OpenAI API key (replace with your own key)
openai.api_key = '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'

# Load existing firewall rules from the file
def load_firewall_rules():
    if os.path.exists(FIREWALL_RULES_FILE):
        with open(FIREWALL_RULES_FILE, 'r') as file:
            return json.load(file)
    return []

# Save the firewall rules to the file
def save_firewall_rules():
    with open(FIREWALL_RULES_FILE, 'w') as file:
        json.dump(firewall_rules, file, indent=4)

# Load existing traffic logs from the file
def load_traffic_logs():
    if os.path.exists(TRAFFIC_LOGS_FILE):
        with open(TRAFFIC_LOGS_FILE, 'r') as file:
            return json.load(file)
    return []

# Save the traffic logs to the file
def save_traffic_logs():
    with open(TRAFFIC_LOGS_FILE, 'w') as file:
        json.dump(traffic_logs, file, indent=4)

# Initialize firewall rules and traffic logs
firewall_rules = load_firewall_rules()
traffic_logs = load_traffic_logs()

# Function to send traffic data to ChatGPT for analysis
def analyze_traffic_with_chatgpt(traffic_data):
    prompt = f"Analyze the following network traffic data for any anomalies or security risks: {traffic_data}"
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    
    return response.choices[0].text.strip()

# Add a new firewall rule
@click.command()
@click.option('--app', prompt='App name', help='Name of the application.')
@click.option('--domain', prompt='Domain', help='Domain to restrict.')
@click.option('--ip', prompt='IP Address', help='IP address to restrict.')
@click.option('--protocol', prompt='Protocol', default='TCP', help='Protocol to restrict (default: TCP).')
def add_rule(app, domain, ip, protocol):
    rule = {
        "app_name": app,
        "domain": domain,
        "ip_address": ip,
        "protocol": protocol
    }
    firewall_rules.append(rule)
    save_firewall_rules()  # Save the rules to the file
    click.echo(f"Firewall rule added: {rule}")

# List all firewall rules
@click.command()
def list_rules():
    if firewall_rules:
        click.echo("Firewall Rules:")
        for rule in firewall_rules:
            click.echo(rule)
    else:
        click.echo("No firewall rules found.")

# Monitor active network connections with alert for unknown domains
@click.command()
def monitor_traffic():
    click.echo("Monitoring traffic... Press Ctrl+C to stop.")
    try:
        while True:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_ESTABLISHED:
                    traffic_entry = {
                        "pid": conn.pid,
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status
                    }
                    traffic_logs.append(traffic_entry)
                    click.echo(traffic_entry)

                    # Trigger alert for unknown domain
                    if traffic_entry['remote_address'] and "unknown.com" in traffic_entry['remote_address']:
                        click.echo("ALERT: Unknown domain detected!")

                    # Analyze with GPT
                    analysis = analyze_traffic_with_chatgpt(traffic_entry)
                    click.echo(f"ChatGPT Analysis: {analysis}")

            save_traffic_logs()  # Save traffic logs to the file after each monitoring round
            time.sleep(5)
    except KeyboardInterrupt:
        click.echo("Stopped monitoring traffic.")

# Send traffic logs to a backend server
@click.command()
@click.option('--backend_url', prompt='Backend URL', default='http://localhost:5000/logs', help='Backend server URL.')
def send_logs(backend_url):
    log_data = {
        "firewall_rules": firewall_rules,
        "traffic": traffic_logs
    }

    # Send logs to backend
    response = requests.post(backend_url, json=log_data)
    if response.status_code == 200:
        click.echo(f"Logs successfully sent to {backend_url}")
    else:
        click.echo(f"Failed to send logs. Status code: {response.status_code}")

# List all traffic logs
@click.command()
def list_traffic_logs():
    if traffic_logs:
        click.echo("Traffic Logs:")
        for log in traffic_logs:
            click.echo(log)
    else:
        click.echo("No traffic logs found.")

# Perform an Nmap port scan
# @click.command()
# @click.option('--target', prompt='Target IP/Domain', help='Target IP address or domain for port scanning.')
# def nmap_scan(target):
#     click.echo(f"Performing Nmap scan on {target}...")
#     nm = nmap.PortScanner()
#     nm.scan(target, '1-1024')  # Scan ports 1-1024
#     for host in nm.all_hosts():
#         click.echo(f"Host: {host}")
#         for proto in nm[host].all_protocols():
#             ports = nm[host][proto].keys()
#             for port in ports:
#                 click.echo(f"Port: {port}, State: {nm[host][proto][port]['state']}")

# CLI group to organize commands
@click.group()
def cli():
    pass

cli.add_command(add_rule)
cli.add_command(list_rules)
cli.add_command(monitor_traffic)
cli.add_command(send_logs)
cli.add_command(list_traffic_logs)
# cli.add_command(nmap_scan)

if __name__ == '__main__':
    cli()
