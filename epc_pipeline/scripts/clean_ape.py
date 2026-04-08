import json
import sqlite3
import pandas as pd
import geopandas as gpd
import fiona
import argparse
from pathlib import Path
from loguru import logger

# =========================
# CONFIG
# =========================

MASTER = "ape_dg"  # but also id from ace

DATA_LAYERS = [
    "ape_dg", "ape_de", "ape_co", "ape_im",
    "ape_imde", "ape_dtag", "ape_dter", "ape_dtre",
    "ape_vi", "cit", "ace"
]

# Chiavi sempre da tenere (e PK di riga per 1:N se esiste)
ALWAYS_KEEP = {
    "ape_dg": {"id_certificato"},
    "ape_de": {"id_certificato"},
    "ape_co": {"id_certificato", "id_qta_consumi"},
    "ape_im": {"id_certificato", "id_dettaglio_imp"},
    "ape_imde": {"id_certificato"},  # se hai un pk riga (es. id_serv_ener) aggiungilo qui
    "ape_dtag": {"id_certificato"},
    "ape_dter": {"id_certificato"},
    "ape_dtre": {"id_certificato"},
    "ape_vi": {"id_certificato"},
    "ace": {"id_certificato"},
    "cit": {"codice_impianto"},
}

# Mantieni geometria in questi layer (gli altri, anche se spaziali, diventano tabellari)
KEEP_GEOMETRY_LAYERS = {"ape_dg", "ape_de", "ape_co", "ape_im"}  # todo non funziona


def parse_args():
    defaults = {
        "ingpkg": r"C:\Users\Mocci\PycharmProjects\GeneralPurpose\to_building_energy\data\raw\raw_data.gpkg",
        "ougpkg": r"C:\Users\Mocci\PycharmProjects\GeneralPurpose\to_building_energy\data\staging\clean_data.gpkg"
    }

    p = argparse.ArgumentParser(description="Clean GeoPackage: drop redundant columns vs master, split clean/orphans.")
    p.add_argument("--in-gpkg", default=defaults["ingpkg"], help="Input GeoPackage path.")
    p.add_argument("--out-gpkg", default=defaults["ougpkg"])

    return p.parse_args()


def detect_name_field(df: pd.DataFrame) -> str:
    candidates = ["name", "column", "column_name", "field", "field_name", "nome_colonna"]
    lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower:
            return lower[cand]
    raise ValueError(f"Metadata: non trovo la colonna nome-campo. Colonne: {list(df.columns)}")


def write_table(conn: sqlite3.Connection, name: str, df: pd.DataFrame):
    df.to_sql(name, conn, if_exists="replace", index=False)


def write_layer_gdf(gpkg_path: str, layer: str, gdf: gpd.GeoDataFrame):
    gdf.to_file(gpkg_path, layer=layer, driver="GPKG")


