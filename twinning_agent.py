import json
import time
import streamlit as st
import random
from pathlib import Path

NDT_FILE = "ndt_model.json"

# Load NDT model
def load_ndt_model(path=NDT_FILE):
    if not Path(path).exists():
        st.error("NDT model file not found!")
        return None
    with open(path, "r") as file:
        return json.load(file)

# Save updated model back to JSON
SIMULATED_FILE="ndt_model_simulated.json"

def save_ndt_model(model, path=SIMULATED_FILE):
    with open(path, "w") as file:
        json.dump(model, file, indent=2)

# Simulate status and update metrics
def simulate_and_update(component):
    status_options = ["online", "offline", "idle", "error"]
    component["status"] = random.choice(status_options)
    component["last_updated"] = time.strftime("%H:%M:%S")

    metrics = component.get("metrics", {})
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            fluctuation = value * 0.1
            metrics[key] = round(value + random.uniform(-fluctuation, fluctuation), 2)

    component["metrics"] = metrics
    return component

# Display UI
def display_component(comp):
    st.markdown(f"### {comp['name']} ({comp['type']})")
    cols = st.columns(3)
    cols[0].metric("Status", comp["status"])
    cols[1].metric("Last Updated", comp.get("last_updated", "N/A"))
    cols[2].metric("Component ID", comp["id"])
    st.json(comp["metrics"])

# Main app
def main():
    st.set_page_config(page_title="5G Twinning Agent", layout="wide")
    st.title("📡 5G Testbed Twinning Agent")

    model = load_ndt_model()
    if not model:
        return

    testbed = model.get("testbed", {})
    components = testbed.get("components", [])

    st.subheader(testbed.get("name", "Unknown Testbed"))
    st.caption(testbed.get("description", ""))

    updated = False
    for i, comp in enumerate(components):
        components[i] = simulate_and_update(comp)
        display_component(components[i])
        updated = True

    if updated:
        model["testbed"]["components"] = components
        save_ndt_model(model)

    st.success("Changes written to ndt_model_simulated.json")
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main()
