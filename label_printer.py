import json

def generate_label():
    try:
        with open("client_records.json", "r") as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No records found.")
        return

    print("\n=== Take-Home Mask Label Generator ===")
    name_query = input("Enter client name for label: ").strip().lower()
    matches = [r for r in records if name_query in r['client_name'].lower()]

    if matches:
        # Grab the most recent record
        r = matches[-1]
        print("\n" + "="*35)
        print("   GARZA GLOBAL SALON - TAKE-HOME MASK")
        print("="*35)
        print(f" Client: {r['client_name']}")
        print(f" Date Blended: {r['date']}")
        print(f" Target Shade: {r['target_tone']}")
        print("-" * 35)
        print(" CUSTOM FORMULA (Grams):")
        for k, v in r['formula'].items():
            print(f"   • {k}: {v}g")
        print("="*35)
        print(" Usage: Apply weekly on damp hair. Leave")
        print(" on for 10 minutes, then rinse cool.")
        print("="*35 + "\n")
    else:
        print("Client not found.")

if __name__ == "__main__":
    generate_label()