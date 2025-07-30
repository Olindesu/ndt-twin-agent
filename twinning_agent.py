import json
import time
import streamlit as st
import random
from pathlib import Path

NDT_FILE = "ndt_model.json"
SIMULATED_FILE = "ndt_model_simulated.json"

def load_ndt_model(path: str = NDT_FILE) -> dict | None:
    """Load NDT model from JSON file."""
    if not Path(path).exists():
        st.error("NDT model file not found!")
        return None
    try:
        with open(path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        st.error("Error decoding NDT model JSON!")
        return None

def save_ndt_model(model: dict, path: str = SIMULATED_FILE) -> None:
    """Save NDT model to JSON file."""
    with open(path, "w") as file:
        json.dump(model, file, indent=2)

def save_error_snapshot(component: dict) -> None:
    """Save snapshot of a component that just entered error state."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    comp_id = component.get("id", "unknown")
    snapshot_filename = f"snapshot_{timestamp}_{comp_id}.json"
    with open(snapshot_filename, "w") as f:
        json.dump(component, f, indent=2)

def check_and_set_error_state(component: dict) -> dict:
    metrics = component.get("metrics", {})
    comp_type = component.get("type", "")

    if comp_type == "CoreNetwork":
        if metrics.get("cpu_usage", 0) > 95.0 or metrics.get("auth_failures", 0) > 50:
            component["status"] = "error"

    elif comp_type == "BasebandUnit":
        if metrics.get("latency_ms", 0) > 50:
            component["status"] = "error"

    elif comp_type == "RadioUnit":
        if metrics.get("snr_db", 20) < 5 or metrics.get("rx_power_dbm", -50) < -90:
            component["status"] = "error"

    elif comp_type == "NetworkSwitch":
        if metrics.get("port_utilization_percent", 0) > 95.0 or metrics.get("packet_drops", 0) > 1000:
            component["status"] = "error"

    elif comp_type == "UserEquipment":
        if metrics.get("download_speed_mbps", 0) < 1 and metrics.get("upload_speed_mbps", 0) < 1:
            component["status"] = "error"

    elif comp_type == "MonitoringNode":
        if metrics.get("disk_usage_percent", 0) > 95.0:
            component["status"] = "error"

    elif comp_type == "AdversarialNode":
        if metrics.get("attack_type", "None") != "None" and metrics.get("attack_packets_sent", 0) > 5000:
            component["status"] = "error"

    return component

def simulate_and_update(component: dict) -> dict:
    """Simulate metrics for a component based on its type and current status."""
    component["last_updated"] = time.strftime("%H:%M:%S")
    metrics = component.get("metrics", {})
    comp_type = component.get("type", "")
    status = component.get("status", "")

    if status == "offline":
        if comp_type == "CoreNetwork":
            metrics["cpu_usage"] = 0.0
            metrics["sessions"] = 0
            metrics["auth_failures"] = 0
        elif comp_type == "BasebandUnit":
            # tx_packets, rx_packets stay constant
            metrics["latency_ms"] = 0
        elif comp_type == "RadioUnit":
            # snr_db, rx_power_dbm, tx_gain stay constant
            pass
        elif comp_type == "NetworkSwitch":
            metrics["port_utilization_percent"] = 0.0
            # packet_drops stays constant
        elif comp_type == "UserEquipment":
            metrics["download_speed_mbps"] = 0.0
            metrics["upload_speed_mbps"] = 0.0
            # rsrp_dbm stays constant
        elif comp_type == "MonitoringNode":
            # captured_packets, disk_usage_percent stay constant
            pass
        elif comp_type == "AdversarialNode":
            metrics["attack_type"] = "None"
            # attack_packets_sent stays constant
        component["metrics"] = metrics
        return component

    if status == "idle":
        if comp_type == "CoreNetwork":
            metrics["cpu_usage"] = round(random.uniform(1, 5), 1)
            metrics["sessions"] = 0
            metrics["auth_failures"] = random.randint(0, 1)
        elif comp_type == "BasebandUnit":
            # tx_packets, rx_packets stay constant
            metrics["latency_ms"] = round(random.uniform(1, 5), 2)
        elif comp_type == "RadioUnit":
            metrics["snr_db"] = round(random.uniform(0, metrics.get("snr_db", 15)), 1)
            # rx_power_dbm, tx_gain stay constant
        elif comp_type == "NetworkSwitch":
            metrics["port_utilization_percent"] = round(random.uniform(0, 5), 1)
            # packet_drops stays constant
        elif comp_type == "UserEquipment":
            metrics["download_speed_mbps"] = 0.0
            metrics["upload_speed_mbps"] = 0.0
            # rsrp_dbm stays constant
        elif comp_type == "MonitoringNode":
            # captured_packets, disk_usage_percent stay constant
            pass
        elif comp_type == "AdversarialNode":
            metrics["attack_type"] = "None"
            # attack_packets_sent stays constant
        component["metrics"] = metrics
        return component

    # Simulate metrics based on component type (for online/error)
    if comp_type == "CoreNetwork":
        metrics["cpu_usage"] = round(random.uniform(10, 98), 1)
        metrics["sessions"] = max(0, metrics.get("sessions", 10) + random.randint(-2, 10))
        metrics["auth_failures"] = max(0, metrics.get("auth_failures", 0) + random.randint(0, 1))
    elif comp_type == "BasebandUnit":
        metrics["tx_packets"] = max(0, metrics.get("tx_packets", 0) + random.randint(100, 1000))
        metrics["rx_packets"] = max(0, metrics.get("rx_packets", 0) + random.randint(100, 1000))
        metrics["latency_ms"] = round(random.uniform(10, 60), 2)
    elif comp_type == "RadioUnit":
        metrics["snr_db"] = round(random.uniform(3, 30), 1)
        metrics["rx_power_dbm"] = round(random.uniform(-95, -40), 1)
        metrics["tx_gain"] = max(0, min(100, metrics.get("tx_gain", 70) + random.randint(-2, 2)))
    elif comp_type == "NetworkSwitch":
        metrics["port_utilization_percent"] = round(random.uniform(10, 98), 1)
        metrics["packet_drops"] = max(0, metrics.get("packet_drops", 0) + random.randint(0, 50))
    elif comp_type == "UserEquipment":
        metrics["download_speed_mbps"] = round(random.uniform(0, 100), 1)
        metrics["upload_speed_mbps"] = round(random.uniform(0, 20), 1)
        metrics["rsrp_dbm"] = round(random.uniform(-110, -80), 1)
    elif comp_type == "MonitoringNode":
        metrics["captured_packets"] = max(0, metrics.get("captured_packets", 0) + random.randint(1000, 10000))
        metrics["disk_usage_percent"] = round(random.uniform(10, 98), 1)
    elif comp_type == "AdversarialNode":
        attack_types = ["None", "DDoS", "MITM", "Spoofing"]
        # Randomize attack_type when online
        if status == "online":
            metrics["attack_type"] = random.choice(attack_types)
            if metrics["attack_type"] == "None":
                pass  # attack_packets_sent stays constant
            else:
                metrics["attack_packets_sent"] = max(
                    0, metrics.get("attack_packets_sent", 0) + random.randint(500, 2000)
                )

    component["metrics"] = metrics
    previous_status = component.get("status", "")
    component = check_and_set_error_state(component)
    if component.get("status") == "error" and previous_status != "error":
        save_error_snapshot(component)
    return component

def display_component(comp: dict) -> None:
    """Display a component's info in Streamlit."""
    st.markdown(f"### {comp.get('name', 'Unknown')} ({comp.get('type', 'N/A')})")
    cols = st.columns(3)
    cols[0].metric("Status", comp.get("status", "N/A"))
    cols[1].metric("Last Updated", comp.get("last_updated", "N/A"))
    cols[2].metric("Component ID", comp.get("id", "N/A"))
    st.json(comp.get("metrics", {}))

def main() -> None:
    st.set_page_config(page_title="5G Twinning Agent", layout="wide")
    st.title("📡 5G Testbed Twinning Agent")

    # Prefer loading the simulated file if it exists
    if Path(SIMULATED_FILE).exists():
        model = load_ndt_model(SIMULATED_FILE)
    else:
        model = load_ndt_model(NDT_FILE)
    if not model:
        return

    testbed = model.get("testbed", {})
    components = testbed.get("components", [])

    st.subheader(testbed.get("name", "Unknown Testbed"))
    st.caption(testbed.get("description", ""))

    # Allow user to set status for each component
    status_options = ["online", "offline", "idle", "error"]
    selected_status = {}
    for comp in components:
        comp_id = comp.get("id", "")
        default_status = comp.get("status", "online")
        selected_status[comp_id] = st.selectbox(
            f"Set status for {comp.get('name', comp_id)}",
            status_options,
            index=status_options.index(default_status) if default_status in status_options else 0,
            key=f"status_{comp_id}"
        )

    if st.button("Simulate & Refresh"):
        updated = False
        for i, comp in enumerate(components):
            # Use user-selected status
            comp["status"] = selected_status.get(comp.get("id", ""), "online")
            components[i] = simulate_and_update(comp)
            updated = True

        if updated:
            model["testbed"]["components"] = components
            save_ndt_model(model, SIMULATED_FILE)
            st.success("Changes written to ndt_model_simulated.json")
            st.rerun()

    for comp in components:
        display_component(comp)

if __name__ == "__main__":
    main()
