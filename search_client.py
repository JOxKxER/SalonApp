import json
import shutil
import os
from datetime import datetime

DB_FILE = "client_records.json"

def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def search_and_manage():
    while True:
        print("\n=== Karlie's Salon Manager ===")
        print("1. Search Client History")
        print("2. Add New Formula Workflow")
        print("3. Edit Existing Client Record")
        print("4. Print & Export Take-Home Mask Label")
        print("5. Backup Client Database")
        print("6. Exit")
        
        choice = input("Select an option (1-6): ").strip()
        
        if choice == "1":
            name_query = input("Enter client name to search: ").strip().lower()
            records = load_data()
            matches = [r for r in records if name_query in r['client_name'].lower()]
            if matches:
                print(f"\nFound {len(matches)} record(s) for '{name_query}':")
                for idx, r in enumerate(matches):
                    print(f"[{idx}] Date: {r['date']} | Level: {r['base_level']} | Target: {r['target_tone']}")
                    for k, v in r['formula'].items():
                        print(f"   - {k}: {v}g")
            else:
                print("No records found matching that name.")
                
        elif choice == "2":
            client_name = input("Enter client name: ")
            base_level = int(input("Enter baseline hair level (1-10): "))
            target_tone = input("Enter target vivid tone: ")
            hair_grams = float(input("Enter total product quantity needed (grams): "))
            
            multiplier = 0.8 if base_level > 7 else 1.2
            direct_pigment = round(hair_grams * 0.15 * multiplier, 2)
            base_cond = round(hair_grams - direct_pigment, 2)
            
            formula = {
                "Neutral Base (Grams)": base_cond,
                f"Direct Pigment ({target_tone}) (Grams)": direct_pigment
            }
            
            records = load_data()
            records.append({
                "client_name": client_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "base_level": base_level,
                "target_tone": target_tone,
                "formula": formula
            })
            save_data(records)
            print(f"Successfully saved passport record for {client_name}.")
            
        elif choice == "3":
            name_query = input("Enter client name to edit: ").strip().lower()
            records = load_data()
            matches = [(i, r) for i, r in enumerate(records) if name_query in r['client_name'].lower()]
            
            if matches:
                print(f"\nFound {len(matches)} record(s):")
                for display_idx, (orig_idx, r) in enumerate(matches):
                    print(f"[{display_idx}] Name: {r['client_name']} | Date: {r['date']} | Target: {r['target_tone']}")
                
                sel = int(input("Select index number to edit: "))
                if 0 <= sel < len(matches):
                    target_orig_idx = matches[sel][0]
                    print("Editing record...")
                    records[target_orig_idx]['base_level'] = int(input("New baseline hair level (1-10): "))
                    records[target_orig_idx]['target_tone'] = input("New target vivid tone: ")
                    records[target_orig_idx]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M (Updated)")
                    save_data(records)
                    print("Record successfully updated.")
            else:
                print("No matching client found to edit.")

        elif choice == "4":
            name_query = input("Enter client name for label: ").strip().lower()
            records = load_data()
            matches = [r for r in records if name_query in r['client_name'].lower()]
            
            if matches:
                r = matches[-1]
                label_text = (
                    "===================================\n"
                    "   KARLIE'S SALON - TAKE-HOME MASK\n"
                    "===================================\n"
                    f" Client: {r['client_name']}\n"
                    f" Date Blended: {r['date']}\n"
                    f" Target Shade: {r['target_tone']}\n"
                    "-----------------------------------\n"
                    " CUSTOM FORMULA (Grams):\n"
                )
                for k, v in r['formula'].items():
                    label_text += f"   • {k}: {v}g\n"
                label_text += (
                    "===================================\n"
                    " Usage: Apply weekly on damp hair. Leave\n"
                    " on for 10 minutes, then rinse cool.\n"
                    "===================================\n"
                )
                
                # Print to terminal
                print(f"\n{label_text}")
                
                # Export to text file
                safe_name = r['client_name'].replace(" ", "_").lower()
                filename = f"{safe_name}_label.txt"
                with open(filename, "w") as f:
                    f.write(label_text)
                print(f"Label successfully exported to '{filename}' in your project folder.")
                
            else:
                print("Client not found.")
                
        elif choice == "5":
            if os.path.exists(DB_FILE):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"client_records_backup_{timestamp}.json"
                shutil.copy(DB_FILE, backup_filename)
                print(f"Database successfully backed up as '{backup_filename}'.")
            else:
                print("No database file found to backup.")
                
        elif choice == "6":
            print("Exiting Karlie's Salon Manager. Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1 through 6.")

if __name__ == "__main__":
    search_and_manage()