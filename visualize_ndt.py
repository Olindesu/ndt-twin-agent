import streamlit as st
import json

st.set_page_config(layout="wide")
st.title("📡 Digital Twin - 5G Fronthaul Testbed")

with open("ndt_model.json") as f:
    ndt = json.load(f)

st.subheader("🧠 Testbed Components")
for comp in ndt["testbed"]["components"]:
    with st.expander(f"{comp['name']} ({comp['type']})"):
        st.json(comp)
