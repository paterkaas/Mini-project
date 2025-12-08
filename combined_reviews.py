import json
import glob
import os

def combine_json_reviews(output_filename='combined_reviews.json'):
    """
    Zoekt naar alle .json-bestanden in de huidige map, 
    leest de 'reviews'-lijsten en voegt ze samen in één nieuw bestand.
    """
    
    # Zoek alle json-bestanden in de map waar het script draait
    json_files = glob.glob('*.json')
    
    # Zorg ervoor dat we het output-bestand niet per ongeluk meenemen
    # als het al bestaat van een eerdere uitvoering.
    if output_filename in json_files:
        json_files.remove(output_filename)

    print(f"Gevonden JSON-bestanden om te verwerken: {json_files}")

    all_reviews_list = []
    files_processed = 0
    files_failed = []

    # Loop door elk gevonden bestand
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Controleer of de structuur klopt (een 'reviews'-key met een lijst)
                if 'reviews' in data and isinstance(data['reviews'], list):
                    all_reviews_list.extend(data['reviews'])
                    files_processed += 1
                else:
                    print(f"WAARSCHUWING: Bestand {file_path} heeft geen 'reviews'-lijst. Wordt overgeslagen.")
                    files_failed.append(file_path)
                    
        except json.JSONDecodeError:
            print(f"FOUT: Kon JSON niet lezen uit {file_path}. Is het een geldig JSON-bestand? Wordt overgeslagen.")
            files_failed.append(file_path)
        except Exception as e:
            print(f"FOUT: Onverwachte error bij verwerken van {file_path}: {e}. Wordt overgeslagen.")
            files_failed.append(file_path)

    # Maak de nieuwe datastructuur voor het gecombineerde bestand
    combined_data = {"reviews": all_reviews_list}

    # Schrijf de gecombineerde data naar het nieuwe bestand
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            # 'indent=2' maakt het bestand leesbaar
            # 'ensure_ascii=False' zorgt dat speciale tekens goed worden opgeslagen
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print("\n--- Voltooid ---")
        print(f"Succesvol {files_processed} bestand(en) verwerkt.")
        print(f"Totaal aantal reviews samengevoegd: {len(all_reviews_list)}")
        print(f"Resultaat opgeslagen in: {output_filename}")
        
        if files_failed:
            print(f"\nMislukt of overgeslagen: {len(files_failed)} bestand(en): {files_failed}")
            
    except Exception as e:
        print(f"\nFOUT: Kon het gecombineerde bestand niet wegschrijven: {e}")

# --- Voer de functie uit als het script direct wordt gerund ---
if __name__ == "__main__":
    combine_json_reviews()