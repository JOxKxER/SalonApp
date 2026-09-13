import streamlit as st
import json
import os
import shutil
from datetime import datetime

DB_FILE = "client_records.json"
PRESETS_FILE = "preset_formulas.json"
UPLOAD_DIR = "client_photos"

# Ensure photo directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="Karlie's Salon Manager", page_icon="✂️", layout="centered")

# Prominent Menu Helper Banner for Mobile Users
st.markdown("""
<div style="background-color: #ff4b4b; color: white; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 15px; font-weight: bold;">
    📱 Tap the <b>[ >> ] Menu Arrow</b> at the very top-left above to switch between New Formula, Search History, and Presets!
</div>
""", unsafe_allow_html=True)

st.title("✂️ Karlie's Salon Manager")
st.subheader("Client Color Passports & Formulation Engine")

menu = st.sidebar.selectbox("Navigation", ["Search History", "New Formula", "Preset Formulas", "Edit Record", "Take-Home Label", "Database Backup", "User Guide"])

records = load_json(DB_FILE, [])
presets = load_json(PRESETS_FILE, [
    {"name": "Standard Vivid Refresh (100g)", "base": 82.0, "tone": "Magenta", "pigment": 18.0},
    {"name": "Platinum Toner Mask (100g)", "base": 90.0, "tone": "Cool Violet", "pigment": 10.0},
    {"name": "Deep Emerald Gloss (100g)", "base": 80.0, "tone": "Emerald Green", "pigment": 20.0}
])

if menu == "Search History":
    st.header("Search Client Records")
    query = st.text_input("Enter client name:").strip().lower()
    if query:
        matches = [r for r in records if query in r['client_name'].lower()]
        if matches:
            st.success(f"Found {len(matches)} record(s):")
            for idx, r in enumerate(matches):
                st.markdown(f"**Client:** {r['client_name']} | **Date:** {r['date']}")
                st.text(f"Baseline Level: {r['base_level']} | Target Shade: {r['target_tone']}")
                st.json(r['formula'])
                
                base_grams = r['formula'].get("Neutral Base (Grams)", 0)
                pigment_key = next((k for k in r['formula'] if "Direct Pigment" in k), "")
                pigment_grams = r['formula'].get(pigment_key, 0)
                est_cost = (base_grams * 0.05) + (pigment_grams * 0.18)
                st.caption(f"Estimated Product Cost: ${est_cost:.2f} ($0.05/g base, $0.18/g pigment)")

                if "photo_path" in r and r["photo_path"] and os.path.exists(r["photo_path"]):
                    st.image(r["photo_path"], caption=f"Calibration Ref - {r['client_name']}", width=300)
                
                if st.button(f"Repeat Last Formula for {r['client_name']}", key=f"repeat_{idx}"):
                    repeat_record = {
                        "client_name": f"{r['client_name']} (Repeat Visit)",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "base_level": r['base_level'],
                        "target_tone": r['target_tone'],
                        "formula": r['formula'],
                        "photo_path": r.get("photo_path", "")
                    }
                    records.append(repeat_record)
                    save_json(DB_FILE, records)
                    st.success(f"Successfully duplicated last formula as a new session for {r['client_name']}!")
                    st.rerun()

                st.markdown("---")
        else:
            st.warning("No matching records found.")

