"""
Source mapping on recorded attributes, so the rules can be checked without the WFS.

The samples are the attribute names and values the live services actually return.
"""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from city_information_modeler.core import schema
from city_information_modeler.core.sources import BdtreFootprintSource, DbgtFootprintSource


def dbgt_frame(rows):
    """A frame shaped like the DBGT Edificato layer."""
    geometries = []
    for index in range(len(rows)):
        geometries.append(box(395000 + index * 20, 4990000, 395010 + index * 20, 4990010))
    frame = pd.DataFrame(rows)
    return gpd.GeoDataFrame(frame, geometry=geometries, crs="EPSG:32632").to_crs(4326)


DBGT_ROW = {
    "codice_intesa": "020101",
    "gruppo": "EDIFICI PRINCIPALI",
    "descrizione": "generica",
    "categoria_uso": "residenziale",
    "epoca_costruzione": "1919 - 1945",
    "numero_piani": "5",
    "altezza_edificio": "16.20",
    "valenza_storica": "non monumentale",
    "nome": "",
    "qt_gronda": "247.20",
    "qt_suolo": "239.47",
    "transito": "",
}


def test_dbgt_maps_the_published_fields():
    result = DbgtFootprintSource().normalize(dbgt_frame([DBGT_ROW]))
    row = result.iloc[0]

    assert list(result.columns) == schema.STANDARD_COLUMNS
    assert row["source"] == "dbgt"
    assert row["usage"] == "residential"
    assert row["height_m"] == pytest.approx(16.20)
    assert row["height_source"] == "dbgt_altezza_edificio"
    assert row["n_floors"] == 5
    assert row["is_monument"] is False or row["is_monument"] == False  # noqa: E712
    assert pd.isna(row["name"])


@pytest.mark.parametrize(
    "period,expected_from,expected_to,expected_year",
    [
        ("1919 - 1945", 1919, 1945, 1932),
        ("1946 - 1960", 1946, 1960, 1953),
        ("2017", 2017, 2017, 2017),
        ("1918 (al ..)", None, 1918, 1918),
        ("non conosciuto", None, None, None),
        ("", None, None, None),
    ],
)
def test_dbgt_parses_every_published_period_shape(
    period, expected_from, expected_to, expected_year
):
    row = dict(DBGT_ROW, epoca_costruzione=period)
    result = DbgtFootprintSource().normalize(dbgt_frame([row])).iloc[0]

    def value(cell):
        return None if pd.isna(cell) else int(cell)

    assert value(result["construction_year_from"]) == expected_from
    assert value(result["construction_year_to"]) == expected_to
    assert value(result["construction_year"]) == expected_year


def test_dbgt_hierarchical_usage_falls_back_to_its_first_level():
    """An unseen sub-category must still land in the right family, not in 'unknown'."""
    row = dict(DBGT_ROW, categoria_uso="ricreativo - qualcosa di nuovo")
    result = DbgtFootprintSource().normalize(dbgt_frame([row])).iloc[0]
    assert result["usage"] == "culture"


def test_dbgt_falls_back_to_elevation_difference_for_height():
    row = dict(DBGT_ROW, altezza_edificio="")
    result = DbgtFootprintSource().normalize(dbgt_frame([row])).iloc[0]

    assert result["height_m"] == pytest.approx(247.20 - 239.47)
    assert result["height_source"] == "dbgt_eave_minus_ground"


def test_dbgt_minor_buildings_are_flagged_and_droppable():
    rows = [DBGT_ROW, dict(DBGT_ROW, gruppo="EDIFICI MINORI (O DI PERTINENZA)")]
    frame = dbgt_frame(rows)

    assert len(DbgtFootprintSource.keep_principal_buildings(frame)) == 1
    assert DbgtFootprintSource().normalize(frame)["is_minor_building"].tolist() == [
        False,
        True,
    ]


def test_dbgt_ids_are_stable_and_derived_from_geometry():
    """DBGT publishes no identifier, so the same footprint must always give the same id."""
    frame = dbgt_frame([DBGT_ROW, dict(DBGT_ROW, categoria_uso="commerciale")])
    first = DbgtFootprintSource().normalize(frame)
    second = DbgtFootprintSource().normalize(frame)

    assert first["building_uuid"].tolist() == second["building_uuid"].tolist()
    assert first["building_uuid"].is_unique


def bdtre_frame(rows):
    """A frame shaped like the BDTRE edifc layer after heights are attached."""
    geometries = []
    for index in range(len(rows)):
        geometries.append(box(395000 + index * 20, 4990000, 395010 + index * 20, 4990010))
    frame = pd.DataFrame(rows)
    return gpd.GeoDataFrame(frame, geometry=geometries, crs="EPSG:32632").to_crs(4326)


BDTRE_ROW = {
    "uuid": "836a3e51-44a4-4e92-bd0e-66eea91a16f2",
    "data_acq": "2019-11-30 00:00:00",
    "data_agg": "2019-11-30 00:00:00",
    "data_fin": "9999-12-31 00:00:00",
    "ente_for": "REGIONE PIEMONTE",
    "ente_prod": "REGIONE PIEMONTE",
    "modo_prod": "banche dati esterne - catasto",
    "sc_acq": "1:2000",
    "edifc_ty": "generica",
    "edifc_uso": "residenziale e commerciale",
    "edifc_stat": "costruito",
    "edifc_mon": "0",
    "edifc_nome": "",
    "edifc_idag": "",
    "edifc_ided": "",
    "height_m": 16.0,
    "height_source": "bdtre_un_vol",
    "volume_units": 1,
}


def test_bdtre_maps_the_published_fields():
    result = BdtreFootprintSource().normalize(bdtre_frame([BDTRE_ROW])).iloc[0]

    assert result["source"] == "bdtre"
    assert result["usage"] == "mixed_residential_commercial"
    assert result["height_m"] == pytest.approx(16.0)
    assert result["survey_year"] == 2019
    assert result["building_group"] == "principal"


def test_bdtre_leaves_construction_year_empty_by_default():
    """The survey year is not a construction year, so it must not silently become one."""
    result = BdtreFootprintSource().normalize(bdtre_frame([BDTRE_ROW])).iloc[0]

    assert pd.isna(result["construction_year"])
    assert pd.isna(result["construction_year_source"])


def test_bdtre_survey_proxy_is_opt_in_and_labelled():
    source = BdtreFootprintSource(construction_year_from_survey=True)
    result = source.normalize(bdtre_frame([BDTRE_ROW])).iloc[0]

    assert result["construction_year"] == 2019
    assert result["construction_year_source"] == "bdtre_survey_year_proxy"


def test_bdtre_ids_come_from_the_published_uuid():
    result = BdtreFootprintSource().normalize(bdtre_frame([BDTRE_ROW])).iloc[0]
    assert result["building_uuid"] == schema.building_uuid("bdtre", BDTRE_ROW["uuid"])


def test_both_sources_return_the_same_schema():
    bdtre = BdtreFootprintSource().normalize(bdtre_frame([BDTRE_ROW]))
    dbgt = DbgtFootprintSource().normalize(dbgt_frame([DBGT_ROW]))
    assert list(bdtre.columns) == list(dbgt.columns) == schema.STANDARD_COLUMNS
