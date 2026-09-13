import json

def view_passports():
    try:
        with open("client_records.json", "r") as f:
            records = json.load(f)
            print(f"--- Archived Client Passports ({len(records)} found) ---")
            for r in records:
                print(f"Client: {r['client_name']} | Date: {r['date']} | Level: {r['base_level']} | Target: {r['target_tone']}")
                for k, v in r['formula'].items():
                    print(f"   - {k}: {v}g")
                print("-" * 30)
    except FileNotFoundError:
        print("No client records found yet.")

if __name__ == "__main__":
    view_passports()