"""
Weather file downloader for EnergyPlus / CESAR-P simulations.

EnergyPlus uses .epw (EnergyPlus Weather) files containing 8760 hours of:
  - Dry-bulb temperature (°C)
  - Dew-point temperature (°C)
  - Relative humidity (%)
  - Atmospheric pressure (Pa)
  - Direct/diffuse solar radiation (W/m²)
  - Wind speed & direction
  - Sky cover

Sources:
  A) climate.onebuilding.org  — largest free EPW repository (17 000+ stations)
  B) PVGIS via pvlib           — ERA5 TMY for any lat/lon in Europe/Africa/Asia
  C) EnergyPlus.net website    — curated selection for major world cities

Usage:
    python 00_weather_downloader.py
"""

from __future__ import annotations

import os
import re
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Method A: Direct download from climate.onebuilding.org
# ---------------------------------------------------------------------------
# Browse https://climate.onebuilding.org to find the URL for your city.
# The URL pattern is:
#   https://climate.onebuilding.org/WMO_Region_X/<COUNTRY>/<STATE_CODE>/<FILE>.zip
#
# Example — Florence (Italy):
ONEBUILDING_EPW_URL = (
    "https://climate.onebuilding.org/WMO_Region_6_Europe/"
    "ITA_Italy/TOS_Tuscany/ITA_TOS_Florence.Peretola.161800_TMYx.2009-2023.zip"
)

WEATHER_OUTPUT_DIR = Path("data/weather")


def download_epw_from_onebuilding(url: str, output_dir: Path) -> Path:
    """
    Download an EPW zip from climate.onebuilding.org and extract the .epw file.

    Parameters
    ----------
    url : str
        Direct URL to the .zip file on climate.onebuilding.org.
    output_dir : Path
        Directory where the .epw will be saved.

    Returns
    -------
    Path
        Path to the extracted .epw file.
    """
    import zipfile

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "downloaded_weather.zip"

    print(f"Downloading weather file from:\n  {url}")
    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        epw_files = [f for f in z.namelist() if f.endswith(".epw")]
        if not epw_files:
            raise FileNotFoundError("No .epw file found inside the downloaded zip.")
        z.extract(epw_files[0], output_dir)
        epw_path = output_dir / epw_files[0]

    zip_path.unlink()
    print(f"EPW saved to: {epw_path}")
    return epw_path


# ---------------------------------------------------------------------------
# Method B: PVGIS TMY via pvlib (for any lat/lon in Europe/Africa/Asia)
# ---------------------------------------------------------------------------
# pvlib fetches hourly TMY data from the EU Joint Research Centre PVGIS API
# and can export it as an EPW file using ladybug-core.
#
# Requires: pip install pvlib ladybug-core

def download_epw_from_pvgis(
    latitude: float,
    longitude: float,
    output_dir: Path,
    location_name: str = "site",
) -> Path:
    """
    Build an EPW file from PVGIS TMY data for any lat/lon.

    Parameters
    ----------
    latitude : float
        Site latitude in decimal degrees (e.g. 43.78 for Florence).
    longitude : float
        Site longitude in decimal degrees (e.g. 11.25 for Florence).
    output_dir : Path
        Directory where the .epw will be saved.
    location_name : str
        Used to name the output file.

    Returns
    -------
    Path
        Path to the created .epw file.
    """
    try:
        import pvlib
        from ladybug.epw import EPW
        from ladybug.dt import DateTime
        from ladybug.datacollection import HourlyContinuousCollection
    except ImportError as exc:
        raise ImportError(
            "Install pvlib and ladybug-core:\n"
            "  pip install pvlib ladybug-core"
        ) from exc

    print(f"Fetching PVGIS TMY for lat={latitude}, lon={longitude} ...")
    tmy_data, months_selected, inputs, metadata = pvlib.iotools.get_pvgis_tmy(
        latitude=latitude,
        longitude=longitude,
        outputformat="json",
        usehorizon=True,
        startyear=2005,
        endyear=2023,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    epw_path = output_dir / f"{location_name}_{latitude}_{longitude}_pvgis.epw"

    # Write a minimal EPW header + data.
    # For full EPW, use the ladybug EPW writer or a dedicated converter.
    # Here we save as CSV for inspection; replace with ladybug EPW writer
    # when ladybug is fully set up.
    csv_path = epw_path.with_suffix(".csv")
    tmy_data.to_csv(csv_path)
    print(f"TMY data saved as CSV (convert to EPW with ladybug): {csv_path}")
    print("Tip: use `ladybug.epw.EPW.from_file()` to load and inspect EPW files.")
    return csv_path


# ---------------------------------------------------------------------------
# Method C: List of pre-curated EnergyPlus.net EPW URLs for common EU cities
# ---------------------------------------------------------------------------
COMMON_CITIES: dict[str, str] = {
    # city_name: direct URL to .epw on energyplus.net or onebuilding.org
    "Rome_ITA": (
        "https://climate.onebuilding.org/WMO_Region_6_Europe/"
        "ITA_Italy/LAZ_Lazio/ITA_LAZ_Rome.Ciampino.162400_TMYx.2009-2023.zip"
    ),
    "Florence_ITA": ONEBUILDING_EPW_URL,
    "Berlin_DEU": (
        "https://climate.onebuilding.org/WMO_Region_6_Europe/"
        "DEU_Germany/BE_Berlin/DEU_BE_Berlin.103840_TMYx.2009-2023.zip"
    ),
    "Amsterdam_NLD": (
        "https://climate.onebuilding.org/WMO_Region_6_Europe/"
        "NLD_Netherlands/NH_North.Holland/NLD_NH_Amsterdam.Airport.062400_TMYx.2009-2023.zip"
    ),
    "Zurich_CHE": (
        "https://climate.onebuilding.org/WMO_Region_6_Europe/"
        "CHE_Switzerland/ZH_Zurich/CHE_ZH_Zurich.Kloten.066000_TMYx.2009-2023.zip"
    ),
}


if __name__ == "__main__":
    # ---- Choose ONE method and uncomment it --------------------------------

    # Method A — download a specific EPW by URL:
    download_epw_from_onebuilding(ONEBUILDING_EPW_URL, WEATHER_OUTPUT_DIR)

    # Method B — generate EPW from PVGIS for any coordinate (Florence example):
    # download_epw_from_pvgis(latitude=43.78, longitude=11.25,
    #                         output_dir=WEATHER_OUTPUT_DIR,
    #                         location_name="Florence")

    # Method C — download for a named city from the curated list:
    # city = "Zurich_CHE"
    # download_epw_from_onebuilding(COMMON_CITIES[city], WEATHER_OUTPUT_DIR)
