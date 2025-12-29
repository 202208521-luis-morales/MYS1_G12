import os
import re
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

PHASES_DIR = "./ANALISISDATOS/phases"   
OUT_DIR = "out"    
PHASE_FILE_PATTERN = r"^phase(\d+)\.csv$"  
 

os.makedirs(OUT_DIR, exist_ok=True)

def load_matrix_csv(path: str) -> pd.DataFrame:
    """
    Lee CSV con formato:
    "","1","4","89"
    "1",0,1,4
    ...
    Devuelve DataFrame cuadrado con índices/columnas como strings (IDs de libros).
    """
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(str)
    df.columns = df.columns.astype(str)

    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    return df

def build_graph_from_matrix(df: pd.DataFrame) -> nx.DiGraph:
    """
    Construye grafo dirigido ponderado:
    arista u->v si df.loc[u,v] > 0 y u != v
    weight = df.loc[u,v]
    """
    G = nx.DiGraph()
    # nodos: unión de filas y columnas
    nodes = sorted(set(df.index).union(set(df.columns)))
    G.add_nodes_from(nodes)

    for u in df.index:
        for v in df.columns:
            w = df.loc[u, v]
            if w > 0 and u != v:
                G.add_edge(u, v, weight=float(w))
    return G

def compute_metrics(G: nx.DiGraph, df: pd.DataFrame) -> pd.DataFrame:
    """
    Métricas pedidas:
    - Libro base: número de conexiones (sin peso) = cuenta columnas > 0 por fila
    - Libro importante: suma de pesos por fila
    - Centralidad de grado (grado): suma del "Libro importante" de los libros conectados
    - Grado de centralidad normalizado: libro_base / (n-1)
    - Intermediación normalizada: (Libro importante / libro base) / denominador
    """
    n = len(df)
    
    # ==============================
    # Libro base: cuántos libros cita cada libro (columnas > 0)
    # ==============================
    libro_base = (df > 0).sum(axis=1)
    
    # ==============================
    # Libro importante: suma de pesos por fila
    # ==============================
    libro_importante = df.sum(axis=1)
    
    # Diccionario para acceso rápido
    libro_importante_dict = libro_importante.to_dict()
    
    # ==============================
    # Centralidad de grado (grado)
    # Suma del "Libro importante" de los libros a los que está conectado
    # ==============================
    grado = []
    for libro in df.index:
        # Libros conectados (columnas con valor > 0 en esa fila)
        fila = df.loc[libro]
        conectados = fila[fila > 0].index.tolist()
        
        # Sumar el "Libro importante" de cada libro conectado
        suma_grado = 0
        for c in conectados:
            if c in libro_importante_dict:
                suma_grado += libro_importante_dict[c]
        
        grado.append(suma_grado)
    
    # ==============================
    # Grado de centralidad normalizado
    # ==============================
    if n > 1:
        grado_centralidad_norm = (libro_base / (n - 1)).round(4)
    else:
        grado_centralidad_norm = pd.Series([0.0] * n, index=df.index)
    
    # ==============================
    # Centralidad de intermediación normalizada
    # ==============================
    denominador = ((n - 1) * (n - 2)) / 2 if n > 2 else 1
    
    intermediacion = (
        (libro_importante / libro_base.replace(0, 1)) / denominador
    ).round(6)

    # ==============================
    # Construir DataFrame resultado
    # ==============================
    out = pd.DataFrame({
        "Libro": df.index.tolist(),
        "Libro_base_conexiones": libro_base.values,
        "Libro_importante_pesos_totales": libro_importante.values,
        "Centralidad_grado": grado,
        "Grado_centralidad_normalizado": grado_centralidad_norm.values,
        "Intermediacion_normalizada": intermediacion.values,
    })

    # Ordenar por Libro importante y luego por Centralidad de grado
    out = out.sort_values(
        ["Libro_importante_pesos_totales", "Centralidad_grado"],
        ascending=[False, False]
    ).reset_index(drop=True)

    return out

def plot_graph(G: nx.DiGraph, title: str, out_png: str):
    """
    Grafica red con estilo mejorado.
    Usa spring_layout con más iteraciones para mejor distribución.
    """
    plt.figure(figsize=(12, 10))
    
    # Layout con más iteraciones para mejor distribución
    pos = nx.spring_layout(G, k=2, iterations=50, seed=7)

    # Dibujar nodos con estilo mejorado
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                           node_size=800, alpha=0.9)

    # Dibujar aristas con flechas más visibles
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                           arrows=True, arrowsize=20, 
                           width=2, alpha=0.6)

    # Etiquetas de nodos con mejor formato
    nx.draw_networkx_labels(G, pos, font_size=10, 
                            font_weight='bold')

    # Etiquetas de aristas (pesos)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    # Convertir a enteros para mejor visualización
    edge_labels = {k: int(v) for k, v in edge_labels.items()}
    
    # Solo mostrar etiquetas si no hay demasiadas aristas
    if len(edge_labels) <= 120:
        nx.draw_networkx_edge_labels(G, pos, edge_labels, 
                                      font_size=8)

    plt.title(title, fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close()

def list_phase_files(folder: str):
    files = []
    for name in os.listdir(folder):
        m = re.match(PHASE_FILE_PATTERN, name.lower())
        if m:
            files.append((int(m.group(1)), os.path.join(folder, name)))
    files.sort(key=lambda x: x[0])
    return files

def main():
    phase_files = list_phase_files(PHASES_DIR)
    if not phase_files:
        raise FileNotFoundError("No encontré archivos phaseX.csv en la carpeta actual.")

    all_metrics = []
    winners = []

    for phase_num, path in phase_files:
        print(f"Procesando fase {phase_num}: {path}")

        df = load_matrix_csv(path)
        G = build_graph_from_matrix(df)

        png_path = os.path.join(OUT_DIR, f"grafo_fase_{phase_num}.png")
        plot_graph(G, f"Fase {phase_num}", png_path)

        met = compute_metrics(G, df)
        met["Fase"] = phase_num

        csv_path = os.path.join(OUT_DIR, f"metricas_fase_{phase_num}.csv")
        met.to_csv(csv_path, index=False)

        top = met.iloc[0]
        winners.append({
            "Fase": phase_num,
            "Libro_mas_importante": top["Libro"],
            "Libro_importante": float(top["Libro_importante_pesos_totales"]),
            "Centralidad_grado": float(top["Centralidad_grado"]),
            "Intermediacion": float(top["Intermediacion_normalizada"]),
        })

        all_metrics.append(met)

    winners_df = pd.DataFrame(winners).sort_values("Fase")
    winners_df.to_csv(os.path.join(OUT_DIR, "resumen_libro_mas_importante_por_fase.csv"), index=False)

    # Promedios globales 11 fases
    all_df = pd.concat(all_metrics, ignore_index=True)
    avg = all_df.groupby("Libro", as_index=False).mean(numeric_only=True)
    avg = avg.sort_values(
        ["Libro_importante_pesos_totales", "Centralidad_grado"],
        ascending=[False, False]
    )
    avg.to_csv(os.path.join(OUT_DIR, "promedios_globales_11_fases.csv"), index=False)

    global_top = avg.iloc[0]
    print("\n==== LISTO ====")
    print(f"Carpeta de salida: {OUT_DIR}")
    print("Ganador global (por promedios):")
    print(global_top.to_string(index=False))

if __name__ == "__main__":
    main()