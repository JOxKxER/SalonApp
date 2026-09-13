class ColorFormulaEngine:
    @staticmethod
    def calculate_mix(base_level: int, target_vivid_tone: str, hair_grams: float) -> dict:
        multiplier = 0.8 if base_level > 7 else 1.2
        direct_pigment_grams = hair_grams * 0.15 * multiplier
        base_conditioner_grams = hair_grams - direct_pigment_grams
        
        return {
            "Neutral Base (Grams)": round(base_conditioner_grams, 2),
            f"Direct Pigment ({target_vivid_tone}) (Grams)": round(direct_pigment_grams, 2)
        }

# Test the formula engine with a sample client
if __name__ == "__main__":
    print("--- Salon App Formula Test ---")
    result = ColorFormulaEngine.calculate_mix(base_level=6, target_vivid_tone="Electric Blue", hair_grams=100.0)
    for key, value in result.items():
        print(f"{key}: {value}g")