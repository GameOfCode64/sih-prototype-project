import click
import psutil
import requests
import json
import time
import os

# File to store firewall rules persistently
FIREWALL_RULES_FILE = 'firewall_rules.json'
# File to store traffic logs persistently
TRAFFIC_LOGS_FILE = 'traffic_logs.json'

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

# Monitor active network connections
@click.command()
def monitor_traffic():
    click.echo("Monitoring traffic... Press Ctrl+C to stop.")
    try:
        while True:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == psutil.CONN_ESTABLISHED:
                    traffic_entry = {
                        "pid": conn.pid if conn.pid is not None else "N/A",
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status
                    }
                    traffic_logs.append(traffic_entry)
                    click.echo(traffic_entry)
            save_traffic_logs()  # Save traffic logs to the file after each monitoring round
            time.sleep(5)
    except KeyboardInterrupt:
        click.echo("Stopped monitoring traffic.")
    except Exception as e:
        click.echo(f"An error occurred: {e}")

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

# CLI group to organize commands
@click.group()
def cli():
    pass

cli.add_command(add_rule)
cli.add_command(list_rules)
cli.add_command(monitor_traffic)
cli.add_command(send_logs)
cli.add_command(list_traffic_logs)

if __name__ == '__main__':
    cli()
