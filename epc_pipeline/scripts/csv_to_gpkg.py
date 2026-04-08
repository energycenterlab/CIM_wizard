import pandas as pd
import json
from pathlib import Path
import argparse
import geopandas as gpd
from loguru import logger

X_NAMES = ["x", "X", "xcoord", "XCoord", "longitude", "lon", "coord_e"]
Y_NAMES = ["y", "Y", "ycoord", "YCoord", "latitude", "lat", "coord_n"]

ROOT = Path(__file__).parent.parent

NULL_STRINGS = {"nan", "null", "none", ""}

def normalize_nulls(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if col == "geometry":
            continue
        s = out[col]
        if s.dtype == "object" or pd.api.types.is_string_dtype(s):
            s2 = s.astype("string").str.strip()
            mask = s2.isna() | s2.str.lower().isin(NULL_STRINGS)
            out.loc[mask, col] = pd.NA
    return out

def column_coverage_report(df: pd.DataFrame):
    df2 = normalize_nulls(df)
    n = len(df2)
    lines = []

    for col in df2.columns:
        if col == "geometry":
            continue
        non_null = df2[col].notna().sum()
        pct = (non_null / n * 100) if n else 0
        lines.append(f"    - {col}: coverage={pct:.2f}% ({non_null}/{n})")

    return lines

def key_analysis_report(df: pd.DataFrame, key: str, tolerance=0.01):
    if key not in df.columns:
        return [f"    - {key}: NOT PRESENT"]

    df2 = normalize_nulls(df[[key]])
    s = df2[key]

    non_null = s.notna().sum()
    if non_null == 0:
        return [f"    - {key}: NO DATA"]

    unique = s.dropna().astype(str).nunique()
    dup = non_null - unique
    dup_rate = dup / non_null if non_null else 0
    relation = "1:1" if dup_rate <= tolerance else "1:N"

    return [
        f"    - {key}:",
        f"        non-null = {non_null}",
        f"        unique   = {unique}",
        f"        dup      = {dup} ({dup_rate*100:.2f}%)",
        f"        relation = {relation}",
    ]

def build_layer_report(gdf: gpd.GeoDataFrame, layer_name: str, layer_type: str):
    lines = []
    lines.append(f"LAYER: {layer_name}")
    lines.append(f"Rows: {len(gdf)}")
    lines.append(f"Type: {'SPATIAL' if layer_type == "spatial" else 'TABLE'}")

    lines.append("Key analysis:")
    for key in ["id_certificato", "codice_impianto"]:
        lines.extend(key_analysis_report(gdf, key))

    lines.append("Column coverage:")
    lines.extend(column_coverage_report(gdf))

    return "\n".join(lines)

def find_coordinates(df):
    """Trova le colonne x e y nel DataFrame, se presenti"""
    x_col = next((col for col in X_NAMES if col in df.columns), None)
    y_col = next((col for col in Y_NAMES if col in df.columns), None)
    if x_col and y_col:
        return x_col, y_col
    return None, None

def save_csv_with_metadata_to_gpkg(csv_path, metadata_json, gpkg_path, layer_name):
    df = pd.read_csv(csv_path, sep=";", decimal=",",dtype=str, on_bad_lines='skip', engine="python")
    logger.info("CSV loaded: {} rows", len(df))
    if isinstance(metadata_json, str):
        with open(metadata_json, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        metadata = metadata_json

    dtype_map = {"string": str, "int": "Int64", "double": float}

    for col_meta in metadata['components']:
        col = col_meta["name"]
        dt = col_meta["datatype"]
        if col in df.columns:
            try:
                if dt == "double":
                    df[col] = pd.to_numeric(df[col].str.replace(",", "."), errors='coerce')
                else:
                    df[col] = df[col].astype(dtype_map.get(dt, str))
            except ValueError:
                logger.warning(f"Attenzione: conversione del campo '{col}' al tipo '{dt}' non riuscita. Rimane Stringa")
                continue
        else:
            logger.warning(f'Colonna "{col}" non trovata nel CSV. Aggiunta come colonna vuota con stringa Null.')
            df[col] = pd.Series(['Null']*len(df))

    x_col, y_col = find_coordinates(df)
    if x_col and y_col:
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[x_col], df[y_col]), crs="EPSG:4326")
        logger.info(f"Trovate coordinate: ({x_col}, {y_col}) → layer geometrico")
        layer_type = "spatial"
    else:
        gdf = gpd.GeoDataFrame(df)  # senza geometria
        logger.info(f"Nessuna coppia di coordinate trovata → layer tabellare")
        layer_type = "table"

    gpkg_path = ROOT / Path(gpkg_path)
    Path(gpkg_path).parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG", overwrite=True)

    meta_df = gpd.GeoDataFrame(metadata['components'])
    meta_df["layer"] = layer_name
    meta_df["dataset"] = metadata['dataset']['code']
    meta_df.to_file(gpkg_path, layer=f"{layer_name}_metadata", driver="GPKG")
    logger.info(f"CSV '{csv_path}' e metadati salvati in '{gpkg_path}'")
    logger.info(f"Layer: {layer_name}, righe: {len(gdf)} (perse {1-len(gdf)/len(df)} % di righe), colonne: {len(gdf.columns)}")

    report_text = build_layer_report(gdf, layer_name, layer_type)

    marker_path = Path(gpkg_path).parent / Path(f".done_{layer_name}")
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    with open(marker_path, "w", encoding="utf-8") as f:
        f.write(report_text)

def main():
    defaults = {
        "csv": "C:/Users/Mocci/Documents/QgisProjects/PED_TO/data/regpie-Sicee_v_t_export_bo_ape_18895-all.csv",
        "metadata": "C:/Users/Mocci/Documents/QgisProjects/PED_TO/data/regpie-Sicee_v_t_export_bo_ape_18895-all.json",
        "gpkg": "data/raw/raw_data_test.gpkg",
        "layer": "prova"
    }

    parser = argparse.ArgumentParser(description="Save csv with json metadata in GeoPackage")
    parser.add_argument("--csv","-c",dest="csv",type=str, default=defaults['csv'], help="Path to input CSV file")
    parser.add_argument("--metadata","-m",dest="metadata",type=str, default=defaults['metadata'], help="Path to metadata JSON file")
    parser.add_argument("--gpkg","-g",dest="gpkg",type=str, default=defaults['gpkg'], help="Path to output GeoPackage file")
    parser.add_argument("--layer","-l",dest="layer",type=str, default=defaults['layer'], help="Layer name in GeoPackage")
    args = parser.parse_args()

    # Setup logging per layer
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    logger.add(log_path / f"{args.layer}.log", rotation="10 MB", level="DEBUG")

    logger.info("Starting CSV to GPKG conversion for layer: {}", args.layer)

    save_csv_with_metadata_to_gpkg(args.csv, args.metadata, args.gpkg, args.layer)



if __name__ == "__main__":
    main()