elif menu == "New Formula":
    st.header("New Formula Workflow")
    with st.form("formula_form"):
        client_name = st.text_input("Client Name")
        base_level = st.slider("Baseline Hair Level", 1, 10, 5)
        target_tone = st.text_input("Target Vivid Tone (e.g., Magenta, Electric Blue)")
        hair_grams = st.number_input("Total Product Quantity Needed (Grams)", min_value=1.0, value=100.0)
        
        uploaded_file = st.file_uploader("Upload Hair Photo (with Color Calibration Card)", type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("Calculate & Save Formula")
        if submitted and client_name:
            multiplier = 0.8 if base_level > 7 else 1.2
            direct_pigment = round(hair_grams * 0.15 * multiplier, 2)
            base_cond = round(hair_grams - direct_pigment, 2)
            
            formula = {
                "Neutral Base (Grams)": base_cond,
                f"Direct Pigment ({target_tone}) (Grams)": direct_pigment
            }
            
            photo_path = ""
            if uploaded_file is not None:
                safe_name = client_name.replace(" ", "_").lower()
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                photo_filename = f"{safe_name}_{timestamp_str}.jpg"
                photo_path = os.path.join(UPLOAD_DIR, photo_filename)
                with open(photo_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            new_record = {
                "client_name": client_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "base_level": base_level,
                "target_tone": target_tone,
                "formula": formula,
                "photo_path": photo_path
            }
            records.append(new_record)
            save_json(DB_FILE, records)
            st.success(f"Successfully saved passport record for {client_name}!")
            st.json(formula)
            if photo_path:
                st.image(photo_path, caption="Saved Calibration Reference Photo", width=300)

elif menu == "Preset Formulas":
    st.header("Preset Formulas & Quick Masks")
    st.markdown("Select a pre-calculated mix for quick dispensing or save a new reusable recipe.")
    
    if presets:
        selected_preset_name = st.selectbox("Choose Preset", options=[p["name"] for p in presets])
        selected_p = next(p for p in presets if p["name"] == selected_preset_name)
        
        st.info(f"**Recipe:** {selected_p['name']}")
        preset_formula = {
            "Neutral Base (Grams)": selected_p["base"],
            f"Direct Pigment ({selected_p['tone']}) (Grams)": selected_p["pigment"]
        }
        st.json(preset_formula)
        
        quick_client = st.text_input("Assign Preset to Client Name:")
        if st.button("Save Preset to Client Passport"):
            if quick_client:
                new_record = {
                    "client_name": quick_client,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "base_level": 5,
                    "target_tone": selected_p["tone"],
                    "formula": preset_formula,
                    "photo_path": ""
                }
                records.append(new_record)
                save_json(DB_FILE, records)
                st.success(f"Saved preset formula to {quick_client}'s passport!")
            else:
                st.warning("Please enter a client name.")

    st.markdown("---")
    st.subheader("Create New Preset Recipe")
    with st.form("preset_form"):
        p_name = st.text_input("Preset Name (e.g., Pastel Peach Mask)")
        p_tone = st.text_input("Shade / Tone Name")
        p_base = st.number_input("Neutral Base Grams", value=80.0)
        p_pigment = st.number_input("Direct Pigment Grams", value=20.0)
        add_preset_btn = st.form_submit_button("Save New Preset")
        if add_preset_btn and p_name:
            new_p = {"name": p_name, "base": p_base, "tone": p_tone, "pigment": p_pigment}
            presets.append(new_p)
            save_json(PRESETS_FILE, presets)
            st.success(f"Successfully added preset '{p_name}'!")
            st.rerun()

elif menu == "Edit Record":
    st.header("Edit Existing Client Record")
    query = st.text_input("Enter client name to edit:").strip().lower()
    if query:
        matches = [(i, r) for i, r in enumerate(records) if query in r['client_name'].lower()]
        if matches:
            selected_idx = st.selectbox("Select Record", options=[i for i, r in matches], format_func=lambda i: f"{records[i]['client_name']} - {records[i]['date']}")
            if selected_idx is not None:
                r = records[selected_idx]
                with st.form("edit_form"):
                    new_level = st.slider("New Baseline Level", 1, 10, r['base_level'])
                    new_tone = st.text_input("New Target Tone", value=r['target_tone'])
                    update_btn = st.form_submit_button("Save Updates")
                    if update_btn:
                        records[selected_idx]['base_level'] = new_level
                        records[selected_idx]['target_tone'] = new_tone
                        records[selected_idx]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M (Updated)")
                        save_json(DB_FILE, records)
                        st.success("Record successfully updated!")
        else:
            st.warning("No clients found.")

elif menu == "Take-Home Label":
    st.header("Take-Home Mask Label Generator")
    query = st.text_input("Enter client name for label:").strip().lower()
    if query:
        matches = [r for r in records if query in r['client_name'].lower()]
        if matches:
            r = matches[-1]
            label_html = f"""
            <div style="border: 2px solid #000; padding: 15px; border-radius: 8px; font-family: monospace; background-color: #f9f9f9; color: #000;">
                <h3 style="text-align: center; margin: 0;">KARLIE'S SALON</h3>
                <p style="text-align: center; margin: 0;">TAKE-HOME MASK</p>
                <hr>
                <b>Client:</b> {r['client_name']}<br>
                <b>Date Blended:</b> {r['date']}<br>
                <b>Target Shade:</b> {r['target_tone']}<br>
                <hr>
                <b>CUSTOM FORMULA:</b><br>
                {''.join([f'&nbsp;&nbsp;• {k}: {v}g<br>' for k, v in r['formula'].items()])}
                <hr>
                <small><b>Usage:</b> Apply weekly on damp hair. Leave on for 10 minutes, then rinse cool.</small>
            </div>
            """
            st.markdown(label_html, unsafe_allow_html=True)
            
            label_text = f"KARLIE'S SALON - TAKE-HOME MASK\nClient: {r['client_name']}\nDate: {r['date']}\nTarget: {r['target_tone']}\n"
            for k, v in r['formula'].items():
                label_text += f"{k}: {v}g\n"
            st.download_button("Download Label Text File", label_text, file_name=f"{r['client_name'].replace(' ', '_').lower()}_label.txt")
        else:
            st.warning("Client not found.")

elif menu == "Database Backup":
    st.header("Database Backup Utility")
    if st.button("Create Backup Now"):
        if os.path.exists(DB_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"client_records_backup_{timestamp}.json"
            shutil.copy(DB_FILE, backup_filename)
            st.success(f"Database successfully backed up as '{backup_filename}'.")
        else:
            st.error("No database file found.")

elif menu == "User Guide":
    st.header("📖 Salon App User Guide & Visual Color Reference")
    st.markdown("""
    Welcome to Karlie's Salon Manager! Use this reference guide for navigating the app, evaluating hair levels, and viewing visual tone swatches:

    * **1. Baseline Hair Levels (Scale 1–10)**
    """)
    
    cols = st.columns(5)
    levels_data = [
        ("L1-2 (Dark)", "#1a1110"),
        ("L3-4 (Med-Dark)", "#3b2f2f"),
        ("L5-6 (Light Brn)", "#6e503b"),
        ("L7-8 (Med Blonde)", "#b8976b"),
        ("L9-10 (Platinum)", "#e6dfcc")
    ]
    for col, (label, hex_code) in zip(cols, levels_data):
        with col:
            st.markdown(f'<div style="background-color: {hex_code}; height: 35px; border-radius: 4px; border: 1px solid #ccc;"></div>', unsafe_allow_html=True)
            st.caption(label)

    st.markdown("""
    * **2. Target Vivid Tone Examples**
    """)
    
    vivid_cols = st.columns(4)
    vivid_data = [
        ("Magenta", "#d90429"),
        ("Electric Blue", "#0077b6"),
        ("Emerald Green", "#2b9348"),
        ("Vibrant Violet", "#7209b7")
    ]
    for col, (label, hex_code) in zip(vivid_cols, vivid_data):
        with col:
            st.markdown(f'<div style="background-color: {hex_code}; height: 35px; border-radius: 4px; border: 1px solid #ccc;"></div>', unsafe_allow_html=True)
            st.caption(label)

    st.markdown("""
    * **3. One-Tap Re-Orders & Cost Estimator**
      * Use the **Search History** view to instantly repeat a returning client's previous formula with one tap, or view real-time product cost breakdowns based on gram weight.

    * **4. What is a Color Calibration Card?**
      * **Definition:** A physical reference card featuring standard neutral blocks (such as 18% neutral gray, pure white, and absolute black) and optional standard color patches.
      * **Purpose:** Indoor salon lighting creates color casts that trick phone cameras into distorting true hair shades. 
      * **How to Use:** Hold or place the physical card right next to the client's hair strand when taking the photo for accurate white balance.
    """)