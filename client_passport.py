import json
from datetime import datetime

class ClientPassport:
    def __init__(self, storage_file="client_records.json"):
        self.storage_file = storage_file

    def save_recipe(self, client_name: str, base_level: int, target_tone: str, formula_result: dict):
        record = {
            "client_name": client_name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "base_level": base_level,
            "target_tone": target_tone,
            "formula": formula_result
        }
        
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
            
        data.append(record)
        
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved passport record for {client_name}.")

if __name__ == "__main__":
    passport = ClientPassport()
    sample_mix = {"Neutral Base (Grams)": 82.0, "Direct Pigment (Electric Blue) (Grams)": 18.0}
    passport.save_recipe("Jane Doe", base_level=6, target_tone="Electric Blue", formula_result=sample_mix)