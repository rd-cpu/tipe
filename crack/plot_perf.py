import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

script_dir = Path(__file__).parent

try:
    df_force = pd.read_csv(script_dir / 'perf_crack_force_brute.csv', encoding='latin-1')
    df_rho = pd.read_csv(script_dir / 'perf_crack_rho_de_pollard.csv', encoding='latin-1')
except Exception as e:
    print(f"Error with latin-1: {e}")
    df_force = pd.read_csv(script_dir / 'perf_crack_force_brute.csv', encoding='utf-8', errors='ignore')
    df_rho = pd.read_csv(script_dir / 'perf_crack_rho_de_pollard.csv', encoding='utf-8', errors='ignore')

df_force.columns = [col.strip() for col in df_force.columns]
df_rho.columns = [col.strip() for col in df_rho.columns]

df_force['Ordre'] = pd.to_numeric(df_force['Ordre'], errors='coerce')
df_force['Temps Moyen'] = pd.to_numeric(df_force['Temps Moyen'], errors='coerce')
df_rho['Ordre'] = pd.to_numeric(df_rho['Ordre'], errors='coerce')
df_rho['Temps Moyen'] = pd.to_numeric(df_rho['Temps Moyen'], errors='coerce')

df_force = df_force.dropna(subset=['Ordre', 'Temps Moyen'])
df_rho = df_rho.dropna(subset=['Ordre', 'Temps Moyen'])

print(f"Loaded {len(df_force)} Brute Force records and {len(df_rho)} Rho records")

force_grouped = df_force.groupby('Ordre')['Temps Moyen'].mean().reset_index().sort_values('Ordre')
rho_grouped = df_rho.groupby('Ordre')['Temps Moyen'].mean().reset_index().sort_values('Ordre')

print(f"\nBrute Force ordres uniques:    {force_grouped['Ordre'].tolist()}")
print(f"Rho de Pollard ordres uniques: {rho_grouped['Ordre'].tolist()}")

plt.figure(figsize=(12, 7))

if len(force_grouped) > 0:
    plt.plot(force_grouped['Ordre'], force_grouped['Temps Moyen'], 
             marker='o', label='Brute Force', linewidth=2, markersize=8, color='blue')
if len(rho_grouped) > 0:
    plt.plot(rho_grouped['Ordre'], rho_grouped['Temps Moyen'], 
             marker='s', label='Rho de Pollard', linewidth=2, markersize=8, color='red')

plt.xlabel('Ordre de la Courbe Elliptique', fontsize=12)
plt.ylabel('Temps Moyen (secondes)', fontsize=12)
plt.title('Temps de Craquage en Fonction de l\'Ordre de la Courbe', fontsize=14, fontweight='bold')

plt.xscale('log')
plt.yscale('log')

plt.grid(True, which='both', alpha=0.3, linestyle='--')
plt.legend(fontsize=11, loc='upper left')
plt.tight_layout()

output_path = script_dir / 'perf_crack_graph.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\nGraph sauvegardé à : {output_path}")

plt.show()

print("\n=== Brute Force Performance ===")
for _, row in force_grouped.iterrows():
    print(f"Ordre {int(row['Ordre']):>12}: {row['Temps Moyen']:.3f}s")

print("\n=== Rho de Pollard Performance ===")
for _, row in rho_grouped.iterrows():
    print(f"Ordre {int(row['Ordre']):>12}: {row['Temps Moyen']:.3f}s")

print("\n=== Comparaison ===")
for order in sorted(set(force_grouped['Ordre'].tolist() + rho_grouped['Ordre'].tolist())):
    bf = force_grouped[force_grouped['Ordre'] == order]['Temps Moyen'].values
    rh = rho_grouped[rho_grouped['Ordre'] == order]['Temps Moyen'].values
    if len(bf) > 0 and len(rh) > 0:
        ratio = rh[0] / bf[0]
        print(f"Ordre {int(order):>12}: BF={bf[0]:.2f}s vs Rho={rh[0]:.2f}s (Rho {ratio:.1f}x {'plus lent' if ratio > 1 else 'plus rapide'})")
