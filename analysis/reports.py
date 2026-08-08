import os
import pandas as pd

def generate_summary_report(df_restaurants: pd.DataFrame, output_path: str = "exports/summary_report.csv"):
    """Génère un rapport récapitulatif par pays et par ville."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    agg_dict = {
        'nombre_restaurants': ('id', 'count'),
        'note_moyenne': ('rating', 'mean')
    }
    
    if 'reviews_count' in df_restaurants.columns:
        agg_dict['total_avis'] = ('reviews_count', 'sum')

    group_cols = [col for col in ['country', 'city'] if col in df_restaurants.columns]
    
    if not group_cols:
        report = df_restaurants.describe()
    else:
        report = df_restaurants.groupby(group_cols).agg(**agg_dict).reset_index()
        report['note_moyenne'] = report['note_moyenne'].round(2)
        
    report.to_csv(output_path, index=False)
    print(f"Rapport sauvegardé avec succès sous : {output_path}")
    return report