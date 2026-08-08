import csv
from sqlalchemy import create_engine, text

# Assurez-vous d'adapter l'URL de votre base de données et le mot de passe
DATABASE_URL = "postgresql://postgres:votre_mot_de_passe@localhost:5432/restaurants_db"
engine = create_engine(DATABASE_URL)

def update_price_range_from_csv(csv_path):
    with engine.connect() as conn:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                # Vérifier si la colonne price_range existe et n'est pas vide
                price_val = row.get('price_range', '').strip()
                if price_val:
                    price_clean = price_val.replace("'", "''")
                    
                    # Mise à jour par ID si présent, sinon par Name
                    if row.get('id'):
                        r_id = row['id']
                        query = text(f"UPDATE restaurants SET price_range = '{price_clean}' WHERE id = {r_id};")
                    elif row.get('name'):
                        r_name = row['name'].replace("'", "''")
                        query = text(f"UPDATE restaurants SET price_range = '{price_clean}' WHERE name ILIKE '{r_name}';")
                    else:
                        continue
                        
                    conn.execute(query)
                    count += 1
            
            conn.commit()
            print(f"✅ Mise à jour réussie : {count} prix mis à jour !")

if __name__ == "__main__":
    # Ajustez le chemin vers votre fichier CSV
    update_price_range_from_csv("data/restaurants_scraped.csv")