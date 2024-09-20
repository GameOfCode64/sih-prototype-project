import click
import psutil
import requests
import json
import time
import os
import openai

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

# Constants for rate limits
MAX_REQUESTS_PER_MINUTE = 20   # Replace with your actual RPM limit
MAX_TOKENS_PER_MINUTE = 1500   # Replace with your actual TPM limit

# Token and request counters
request_counter = 0
token_counter = 0

# Time tracking for rate limiting
last_reset_time = time.time()

# Function to send traffic data to ChatGPT for analysis
def analyze_traffic_with_chatgpt(traffic_data):
    global request_counter, token_counter, last_reset_time

    # Ensure we reset counters every minute
    current_time = time.time()
    if current_time - last_reset_time > 60:
        request_counter = 0
        token_counter = 0
        last_reset_time = current_time

    # Check if we've hit the request or token limit
    if request_counter >= MAX_REQUESTS_PER_MINUTE or token_counter >= MAX_TOKENS_PER_MINUTE:
        time_to_wait = 60 - (current_time - last_reset_time)
        click.echo(f"Rate limit reached. Waiting for {int(time_to_wait)} seconds...")
        time.sleep(time_to_wait)

        # Reset counters after waiting
        request_counter = 0
        token_counter = 0
        last_reset_time = time.time()

    # Prepare the prompt for traffic analysis
    prompt = f"Analyze the following network traffic data for any anomalies or security risks: {traffic_data}"

    # Estimate token usage (prompt tokens + response tokens)
    prompt_token_count = len(prompt.split())  # Rough token estimate based on word count
    response_token_count = 150                # Assuming max tokens for response
    total_tokens = prompt_token_count + response_token_count

    # Check token usage limit
    if token_counter + total_tokens > MAX_TOKENS_PER_MINUTE:
        click.echo("Token limit reached, waiting until the next minute...")
        time.sleep(60 - (time.time() - last_reset_time))  # Wait until next minute

        # Reset counters after waiting
        request_counter = 0
        token_counter = 0
        last_reset_time = time.time()

    # Call OpenAI API using gpt-3.5-turbo
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant analyzing network traffic for security risks."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    
    # Update counters
    request_counter += 1
    token_counter += total_tokens

    return response['choices'][0]['message']['content'].strip()

# Monitor active network connections with rate-limited GPT analysis
@click.command()
def monitor_traffic():
    traffic_batch = []
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
                    traffic_batch.append(traffic_entry)

                    # When batch size reaches 100, send to ChatGPT for analysis
                    if len(traffic_batch) >= 100:
                        analysis = analyze_traffic_with_chatgpt(traffic_batch)
                        click.echo(f"ChatGPT Analysis: {analysis}")
                        traffic_batch.clear()  # Clear the batch after processing

            time.sleep(5)
    except KeyboardInterrupt:
        click.echo("Stopped monitoring traffic.")

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
