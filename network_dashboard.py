import psutil
import scapy.all as scapy
import dash
from dash import dcc, html
import plotly.graph_objs as go
import threading
import time

# Store data
network_data = []

# Capture network packets (replace "wlp2s0" with your actual interface)
def capture_packets():
    def process_packet(packet):
        if packet.haslayer(scapy.IP):
            src = packet[scapy.IP].src
            dst = packet[scapy.IP].dst
            size = len(packet)
            timestamp = time.time()
            network_data.append({"src": src, "dst": dst, "size": size, "time": timestamp})  # Fixed line
    scapy.sniff(iface="wlp2s0", prn=process_packet, store=False)

# Monitor system performance
def get_system_metrics():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "net_sent": psutil.net_io_counters().bytes_sent,
        "net_recv": psutil.net_io_counters().bytes_recv,
    }

# Start packet capture in a separate thread
threading.Thread(target=capture_packets, daemon=True).start()

# Dash web dashboard
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Network Monitoring Dashboard"),
    dcc.Graph(id="network-graph"),
    dcc.Interval(id="interval-update", interval=2000, n_intervals=0)
])

@app.callback(
    dash.Output("network-graph", "figure"),
    [dash.Input("interval-update", "n_intervals")]
)
def update_graph(n):
    metrics = get_system_metrics()
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics["cpu"],
        title={"text": "CPU Usage (%)"},
        gauge={"axis": {"range": [0, 100]}}
    ))

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics["ram"],
        title={"text": "RAM Usage (%)"},
        gauge={"axis": {"range": [0, 100]}}
    ))

    return fig

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8000)