def main():
    args = parse_args()
    gpkg_in = Path(args.in_gpkg)
    gpkg_out = Path(args.out_gpkg)
    gpkg_out.parent.mkdir(parents=True, exist_ok=True)

    # reset output
    if gpkg_out.exists():
        gpkg_out.unlink()

    # =========================
    # 1) LISTA LAYER
    # =========================
    all_layers = set(fiona.listlayers(gpkg_in))
    data_layers = [l for l in DATA_LAYERS if l in all_layers]

    if MASTER not in data_layers:
        raise ValueError(f"Non trovo '{MASTER}' nel GPKG. Trovati: {sorted(data_layers)}")

    # =========================
    # 2) ESTRAI COLONNE DA *_metadata
    # =========================
    cols_by_table = {}

    for t in data_layers:
        meta_layer = f"{t}_metadata"
        if meta_layer in all_layers:
            mdf = gpd.read_file(gpkg_in, layer=meta_layer)
            name_field = detect_name_field(mdf)
            cols_by_table[t] = set(mdf[name_field].dropna().astype(str).str.strip().tolist())
        else:
            df = gpd.read_file(gpkg_in, layer=t)
            cols_by_table[t] = set(df.columns)

    master_cols = cols_by_table[MASTER].copy()

    # =========================
    # 3) KEEP/DROP ridondanti rispetto a MASTER
    # =========================
    keep_drop = {}
    summary_rows = []

    for t in data_layers:
        cols = cols_by_table[t].copy()

        # ✅ MASTER: non eliminare nulla achne da ace
        if t == MASTER or t == 'ace':
            redundant = set()
            keep = cols.copy()
        else:
            redundant = (cols & master_cols) - ALWAYS_KEEP.get(t, set())

            # geometria: si tiene solo nei layer configurati
            if t in KEEP_GEOMETRY_LAYERS:
                redundant.add("geometry")

            keep = (cols - redundant) | (ALWAYS_KEEP.get(t, set()) & cols)

        keep_drop[t] = {"keep": sorted(keep), "drop": sorted(redundant)}
        summary_rows.append({
            "table": t, "n_cols": len(cols), "n_keep": len(keep), "n_drop": len(redundant)
        })

    summary = pd.DataFrame(summary_rows).sort_values("table").reset_index(drop=True)
    logger.info("Keep/Drop summary:\n{}", summary)
    # =========================
    # 4) ID MASTER per split orphans su tutti i layer con id_certificato
    # =========================
    dg = gpd.read_file(gpkg_in, layer=MASTER)
    ace = gpd.read_file(gpkg_in, layer="ace")
    if "id_certificato" not in dg.columns:
        raise ValueError("ape_dg non contiene id_certificato: impossibile fare orphan split.")
    master_ids = set(dg["id_certificato"].astype(str)) | set(
        ace["id_certificato"].astype(str))  # unione con ace per CIT

    # per CIT (se serve)
    ape_im_codes = set()
    if "ape_im" in data_layers:
        ape_im_df = gpd.read_file(gpkg_in, layer="ape_im")
        if "codice_impianto_cit" in ape_im_df.columns:
            ape_im_codes = set(
                ape_im_df["codice_impianto_cit"].dropna().astype(int)
            )

    # =========================
    # 5) SCRIVI OUTPUT (clean/orphans GENERALIZZATO)
    # =========================

    # scrivo solo ape_dg_clean (tutto) e orphans vuoto (opzionale)
    df = gpd.read_file(gpkg_in, layer=MASTER)
    write_layer_gdf(gpkg_out, MASTER, df)

    conn_out = sqlite3.connect(gpkg_out)

    # scrivo ace_clean (tutto) e orphans vuoto (opzionale)
    df = gpd.read_file(gpkg_in, layer='ace')
    write_table(conn_out, 'ace', df)

    def split_by_id_certificato(df: pd.DataFrame, keep_cols: list):
        d = df.copy()
        d["id_certificato"] = d["id_certificato"].astype(str)
        in_mask = d["id_certificato"].isin(master_ids)
        clean = d.loc[in_mask, keep_cols].copy()
        orph = d.loc[~in_mask, keep_cols].copy()
        return clean, orph
    logger.info("splitting layers by id_certificato and keeping columns...")
    for t in data_layers:
        if t == MASTER or t == 'ace':
            continue
        df = gpd.read_file(gpkg_in, layer=t)
        keep_cols = keep_drop[t]["keep"]

        # --- CASO CIT ---
        if t == "cit":
            cit = pd.DataFrame(df)

            # Se cit ha id_certificato -> split standard
            if "id_certificato" in cit.columns:
                cit["id_certificato"] = cit["id_certificato"].astype(str)
                keep_cols_cit = [c for c in keep_cols if c in cit.columns]
                clean, orph = split_by_id_certificato(cit, keep_cols_cit)
                write_table(conn_out, "cit_clean", clean)
                write_table(conn_out, "cit_orphans", orph)

            # Altrimenti split su codice_impianto rispetto a ape_im.codice_impianto_cit
            elif "codice_impianto" in cit.columns and len(ape_im_codes) > 0:
                cit["codice_impianto"] = cit["codice_impianto"].astype(int)
                in_mask = cit["codice_impianto"].isin(ape_im_codes)
                keep_cols_cit = [c for c in keep_cols if c in cit.columns]
                clean = cit.loc[in_mask, keep_cols_cit].copy()
                orph = cit.loc[~in_mask, keep_cols_cit].copy()
                write_table(conn_out, "cit_clean", clean)
                write_table(conn_out, "cit_orphans", orph)

            else:
                # non riesco a fare split -> scrivo solo pulita
                out = cit[[c for c in keep_cols if c in cit.columns]].copy()
                write_table(conn_out, "cit_clean", out)

            continue

        # --- CASO GENERALE: se ha id_certificato, split sempre ---
        has_id = "id_certificato" in df.columns

        # Gestione layer spaziali vs tabellari
        is_spatial = isinstance(df, gpd.GeoDataFrame) and df.geometry is not None and df.geometry.name in df.columns
        geom_name = df.geometry.name if is_spatial else None

        if has_id:
            base = df[keep_cols].copy()

            # se è spaziale e geometry non è in keep_cols, la trasformiamo in tabella
            if is_spatial and geom_name not in keep_cols:
                base = pd.DataFrame(df.drop(columns=[geom_name], errors="ignore"))[keep_cols].copy()

            clean, orph = split_by_id_certificato(pd.DataFrame(base), keep_cols)

            # Scrittura: se tabellare -> to_sql; se spaziale -> to_file
            if is_spatial and (geom_name in keep_cols) and (t in KEEP_GEOMETRY_LAYERS):
                clean_gdf = gpd.GeoDataFrame(clean, geometry=geom_name, crs=df.crs)
                orph_gdf = gpd.GeoDataFrame(orph, geometry=geom_name, crs=df.crs)
                write_layer_gdf(gpkg_out, f"{t}_clean", clean_gdf)
                write_layer_gdf(gpkg_out, f"{t}_orphans", orph_gdf)
            else:
                write_table(conn_out, f"{t}_clean", clean)
                write_table(conn_out, f"{t}_orphans", orph)

        else:
            # non ha id_certificato -> scrivo solo pulita
            if is_spatial and (geom_name in keep_cols) and (t in KEEP_GEOMETRY_LAYERS):
                out_gdf = df[keep_cols].copy()
                out_gdf = gpd.GeoDataFrame(out_gdf, geometry=geom_name, crs=df.crs)
                write_layer_gdf(gpkg_out, f"{t}_clean", out_gdf)
            else:
                out_df = pd.DataFrame(df)[keep_cols].copy()
                write_table(conn_out, f"{t}_clean", out_df)
        logger.info(f"{t} Done.")
    conn_out.close()

    # =========================
    # 6) REPORT
    # =========================
    folder_path = Path(gpkg_out).parent
    summarypath = folder_path / "keep_drop_summary.xlsx"
    detailpath = folder_path / "keep_drop_detail.json"
    summary.to_excel(summarypath, index=False)
    with open(detailpath, "w", encoding="utf-8") as f:
        json.dump(keep_drop, f, ensure_ascii=False, indent=2)

    logger.info(f"Done: {gpkg_out}")
    logger.info(f"Report: {summarypath}, {detailpath}")


if __name__ == "__main__":
    main()
