import streamlit as st
import json
import os
import shutil
from datetime import datetime

DB_FILE = "client_records.json"
UPLOAD_DIR = "client_photos"

# Ensure photo directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="Karlie's Salon Manager", page_icon="✂️", layout="centered")

st.title("✂️ Karlie's Salon Manager")
st.subheader("Client Color Passports & Formulation Engine")

menu = st.sidebar.selectbox("Navigation", ["Search History", "New Formula", "Edit Record", "Take-Home Label", "Database Backup", "User Guide"])

records = load_data()

if menu == "Search History":
    st.header("Search Client Records")
    query = st.text_input("Enter client name:").strip().lower()
    if query:
        matches = [r for r in records if query in r['client_name'].lower()]
        if matches:
            st.success(f"Found {len(matches)} record(s):")
            for r in matches:
                st.markdown(f"**Client:** {r['client_name']} | **Date:** {r['date']}")
                st.text(f"Baseline Level: {r['base_level']} | Target Shade: {r['target_tone']}")
                st.json(r['formula'])
                if "photo_path" in r and r["photo_path"] and os.path.exists(r["photo_path"]):
                    st.image(r["photo_path"], caption=f"Calibration Ref - {r['client_name']}", width=300)
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
        
        # Calibration card photo upload slot
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
            save_data(records)
            st.success(f"Successfully saved passport record for {client_name}!")
            st.json(formula)
            if photo_path:
                st.image(photo_path, caption="Saved Calibration Reference Photo", width=300)

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
                        save_data(records)
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
    st.header("📖 Salon App User Guide & Formulation Reference")
    st.markdown("""
    Welcome to Karlie's Salon Manager! This guide details both app navigation and how to accurately evaluate hair metrics during client consultations:

    * **1. Determining Baseline Hair Level (Scale 1–10)**
      * **1–2:** Black to Darkest Brown
      * **3–4:** Dark Brown to Medium Brown
      * **5–6:** Light Brown to Dark Blonde
      * **7–8:** Medium Blonde to Light Blonde
      * **9–10:** Very Light Blonde to Platinum / Pale Yellow
      * *Tip:* Compare the mid-lengths of the client's hair directly against your physical color ring under neutral light.

    * **2. Setting Target Tone**
      * Enter the exact descriptive vivid shade requested (e.g., *Magenta*, *Electric Blue*, *Emerald Green*, *Vibrant Violet*).
      * This dynamically labels the custom pigment breakdown in grams for easy mixing.

    * **3. Calculating Total Product Quantity (Grams)**
      * **Short / Touch-Up:** ~50g to 75g
      * **Medium / Shoulder-Length:** ~100g
      * **Long / Thick Hair:** ~150g to 200g+

    * **4. Taking Calibration Photos**
      * Place the physical gray balance/color card right beside the hair strand before snapping the photo via the upload slot to lock in true color representation.
    """)