from salon_engine import ColorFormulaEngine
from client_passport import ClientPassport

def run_salon_workflow():
    print("=== Garza Global Salon Studio Manager ===")
    client_name = input("Enter client name: ")
    base_level = int(input("Enter client baseline hair level (1-10): "))
    target_tone = input("Enter target vivid tone (e.g., Electric Blue, Magenta): ")
    hair_grams = float(input("Enter total product quantity needed (grams): "))
    
    # Calculate mix via formula engine
    formula = ColorFormulaEngine.calculate_mix(base_level, target_tone, hair_grams)
    
    print("\n--- Calculated Gram-Weight Formula ---")
    for ingredient, weight in formula.items():
        print(f" * {ingredient}: {weight}g")
        
    # Save to client passport database
    passport = ClientPassport()
    passport.save_recipe(client_name, base_level, target_tone, formula)
    print("\nWorkflow complete! Recipe archived and ready for take-home jar label printing.")

if __name__ == "__main__":
    run_salon_workflow()