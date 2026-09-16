from datetime import date, timedelta
import csv
from skyfield.api import load, wgs84
from skyfield import almanac
from skyfield.units import Angle
from skyfield.earthlib import refraction
from numpy import arccos
import pandas as pd
import math

ts = load.timescale()
eph = load('de440s.bsp')
earth, sun, moon = eph['earth'], eph['sun'], eph['moon']

def tabledata(lat, lon, ele, tz, year, m, d, csv_filename="crescent_data.csv"):


    # Observer (works across Skyfield versions)
    try:
        location = wgs84.latlon(lat, lon, elevation_m=ele, center=earth)
    except TypeError:
        location = earth + wgs84.latlon(lat, lon, elevation_m=ele)

    # Local-day window in UTC
    t0 = ts.utc(year, m, d, 0 - tz, 0, 0)
    t1 = ts.utc(year, m, d, 24 - tz, 0, 0)

    # Apparent horizon for upper-limb sunset, with height & refraction
    earth_radius_m = 6378136.6
    side_over_hyp = earth_radius_m / (earth_radius_m + ele)
    h_geom = Angle(radians=-arccos(side_over_hyp))           # dip from observer height
    r = refraction(0.0, temperature_C=15.0, pressure_mbar=1013.25)
    solar_radius_deg = 16/60
    horizon_deg = -r + h_geom.degrees - solar_radius_deg

    # Sunset within the local-day window    
    set_times_sun, _ = almanac.find_settings(location, sun, t0, t1, horizon_degrees=horizon_deg)
    if len(set_times_sun) == 0:
        raise RuntimeError("No sunset found in this local-day window.")
    t_sunset = set_times_sun[0]
    dt_sunset_local = t_sunset.utc_datetime() + timedelta(hours=tz)
    sunset_str = dt_sunset_local.strftime("%H:%M:%S")

    # Moonset within the local-day window (may be missing)
    set_times_moon, _ = almanac.find_settings(location, moon, t0, t1, horizon_degrees=horizon_deg)
    if len(set_times_moon) == 0:
        t_moonset = None
        moonset_str = "—"
        lag_str = "—"
    else:
        t_moonset = set_times_moon[0]
        dt_moonset_local = t_moonset.utc_datetime() + timedelta(hours=tz)
        moonset_str = dt_moonset_local.strftime("%H:%M:%S")

        # Lag = moonset - sunset (ensure positive same-evening)
        lag_td = (t_moonset.utc_datetime() - t_sunset.utc_datetime())
        if lag_td.total_seconds() < 0:
            lag_td += timedelta(days=1)
        hh = int(lag_td.total_seconds() // 3600)
        mm = int((lag_td.total_seconds() % 3600) // 60)
        ss = int(lag_td.total_seconds() % 60)
        lag_str = f"{hh:02d}:{mm:02d}:{ss:02d}"

    # Alt/Az at actual sunset
    alt_moon, az_moon, _ = location.at(t_sunset).observe(moon).apparent().altaz()
    alt_sun,  az_sun,  _ = location.at(t_sunset).observe(sun).apparent().altaz()

    moon_alt_deg = float(alt_moon.degrees)
    daz_deg = abs(float(az_moon.degrees) - float(az_sun.degrees))
    arcv_deg = abs(moon_alt_deg - float(alt_sun.degrees))    # Arc of Vision
    arcl_deg = float(
        location.at(t_sunset).observe(sun).apparent()
        .separation_from(location.at(t_sunset).observe(moon).apparent()).degrees
    )  # Arc of Light

    # Moon age at sunset: (JD_sunset - JD_conjunction_before)*24
    jd_sunset = t_sunset.tt
    # Search ±5 days around date; pick last conjunction BEFORE sunset
    t0c = ts.utc(year, m, d - 5)
    t1c = ts.utc(year, m, d + 5)
    oc_func = almanac.oppositions_conjunctions(eph, eph['Moon'])
    times_oc, events_oc = almanac.find_discrete(t0c, t1c, oc_func)
    jd_conj = None
    for ti, ei in zip(times_oc, events_oc):
        if ei == 1 and ti.tt <= jd_sunset:  # 1 = conjunction
            jd_conj = ti.tt
    moon_age_hours = (jd_sunset - jd_conj) * 24.0 if jd_conj is not None else float('nan')

    # Build row
    date_str = date(year, m, d).strftime("%Y-%m-%d")
    header = ["Date", "Sunset", "Moonset", "Lag Time", "Moon Age", "Moon Alt", "DAZ", "ArcV", "ArcL"]
    row = [
        date_str,
        sunset_str,
        moonset_str,
        lag_str,
        f"{moon_age_hours:.2f}",
        f"{moon_alt_deg:.2f}",
        f"{daz_deg:.2f}",
        f"{arcv_deg:.2f}",
        f"{arcl_deg:.2f}",
    ]

    # Pretty print
    print("\n+------------+----------+----------+----------+----------+----------+----------+----------+----------+")
    print("|    Date    |  Sunset  |  Moonset | LagTime  | MoonAge  | MoonAlt  |   DAZ    |   ArcV   |   ArcL   |")
    print("+------------+----------+----------+----------+----------+----------+----------+----------+----------+")
    print(f"| {date_str} | {sunset_str:8} | {moonset_str:8} | {lag_str:8} | "
          f"{moon_age_hours:8.2f} | {moon_alt_deg:8.2f} | {daz_deg:8.2f} | {arcv_deg:8.2f} | {arcl_deg:8.2f} |")
    print("+------------+----------+----------+----------+----------+----------+----------+----------+----------+")

    # Save CSV
    with open(csv_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(row)

    print(f"\n✅ Saved to CSV file: {csv_filename}")

    return {
        "Date": date_str,
        "Sunset": sunset_str,
        "Moonset": moonset_str,
        "Lag Time": lag_str,
        "Moon Age (h)": f"{moon_age_hours:.2f}",
        "Moon Alt (deg)": f"{moon_alt_deg:.2f}",
        "DAZ (deg)": f"{daz_deg:.2f}",
        "ArcV (deg)": f"{arcv_deg:.2f}",
        "ArcL (deg)": f"{arcl_deg:.2f}",
    }

from datetime import date, timedelta
import csv
from skyfield.api import load, wgs84
from skyfield import almanac
from skyfield.units import Angle
from skyfield.earthlib import refraction
from numpy import arccos

ts = load.timescale()
eph = load('de440s.bsp')
earth, sun, moon = eph['earth'], eph['sun'], eph['moon']

def observedata(lat, lon, ele, tz, year, m, d):


    # Observer (works across Skyfield versions)
    try:
        location = wgs84.latlon(lat, lon, elevation_m=ele, center=earth)
    except TypeError:
        location = earth + wgs84.latlon(lat, lon, elevation_m=ele)

    # Local-day window in UTC
    t0 = ts.utc(year, m, d, 0 - tz, 0, 0)
    t1 = ts.utc(year, m, d, 24 - tz, 0, 0)

    # Apparent horizon for upper-limb sunset, with height & refraction
    earth_radius_m = 6378136.6
    side_over_hyp = earth_radius_m / (earth_radius_m + ele)
    h_geom = Angle(radians=-arccos(side_over_hyp))           # dip from observer height
    r = refraction(0.0, temperature_C=15.0, pressure_mbar=1013.25)
    solar_radius_deg = 16/60
    horizon_deg = -r + h_geom.degrees - solar_radius_deg

    # Sunset within the local-day window
    set_times_sun, _ = almanac.find_settings(location, sun, t0, t1, horizon_degrees=horizon_deg)
    if len(set_times_sun) == 0:
        raise RuntimeError("No sunset found in this local-day window.")
    t_sunset = set_times_sun[0]
    dt_sunset_local = t_sunset.utc_datetime() + timedelta(hours=tz)
    sunset_str = dt_sunset_local.strftime("%H:%M:%S")

    # Moonset within the local-day window (may be missing)
    set_times_moon, _ = almanac.find_settings(location, moon, t0, t1, horizon_degrees=horizon_deg)
    if len(set_times_moon) == 0:
        t_moonset = None
        moonset_str = "—"
        lag_str = "—"
    else:
        t_moonset = set_times_moon[0]
        dt_moonset_local = t_moonset.utc_datetime() + timedelta(hours=tz)
        moonset_str = dt_moonset_local.strftime("%H:%M:%S")

        # Lag = moonset - sunset (ensure positive same-evening)
        lag_time = (t_moonset.utc_datetime() - t_sunset.utc_datetime())



    # Alt/Az at actual sunset
    alt_moon, az_moon, _ = location.at(t_sunset).observe(moon).apparent().altaz()
    alt_sun,  az_sun,  _ = location.at(t_sunset).observe(sun).apparent().altaz()

    moon_alt_deg = float(alt_moon.degrees)
    daz_deg = abs(float(az_moon.degrees) - float(az_sun.degrees))
    arcv_deg = abs(moon_alt_deg - float(alt_sun.degrees))    # Arc of Vision
    arcl_deg = float(
        location.at(t_sunset).observe(sun).apparent()
        .separation_from(location.at(t_sunset).observe(moon).apparent()).degrees
    )  # Arc of Light

    # Moon age at sunset: (JD_sunset - JD_conjunction_before)*24
    jd_sunset = t_sunset.tt
    # Search ±5 days around date; pick last conjunction BEFORE sunset
    t0c = ts.utc(year, m, d - 5)
    t1c = ts.utc(year, m, d + 5)
    oc_func = almanac.oppositions_conjunctions(eph, eph['Moon'])
    times_oc, events_oc = almanac.find_discrete(t0c, t1c, oc_func)
    jd_conj = None
    for ti, ei in zip(times_oc, events_oc):
        if ei == 1 and ti.tt <= jd_sunset:  # 1 = conjunction
            jd_conj = ti.tt
    moon_age_hours = (jd_sunset - jd_conj) * 24.0 if jd_conj is not None else float('nan')

    # --- ADDED: Crescent Width Calculation ---
    moon_dist_km = location.at(t_sunset).observe(moon).apparent().distance().km
    moon_radius_km = 1737.4

    # Semidiameter
    sd_deg = math.degrees(math.asin(moon_radius_km / moon_dist_km))

    # Width = SD * (1 - cos(ArcL))
    width_deg = sd_deg * (1 - math.cos(math.radians(arcl_deg)))

    width_arcm = width_deg * 60.0
    width_arcs = width_deg * 3600.0

    return  sunset_str, moonset_str, lag_time,moon_age_hours,moon_alt_deg, daz_deg,arcv_deg,arcl_deg,width_arcm,width_arcs

def criteriavisibility ( lat, lon, ele, tz, year, m, d):

  sunset_str, moonset_str, lag_time,moon_age_hours,moon_alt_deg, daz,arcv,arcl,width_arcm,width_arcs = observedata(lat, lon, ele, tz, year, m, d)
  #print(arcl_deg)
  arcl_deg = arcl
  # List to store results
  results = []

  # Function to append results to the list
  def append_result(kriteria, expression, arcv_cerapan, arcv_kriteria, visibility):

    results.append({
        "Kriteria": kriteria,
        "Expression": expression,
        "Observation Value": arcv_cerapan,
        "Criterion Value": arcv_kriteria,
        "Visibility": visibility
    })
  v="Visible"
  i = "Not Visibile"
  # a. Kriteria Fotheringham
  kriteria = "Fotheringham"
  expression = "ARCV = 12.0 - 0.008 DAZ"
  fotheringham_arcv = float(12.0 - 0.008 * daz)

  visibility = i if fotheringham_arcv >= arcv else v
  append_result(kriteria, expression, arcv, fotheringham_arcv, visibility)

  # b. Kriteria Maunder
  kriteria = "Maunder"
  expression = "ARCV = 11 - 0.005*daz - 0.01*daz**2"
  maunder_arcv =  float(11 - 0.005*daz - 0.01*daz**2)

  visibility = i if maunder_arcv >= arcv else v
  append_result(kriteria, expression, arcv, maunder_arcv, visibility)

  # c. Kriteria Ilyas
  kriteria = "Ilyas"
  expression = "ARCV = -0.0027356815*daz - 0.0136648716*daz**2 + 0.0002119205*daz**3 + 10.2832719598"
  ilyas_arcv = float(-0.0027356815 * daz - 0.0136648716 * daz**2 + 0.0002119205 * daz**3 + 10.2832719598)

  visibility = i if ilyas_arcv >= arcv else v
  append_result(kriteria, expression, arcv, ilyas_arcv, visibility)

  # d. Kriteria Fatoohi
  kriteria = "Fatoohi"
  expression = "ARCV = 9.2714-0.0644*daz-0.0058*daz**2 + 0.0002*daz**3"
  fatoohi_arcv = float(9.2714 - 0.0644 * daz - 0.0058 * daz**2 + 0.0002 * daz**3)

  visibility = i if fatoohi_arcv >= arcv else v
  append_result(kriteria, expression, arcv, fatoohi_arcv, visibility)

  # e. Kriteria Krauss
  kriteria = "Krauss"
  expression = "ARCV = 0.0291254840*daz - 0.0098347831*daz**2 + 0.0000475196*daz**3 + 10.5981838905"
  krauss_arcv = float(0.0291254840 * daz - 0.0098347831 * daz**2 + 0.0000475196 * daz**3 + 10.5981838905)

  visibility = i if krauss_arcv >= arcv else v
  append_result(kriteria, expression, arcv, krauss_arcv, visibility)

  # f. Kriteria Faid Naked Eye
  kriteria = "Faid et.al (2024) Mata Kasar"
  expression = "ARCV = -0.09222*DAZ - 0.00629*DAZ^2 + 0.0002078*DAZ^3 + 6.792"
  faidne_arcv = float(-0.09222 * daz - 0.00629 * daz**2 + 0.0002078 * daz**3 + 6.792)

  visibility = i  if faidne_arcv >= arcv else v
  append_result(kriteria, expression, arcv, faidne_arcv, visibility)

  # g. Kriteria Faid CCD Imaging
  kriteria = "Faid et.al (2024) Optical Aid"
  expression = "ARCV = -1.3590*DAZ + 0.081710*DAZ^2 - 0.0015330*DAZ^3 + 7.391"
  faidCCD_arcv = float(-1.3590 * daz + 0.081710 * daz**2 - 0.0015330 * daz**3 + 7.391)

  visibility = i if faidCCD_arcv >= arcv else v
  append_result(kriteria, expression, arcv, faidCCD_arcv, visibility)

   #a. Kriteria MABIMS
  kriteria = "MABIMS 1995"
  expression = "ArcL ≥ 3° & MAlt ≥ 2°"
  k_arcl = 3  # Arc Length Criterion
  k_malt = 2  # Moon Altitude Criterion
  obs_string = f"{arcl:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Check visibility based on Nawawi's criteria
  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # b. Kriteria MABIMS 2021
  kriteria = "MABIMS 2021"
  expression = "ArcL ≥ 6.4° & MAlt ≥ 3°"
  k_arcl = 6.4  # Arc Length Criterion
  k_malt = 3  # Moon Altitude Criterion

  # Check visibility based on Nawawi's criteria
  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # c. Kriteria Istanbul 2015
  kriteria = "Istanbul 2015"
  expression = "ArcL ≥ 8° & MAlt ≥ 5°"
  k_arcl = 8  # Arc Length Criterion
  k_malt = 5  # Moon Altitude Criterion

  # Check visibility based on Nawawi's criteria
  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # d. Kriteria Danjon
  kriteria = "Danjon"
  expression = "ArcL ≥ 7° "
  k_arcl = 7  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  # Check visibility based on Nawawi's criteria
  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # e. Kriteria Ilyas Elongation
  kriteria = "Ilyas"
  expression = "ArcL ≥ 10.5° "
  k_arcl = 10.5  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  # Check visibility based on Nawawi's criteria
  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # f. Kriteria McNally
  kriteria = "McNally"
  expression = "ArcL ≥ 5° "
  k_arcl = 5  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  # Check visibility based on Nawawi's criteria
  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # g. Kriteria McNally
  kriteria = "Amir Hasanzadeh"
  expression = "ArcL ≥ 5° "
  k_arcl = 5  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  # Check visibility based on Nawawi's criteria
  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # g. Kriteria Sultan
  kriteria = "Sultan"
  expression = "ArcL ≥ 5° "
  k_arcl = 5  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # g. Kriteria Schaefer
  kriteria = "Schaefer"
  expression = "ArcL ≥ 7.5° "
  k_arcl = 7.5  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # h. Kriteria Fatoohi
  kriteria = "Fatoohi"
  expression = "ArcL ≥ 7.5° "
  k_arcl = 7.5  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # i. Kriteria Odeh
  kriteria = "Odeh"
  expression = "ArcL ≥ 6.4° "
  k_arcl = 6.4  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # i. Kriteria Odeh
  kriteria = "Odeh"
  expression = "ArcL ≥ 6.4° "
  k_arcl = 6.4  # Arc Length Criterion
  k_malt = 0  # Moon Altitude Criterion

  visibility = i if (k_arcl > arcl or k_malt > moon_alt_deg) else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"

  # Append the result
  append_result(kriteria, expression, obs_string, criterion_string, visibility)

  # j. Kriteria Faid Naked Eye
  kriteria = "Faid Naked Eye"
  expression = "MAlt = − 0.3351 ArcL + 0.0023 ArcL2 + 0.000064 ArcL3 + 7.78"
  faidne_malt = float(- 0.3351 * arcl + 0.0023 * arcl**2 + 0.000064 * arcl**3 + 7.78)

  visibility = i if faidne_arcv >= moon_alt_deg else v
  obs_string = f"{arcl_deg:.2f}, {moon_alt_deg:.2f}" # "12.45, 4.50"
  criterion_string = f"{k_arcl}, {k_malt}" # "12.45, 4.50"
  append_result(kriteria, expression, obs_string, criterion_string, visibility)


  # a. Kriteria Yallop
  kriteria = "Yallop Q1 (Lunar Crescent Easily Visible)"
  expression = "ArcV =- 0.1018*W^3 +0.7319*W^2 -6.3226*W + 13.9971"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 13.9971)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # b. Kriteria Yallop
  kriteria = "Yallop Q2 (Lunar Crescent Visibile Under Perfect Condition)"
  expression = "ArcV =- 0.1018W3 +0.7319W2 -6.3226W' + 11.6971"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 11.6971)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # c. Kriteria Yallop
  kriteria = "Yallop Q3 (May Need Optical Aid to Find Crescent)"
  expression = "ArcV =- 0.1018W3 +0.7319W2 -6.3226W' + 10.2371"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 10.2371)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # d. Kriteria Yallop
  kriteria = "Yallop Q4 (Will Need Optical Aid to Find Crescent)"
  expression = "ArcV =- 0.1018W3 +0.7319W2 -6.3226W' + 9.5171"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 9.5171)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # e. Kriteria Yallop
  kriteria = "Yallop Q5 (Not visible with a telescope)"
  expression = "ArcV =- 0.1018W3 +0.7319W2 -6.3226W' + 8.9071"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 8.9071)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Yallop
  kriteria = "Yallop Q6 (Not visible, below Danjon limit)"
  expression = "ArcV =- 0.1018W3 +0.7319W2 -6.3226W' + 8.9071"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 8.9071)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Odeh
  kriteria = "Odeh V1 (Crescent is visible by naked eyes)"
  expression = "ArcV =- 0.1018W3 +0.7319W^2 -6.3226W' + 12.8151"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 12.8151)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Odeh
  kriteria = "Odeh V2 (Crescent is visible by optical aid, and it could be seen by naked eyes)"
  expression = "ArcV =- 0.1018W^3 +0.7319W^2 -6.3226W' + 9.1651"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm + 9.1651)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Odeh
  kriteria = "Odeh V3 (Crescent is visible by optical aid only)"
  expression = "ArcV =- 0.1018W^3 +0.7319W^2 -6.3226W' +  6.2051"
  kriteria_arcv_w = float(- 0.1018*width_arcm**3 +0.7319*width_arcm**2 -6.3226*width_arcm +  6.2051)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Alrefay
  kriteria = "Alrefay v1 (Visible by Naked Eye)"
  expression = "ArcV =− 1.01W^3 +3.3W^2 − 4.51W +  9.34"
  kriteria_arcv_w = float(- 1.01*width_arcm**3 +3.3*width_arcm**2 + -4.51*width_arcm +  9.34)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Alrefay
  kriteria = "Alrefay v2 (Visible by Optical Aided Only)"
  expression = "ArcV =− 1.02W^3 +3.22W^2 − 4.35W +  7.83"
  kriteria_arcv_w = float(- 1.02*width_arcm**3 +3.22*width_arcm**2 + -4.35*width_arcm +  7.83)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Faid
  kriteria = "Faid v1 (Visible by Naked Eye))"
  expression = "ArcV = − 0.2387791499 W + 0.0053517999 W2 − 0.0000422340 W3 + 7.9662653619"
  kriteria_arcv_w = float(- 0.0000422340*width_arcm**3 ++ 0.0053517999 *width_arcm**2 + - 0.2387791499*width_arcm +  7.9662653619)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Faid
  kriteria = "Faid v2 (Visible by CCD Imaging Only))"
  expression = "ArcV = − 0.2372 W + 0.0064324 W2 − 0.0000523 W3 + 2.957"
  kriteria_arcv_w = float(-  0.2372*width_arcm**3 + 0.0064324 *width_arcm**2 + - 0.0000523*width_arcm +  2.957)

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

  # Kriteria Faid
  kriteria = "Bruin"
  expression = "ArcV =11.5621745317 − 7.944238328 W + 3.2608487770 W2 − 0.4559413249 W3"
  kriteria_arcv_w = float(-0.4559413249*width_arcm**3 + 3.2608487770 *width_arcm**2 + - 7.944238328*width_arcm +  11.5621745317 )

  visibility = i if kriteria_arcv_w  >= arcv else v
  append_result(kriteria, expression, arcv, kriteria_arcv_w , visibility)

    # Convert the timedelta object to total minutes (float)
  lag_time = lag_time.total_seconds() / 60.0

  # Kriteria Caldwell
  kriteria = "Caldwell (Naked Eye Visible)"
  expression = "lag (min) = − 0.9709 ArcL + 44.65"
  kriteria_lt = float(-0.9709*arcl + 44.65)

  visibility = i if kriteria_lt  >= lag_time else v
  append_result(kriteria, expression, lag_time, kriteria_lt , visibility)

  # Kriteria Caldwell
  kriteria = "Caldwell (Only Optical Aided Visible)"
  expression = "lag (min) =  − 1.9230 ArcL + 43.13 "
  kriteria_lt = float(- 1.9230*arcl + 43.13)

  visibility = i if kriteria_lt  >= lag_time else v
  append_result(kriteria, expression, lag_time, kriteria_lt , visibility)

  # Kriteria Gautchy
  kriteria = "Gautchy "
  expression = "lag (min) =  0.3342328913 DAZ + − 0.0715608980 DAZ2 + 0.0009924422 DAZ3 + 33.8890455442  "
  kriteria_lt = float(0.3342328913 * daz + - 0.0715608980 * daz**2 + 0.0009924422* daz**3 + 33.8890455442 )

  visibility = i if kriteria_lt  >= lag_time else v
  append_result(kriteria, expression, lag_time, kriteria_lt , visibility)


  # Create DataFrame
  df = pd.DataFrame(results)

  # Display the DataFrame
  print(df)

  csv_path = 'kriteria_arcv_vs_daz.csv'
  df.to_csv(csv_path, index=False)

  return df


import io
import math
import urllib.request
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

from skyfield.api import load, wgs84, N, E
from skyfield import almanac


def _resolve_image(image_input, mode='RGB'):
    if image_input is None:
        return None
    if isinstance(image_input, np.ndarray):
        return image_input
    if isinstance(image_input, Image.Image):
        return np.array(image_input.convert(mode))
    if isinstance(image_input, str):
        if image_input.startswith(('http://', 'https://')):
            req = urllib.request.Request(image_input, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                img_data = resp.read()
            return np.array(Image.open(io.BytesIO(img_data)).convert(mode))
        return np.array(Image.open(image_input).convert(mode))
    raise ValueError(f"Unsupported image input type: {type(image_input)}")


def moonpositionanalysis(
    year, month, day, tz, lat, long, ele,
    IMAGE_PATH=None,
    horizon_y_ratio=0.50,       # Fraction from bottom of image to the sea horizon (0.0 to 1.0)
    horizon_alt_target=-0.83,   # Altitude where the sea horizon line should sit (default: sunset sun altitude)
    y_max=25,
    img_center_az=270,
    img_fov=65,
    duration_years=1            # Number of years to simulate (1 to 19)
):
    ts = load.timescale()
    try:
        eph = load('de440s.bsp')
    except Exception:
        eph = load('de421.bsp')

    def parameter_calculator(c_year, c_month, c_day, c_tz):
        location = wgs84.latlon(lat * N, long * E, elevation_m=ele)
        observer = eph['Earth'] + location
        sun, moon = eph['sun'], eph['moon']

        t0 = ts.utc(c_year, c_month, c_day)
        t1 = ts.utc(c_year, c_month, c_day + 1)

        t, y = almanac.find_settings(observer, sun, t0, t1)
        if len(t) == 0:
            return 0, 0, 0, 0, 0

        t_sunset = t[0]

        sun_obs = observer.at(t_sunset).observe(sun).apparent()
        moon_obs = observer.at(t_sunset).observe(moon).apparent()

        sun_alt, sun_az, _ = sun_obs.altaz()
        moon_alt, moon_az, _ = moon_obs.altaz()
        elongation = sun_obs.separation_from(moon_obs).degrees

        return (
            elongation,
            moon_alt.degrees,
            sun_alt.degrees,
            sun_az.degrees,
            moon_az.degrees,
        )

    def generate_hijri_calendar():
        start_date = datetime(year, month, day)
        h_day = 22
        h_month = 7
        h_year = 1448

        duration_days = 365 * duration_years

        LIMIT_ALT = 3.0
        LIMIT_ELONG = 6.4

        nama_bulan_hijri = [
            "Muharram", "Safar", "Rabiulawal", "Rabiulakhir",
            "Jamadilawal", "Jamadilakhir", "Rejab", "Syaaban",
            "Ramadan", "Syawal", "Zulkaedah", "Zulhijah",
        ]

        data = []
        current_date = start_date

        for _ in tqdm(range(duration_days), desc="Simulating Calendar"):
            row = {
                "Gregorian": current_date.strftime("%Y-%m-%d"),
                "Hijri Day": h_day,
                "Hijri Month": nama_bulan_hijri[h_month - 1],
                "Hijri Year": h_year,
                "Elongation": None,
                "Moon Alt": None,
                "Sun Alt": None,
                "Sun Az": None,
                "Moon Az": None,
                "Status": "Normal",
            }

            next_h_day = h_day + 1
            next_h_month = h_month
            next_h_year = h_year

            if h_day == 29:
                elong, m_alt, s_alt, s_az, m_az = parameter_calculator(
                    current_date.year, current_date.month, current_date.day, tz
                )

                row["Elongation"] = round(elong, 2)
                row["Moon Alt"] = round(m_alt, 2)
                row["Sun Alt"] = round(s_alt, 3)
                row["Sun Az"] = round(s_az, 2)
                row["Moon Az"] = round(m_az, 2)

                if m_alt > LIMIT_ALT and elong > LIMIT_ELONG:
                    next_h_day = 1
                    next_h_month += 1
                    row["Status"] = "New Moon Visible (End 29)"
                else:
                    next_h_day = 30
                    row["Status"] = "Not Visible (Extend to 30)"

            elif h_day == 30:
                next_h_day = 1
                next_h_month += 1
                row["Status"] = "End of Month (30)"

            if next_h_month > 12:
                next_h_month = 1
                next_h_year += 1

            data.append(row)

            h_day = next_h_day
            h_month = next_h_month
            h_year = next_h_year
            current_date += timedelta(days=1)

        return pd.DataFrame(data)

    df = generate_hijri_calendar()
    obs_days = df[df['Hijri Day'] == 29].copy()

    # Dynamic calculation of bounds so sea horizon is pinned precisely
    x_min = img_center_az - (img_fov / 2)
    x_max = img_center_az + (img_fov / 2)

    # Calculate image extent based on horizon_y_ratio
    # If horizon is at horizon_y_ratio (from bottom) and should match horizon_alt_target:
    total_vert_span = (y_max - horizon_alt_target) / (1.0 - horizon_y_ratio)
    img_bottom_deg = y_max - total_vert_span

    extent = [x_min, x_max, img_bottom_deg, y_max]

    fig, ax = plt.subplots(figsize=(14, 8), dpi=120)

    img_arr = None
    if IMAGE_PATH is not None:
        try:
            img_arr = _resolve_image(IMAGE_PATH, mode='RGB')
            ax.imshow(img_arr, extent=extent, aspect='auto', zorder=0)
        except Exception as e:
            print(f"Warning: Could not load image from '{IMAGE_PATH}': {e}. Generating sunset gradient.")
            img_arr = None

    if img_arr is None:
        nodes = [
            (0.0, '#001133'),
            (horizon_y_ratio - 0.01, '#001133'),
            (horizon_y_ratio, '#FF4500'),
            (min(1.0, horizon_y_ratio + 0.15), '#FF8C00'),
            (min(1.0, horizon_y_ratio + 0.35), '#FFD700'),
            (1.0, '#87CEEB'),
        ]
        sunset_cmap = mcolors.LinearSegmentedColormap.from_list("SimulatedSunset", nodes)
        gradient = np.linspace(0, 1, 500).reshape(-1, 1)
        ax.imshow(gradient, extent=extent, aspect='auto', cmap=sunset_cmap, origin='lower', zorder=0)

    LIMIT_ALT = 3.0
    LIMIT_ELONG = 6.4

    total_moons = len(obs_days)
    above_criteria_count = len(obs_days[(obs_days['Moon Alt'] > LIMIT_ALT) & (obs_days['Elongation'] > LIMIT_ELONG)])
    below_criteria_count = total_moons - above_criteria_count

    pct_above = (above_criteria_count / total_moons) * 100 if total_moons > 0 else 0
    pct_below = (below_criteria_count / total_moons) * 100 if total_moons > 0 else 0

    # True Horizon Line (0°)
    ax.axhline(0, color='white', linestyle='-', linewidth=1.2, alpha=0.6)

    # Plot Sun (Sits at ~ -0.83°, right along the sea horizon)
    ax.scatter(obs_days['Sun Az'], obs_days['Sun Alt'],
               c='orange', s=160, marker='o', edgecolors='red', linewidth=1.5, zorder=2)

    # Plot Moons
    colors = [
        '#00FF00' if (r['Moon Alt'] > LIMIT_ALT and r['Elongation'] > LIMIT_ELONG) else '#CCCCCC'
        for _, r in obs_days.iterrows()
    ]
    ax.scatter(obs_days['Moon Az'], obs_days['Moon Alt'],
               c=colors, s=90, marker='o', edgecolors='black', linewidth=1, zorder=3)

    for _, row in obs_days.iterrows():
        ax.plot([row['Sun Az'], row['Moon Az']], [row['Sun Alt'], row['Moon Alt']],
                color='white', linestyle=':', linewidth=0.8, alpha=0.5)

    ax.set_title('Sun & Moon at Sunset: Horizon Simulation', color='black', fontsize=14, fontweight='bold')
    ax.set_xlabel('Azimuth (Compass Direction)', fontsize=12)
    ax.set_ylabel('Altitude (Degrees)', fontsize=12)

    legend_handles = [
        mpatches.Patch(facecolor='#00FF00', edgecolor='black', label=f'Moon Above Criteria: {pct_above:.1f}%'),
        mpatches.Patch(facecolor='#CCCCCC', edgecolor='black', label=f'Moon Below Criteria: {pct_below:.1f}%'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markeredgecolor='red', markersize=10, label='Sun (Sunset ~ -0.83°)'),
        plt.Line2D([0], [0], color='white', lw=1.2, label='True Horizon (0°)'),
    ]
    ax.legend(handles=legend_handles, loc='upper left', frameon=True, framealpha=0.85, fontsize=10)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(img_bottom_deg, y_max)

    ax.text(270, img_bottom_deg + 1, 'WEST (270°)', color='yellow', fontsize=12,
            ha='center', fontweight='bold', bbox=dict(facecolor='black', alpha=0.35))

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    img.load()
    buf.close()
    plt.close(fig)

    return img

import io
import os
import csv
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from skyfield.api import load, wgs84, Topos
from skyfield.earthlib import refraction
from skyfield.units import Angle
from skyfield.almanac import find_settings
from numpy import arccos


def visibilitycontrast(lat, long, year, month, day, ele, tz, temperature_celcius, relative_humidity, light_pollution_magsec, location):
    direction_obs = "N"
    lokasi = location

    # --- Initialization ---
    ts = load.timescale()
    try:
        eph = load('de440s.bsp')
    except Exception:
        eph = load('de421.bsp')

    earth, sun, moon = eph['earth'], eph['sun'], eph['moon']

    # Define time range
    local_midnight = datetime(year, month, day, 0, 0, 0)
    t0_utc = local_midnight - timedelta(hours=tz)
    t1_utc = t0_utc + timedelta(days=1)

    t0 = ts.utc(t0_utc.year, t0_utc.month, t0_utc.day, t0_utc.hour, t0_utc.minute, t0_utc.second)
    t1 = ts.utc(t1_utc.year, t1_utc.month, t1_utc.day, t1_utc.hour, t1_utc.minute, t1_utc.second)

    # Calculate Horizon Dip based on elevation
    altitude_m = ele
    earth_radius_m = 6378136.6
    side_over_hypotenuse = earth_radius_m / (earth_radius_m + altitude_m)
    h = Angle(radians=-arccos(side_over_hypotenuse))

    # Standard solar radius approximation
    solar_radius_degrees = 16 / 60

    # --- Find Sunset ---
    observer_topo = earth + Topos(latitude_degrees=lat, longitude_degrees=long, elevation_m=ele)
    t, y = find_settings(observer_topo, sun, t0, t1, horizon_degrees=h.degrees - solar_radius_degrees)

    if not t:
        print("Sun does not set in this time range.")
        return None

    sunset_time_utc = t[0].utc_datetime()
    sunset_local = sunset_time_utc + timedelta(hours=tz)

    utc_x = (
        sunset_time_utc.year,
        sunset_time_utc.month,
        sunset_time_utc.day,
        sunset_time_utc.hour,
        sunset_time_utc.minute,
        sunset_time_utc.second
    )

    current_time_ts = ts.utc(*utc_x)
    moon_app = observer_topo.at(current_time_ts).observe(moon).apparent()
    moon_alt, _, _ = moon_app.altaz()

    data = []
    print(f"Sunset calculated at: {sunset_local} (Local)")
    print("Starting visibility calculation loop...")

    # --- Main Calculation Loop ---
    while moon_alt.degrees >= -1.0:
        current_time_ts = ts.utc(*utc_x)

        sun_astro = observer_topo.at(current_time_ts).observe(sun)
        sun_app = sun_astro.apparent()
        sun_alt, sun_az, sun_dist = sun_app.altaz()
        sun_ra, sun_dec, _ = sun_app.radec()

        moon_astro = observer_topo.at(current_time_ts).observe(moon)
        moon_app = moon_astro.apparent()
        moon_alt, moon_az, moon_dist = moon_app.altaz()

        if moon_alt.degrees < -1.0:
            break

        daz = abs(moon_az.degrees - sun_az.degrees)

        # 1. Geometry Calculations
        moon_earth_dist_km = (moon.at(current_time_ts) - earth.at(current_time_ts)).distance().km
        horizontal_parallax = math.degrees(math.asin(6378.14 / moon_earth_dist_km))

        moon_sun_distance_ratio = 0.272481
        semidiameter_geocentric = math.degrees(math.asin(moon_sun_distance_ratio * math.sin(math.radians(horizontal_parallax))))
        semidiameter_topocentric = semidiameter_geocentric * (1 + math.sin(math.radians(moon_alt.degrees)) * math.sin(math.radians(horizontal_parallax)))

        separation_angle = sun_app.separation_from(moon_app).degrees

        # 2. Phase Angle
        moon_sun_vector = eph['moon'].at(current_time_ts) - eph['sun'].at(current_time_ts)
        moon_sun_dist_km = moon_sun_vector.distance().km
        sun_earth_dist_km = sun_dist.km

        arcl_rad = math.radians(separation_angle)
        denom = sun_earth_dist_km - moon_sun_dist_km * math.cos(arcl_rad)
        if denom == 0: 
            denom = 1e-9

        phase_angle = 180 + math.degrees(math.atan((moon_sun_dist_km * math.sin(arcl_rad)) / denom))

        # 3. Illuminated Fraction
        k_frac = (1 + math.cos(math.radians(phase_angle))) / 2
        moon_area = math.pi * semidiameter_topocentric**2
        ilum_area = k_frac * moon_area

        # 4. Moon Brightness (Extra-Atmospheric)
        m = -12.73 + 0.026 * phase_angle + 4 * 10**-9 * phase_angle**4

        if ilum_area <= 0:
            out_moonbrightness_mag = 999
        else:
            out_moonbrightness_s10 = (1 / ilum_area) * 2.51**(10 - m)
            if out_moonbrightness_s10 <= 0:
                out_moonbrightness_mag = 999
            else:
                out_moonbrightness_mag = -((math.log10(out_moonbrightness_s10)) * 2.5 - 26.33)

        # 5. Atmospheric Extinction (k)
        kr = 0.1066 * math.exp(-(ele) / 8200) * (0.031 / 0.55)**(-4)

        ke1 = 0.10 * (0.031 / 0.55)**-1.3
        ke2 = math.exp(-ele / 1500)
        ke3 = (1 - (0.32 / math.log(relative_humidity)))**(4/3) if relative_humidity > 0 and math.log(relative_humidity) != 0 else 1
        ke4 = 1 + 0.33 * math.sin(math.radians(sun_ra.hours * 15))
        ke = ke1 * ke2 * ke3 * ke4

        matara = float((sun_ra.hours * 15))
        ko1 = (lat * math.cos(math.radians(matara)) - math.cos(math.radians(3 * matara)))
        ko2 = 1 + 0.13 * ko1
        ko = 0.031 * ko2

        k_W = 0.0031 * 0.94 * relative_humidity * math.exp(temperature_celcius / 15) * math.exp(-ele / 8200)

        moon_zenith_dist = 90 - moon_alt.degrees
        rad_z = np.radians(min(moon_zenith_dist, 89.9))
        air_mass = (np.cos(rad_z) + 0.025 * np.exp(-11 * np.cos(rad_z)))**-1

        difmag = float(kr * air_mass)
        bulanmagket = out_moonbrightness_mag * 10**(-0.4 * difmag)

        # 7. Twilight Brightness
        tw1 = -(7.5 * (10**-5) * moon_zenith_dist + 5.05 * 10**-3) * daz
        tw2 = (3.67 * 10**-4 * moon_zenith_dist - 0.458) * -1 * (sun_alt.degrees)
        tw3 = (9.17 * 10**-3) * moon_zenith_dist + 3.525
        tw = tw1 + tw2 + tw3
        twmag1 = 10**tw
        twmag2 = 9.17 * 10**4 * twmag1
        tw_no_lightpollution = -(math.log10(twmag2) * 2.5 - 27.78)

        poly_a, poly_b = 319.186511755673, -46.9419919726453
        poly_c = 0.434369283318305
        poly_d, poly_e = 2.39138122541257, -0.00121311966265414
        poly_f, poly_g = -0.0488735671014705, -0.0396262989070584
        poly_h, poly_i = -0.000000928758741258742, 0.0000548215089277455
        poly_j = 0.001346675592325110

        dir_obs_val = 1 if direction_obs == "Y" else -1
        theta = dir_obs_val * moon_zenith_dist
        Zlp = light_pollution_magsec

        tw_lightpollution = (poly_a + poly_b*Zlp + poly_c*theta + poly_d*Zlp**2 +
                             poly_e*theta**2 + poly_f*Zlp*theta + poly_g*Zlp**3 +
                             poly_h*theta**3 + poly_i*Zlp*theta**2 + poly_j*Zlp**2*theta)

        twmag = min(tw_no_lightpollution, tw_lightpollution)

        # 8. Contrast Calculation
        moon_brightness_nL = 10**(-0.4 * (bulanmagket - 26.33))
        twilight_brightness_nL_raw = 10**(-0.4 * (twmag - 26.33))

        factor_nl = 1.0
        if light_pollution_magsec < 15:
            factor_nl = 5000 * (np.log10(100000 / (light_pollution_magsec + 1)))
        elif light_pollution_magsec < 16:
            factor_nl = 50 * (np.log10(1000 / (light_pollution_magsec + 1)))
        elif light_pollution_magsec < 18:
            factor_nl = 25 * (np.log10(1000 / (light_pollution_magsec + 1)))

        twilight_brightness_nL = twilight_brightness_nL_raw * factor_nl
        contrast_c = ((moon_brightness_nL - twilight_brightness_nL) / twilight_brightness_nL)

        # 9. Contrast Threshold
        twilight_brightness_cd_raw = 10**((12.58 - twmag) / 2.5)
        twilight_brightness_cd = twilight_brightness_cd_raw * factor_nl

        r1, r2 = 6.505 * 10**-4, -8.461 * 10**-4
        k1, k2 = 7.633 * 10**-3, -7.174 * 10**-3

        term1 = (r1 * twilight_brightness_cd**(-0.25) + r2)**2 / semidiameter_topocentric
        term2 = k1 * twilight_brightness_cd**(-0.25) + k2

        try:
            contrast_threshold = (term1**(0.6) + term2**(0.6))**(5/3)
        except Exception:
            contrast_threshold = 999

        if isinstance(contrast_threshold, complex) or math.isnan(contrast_threshold):
            contrast_threshold = 999

        visibility = "No" if contrast_c <= contrast_threshold else "Yes"

        utc_tz = datetime(*utc_x) + timedelta(hours=tz)
        time_str = utc_tz.strftime("%H:%M")

        data.append((time_str, twmag, contrast_c, contrast_threshold, visibility))

        utc_x_dt = datetime(*utc_x) + timedelta(minutes=1)
        utc_x = list(utc_x_dt.timetuple())[:6]

    # --- Save CSV ---
    csv_filename = "twilight_sky_brightness_results.csv"
    headers = ["Time", "Twilight Mag", "Contrast", "Contrast Threshold", "Visibility"]
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    df_v = pd.DataFrame(data, columns=headers)

    # --- Visibility Window Stats ---
    t_moonset, _ = find_settings(observer_topo, moon, t0, t1, horizon_degrees=-0.57)
    if t_moonset:
        moonset_time_utc = t_moonset[0].utc_datetime()
        moonset_local = moonset_time_utc + timedelta(hours=tz)
        minutes_sunset_to_moonset = int((moonset_local - sunset_local).total_seconds() / 60)
    else:
        moonset_local = "N/A"
        minutes_sunset_to_moonset = 0

    df_yes = df_v[df_v["Visibility"] == "Yes"].copy()
    duration = 0

    if not df_yes.empty:
        time1_str = df_yes["Time"].iloc[0]
        time2_str = df_yes["Time"].iloc[-1]

        def calc_delta(t_str):
            cur_time = datetime.strptime(t_str, "%H:%M").replace(
                year=sunset_local.year, month=sunset_local.month, day=sunset_local.day)
            if cur_time.hour < 12 and sunset_local.hour > 12:
                cur_time += timedelta(days=1)
            return int((cur_time - sunset_local.replace(tzinfo=None)).total_seconds() / 60)

        df_yes["Δt"] = df_yes["Time"].apply(calc_delta)
        duration = df_yes["Δt"].iloc[-1] - df_yes["Δt"].iloc[0] + 1
        vis_text = f"The lunar crescent will be visible from {time1_str} to {time2_str}."
    else:
        vis_text = "The lunar crescent will not be visible during this period."

    # --- Plotting to Memory Buffer ---
    df_plot = df_v.copy()
    df_plot["Datetime"] = pd.to_datetime(df_plot["Time"], format="%H:%M")

    fig, ax = plt.subplots(figsize=(12, 6), dpi=120)

    contrast_color = "#1f77b4"
    threshold_color = "#ff7f0e"

    ax.plot(df_plot["Datetime"], df_plot["Contrast"],
            label="Contrast (Moon/Sky)", color=contrast_color, linestyle='-', linewidth=2.5)
    ax.plot(df_plot["Datetime"], df_plot["Contrast Threshold"],
            label="Visibility Threshold", color=threshold_color, linestyle='--', linewidth=2.5)

    ax.set_yscale('log')
    ax.set_xlabel("Time (Local)", fontsize=12, fontweight='bold', color="#333333")
    ax.set_ylabel("Contrast (Log Scale)", fontsize=12, fontweight='bold', color="#333333")
    ax.set_title(f"Lunar Crescent Visibility at {lokasi}\n{day}/{month}/{year}", fontsize=14, fontweight='bold', color="#222222", pad=15)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate(rotation=45)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

    y_pos = df_plot["Contrast"].max() * 0.1
    ax.text(df_plot["Datetime"].iloc[len(df_plot)//2], y_pos, vis_text,
            fontsize=10, color="black",
            bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.5', alpha=0.9),
            horizontalalignment='center')

    ax.legend(fontsize=10, loc='best')
    fig.tight_layout()

    # Convert Figure to PIL Image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    img.load()
    buf.close()
    plt.close(fig)

    # --- Final Printout ---
    print("-" * 30)
    print(f"Sunset (local):  {sunset_local.strftime('%Y-%m-%d %H:%M:%S')}")
    if isinstance(moonset_local, datetime):
        print(f"Moonset (local): {moonset_local.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"Moonset (local): {moonset_local}")

    print(f"Lag (Sunset→Moonset): {minutes_sunset_to_moonset} minutes")
    print(f"Visibility Window: {duration} minutes")
    print(f"Visibility Status: {vis_text}")

    if minutes_sunset_to_moonset > 0:
        ratio = duration / minutes_sunset_to_moonset
        print(f"Visibility Ratio: {ratio:.2f}")
    else:
        print("Visibility Ratio: 0.00")
    print("-" * 30)

    return img

"""
falak.py
========
Modul backend untuk pengiraan data anak bulan (hilal) menggunakan Skyfield.

Ini adalah versi "dibersihkan" (refactored) daripada notebook asal
`Visualisasi_Data_Anak_Bulan.ipynb`. Logik pengiraan (sunset/moonset,
altitud, azimuth, elongasi, umur bulan, kriteria MABIMS) adalah SAMA
seperti notebook — cuma disusun semula menjadi fungsi-fungsi supaya
boleh dipanggil berulang kali oleh web app (setiap kali pelajar hantar
borang, bukan setiap graf perlu >100 baris kod disalin semula).

Untuk tujuan pengajaran, setiap fungsi diberi docstring supaya pelajar
faham APA yang dikira dan MENGAPA.
"""

import io
import math
import base64

import numpy as np
import matplotlib
#matplotlib.use("Agg")  # backend tanpa GUI - perlu untuk server web
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from scipy.ndimage import rotate

from skyfield.api import load, wgs84, N, E
from skyfield import almanac
from skyfield.almanac import find_settings
from skyfield.units import Angle
from skyfield.earthlib import refraction


# ---------------------------------------------------------------------------
# 1. Muat naik data ephemeris (JPL DE440s) - dilakukan SEKALI sahaja semasa
#    server bermula, bukan setiap kali pelajar hantar borang (supaya laju).
# ---------------------------------------------------------------------------
ts = load.timescale()
eph = load("de440s.bsp")
earth = eph["earth"]
sun = eph["sun"]
moon = eph["moon"]


# ---------------------------------------------------------------------------
# 2. Fungsi bantuan: kira waktu terbenam sesuatu objek (matahari / bulan)
# ---------------------------------------------------------------------------
def _waktu_terbenam(observer, body, year, month, day, tz, elevation_m):
    """
    Kira waktu terbenam (sunset/moonset) bagi 'body' (matahari atau bulan)
    di lokasi 'observer', pada tarikh year-month-day.

    Mengembalikan (waktu_skyfield, jam_tempatan_str) supaya waktu tepat
    (objek Skyfield Time) boleh terus digunakan untuk kira altitud/azimuth
    - ini mengelakkan ralat pembundaran yang berlaku bila waktu ditukar
    ke jam:minit dahulu sebelum digunakan semula (seperti dalam notebook asal).
    """
    earth_radius_m = 6378136.6
    side_over_hypotenuse = earth_radius_m / (earth_radius_m + elevation_m)
    dip = Angle(radians=-np.arccos(side_over_hypotenuse))

    solar_radius_degrees = 16 / 60
    r = refraction(0.0, temperature_C=15.0, pressure_mbar=1030.0)
    horizon_degrees = -r + dip.degrees - solar_radius_degrees

    t0 = ts.utc(year, month, day)
    t1 = ts.utc(year, month, day + 1)

    t, y = find_settings(observer, body, t0, t1, horizon_degrees=horizon_degrees)

    waktu_set = None
    for ti, yi in zip(t, y):
        if yi:
            waktu_set = ti
            break

    if waktu_set is None:
        return None, "Tiada terbenam (objek sentiasa di atas/bawah ufuk)"

    h, m, s = waktu_set.utc.hour, waktu_set.utc.minute, waktu_set.utc.second
    jumlah_jam = h + m / 60 + s / 3600 + tz
    h_set, sisa = divmod(jumlah_jam, 1)
    h_set = int(h_set) % 24
    m_set, sisa_s = divmod(sisa * 60, 1)
    m_set = int(m_set)
    s_set = int(sisa_s * 60)
    if s_set >= 60:
        m_set += s_set // 60
        s_set %= 60
    if m_set >= 60:
        h_set = (h_set + m_set // 60) % 24
        m_set %= 60

    waktu_str = f"{h_set:02}:{m_set:02}:{s_set:02}"
    return waktu_set, waktu_str


# ---------------------------------------------------------------------------
# 3. Fungsi utama: kira semua data anak bulan bagi satu lokasi + tarikh
# ---------------------------------------------------------------------------
def kira_data_anak_bulan(lokasi, lat, lon, elevation_m, tz, year, month, day,
                          kriteria_altitude=3.0, kriteria_elongasi=6.4,
                          nama_kriteria="Kriteria MABIMS 2021"):
    """
    Fungsi peringkat tinggi (high-level) yang menghasilkan SEMUA data yang
    diperlukan untuk jadual dan graf:
      - waktu terbenam matahari & bulan
      - sela masa (selang di antara terbenam matahari & bulan)
      - altitud & azimuth bulan dan matahari (ketika matahari terbenam)
      - elongasi (jarak sudut bulan-matahari)
      - umur bulan (jam, sejak ijtimak/konjunksi)
      - status kenampakan mengikut kriteria yang dipilih
    """
    location = wgs84.latlon(lat * N, lon * E)
    observer = earth + location

    # --- Waktu terbenam matahari & bulan ---
    t_sun_set, sun_set_str = _waktu_terbenam(observer, sun, year, month, day, tz, elevation_m)
    t_moon_set, moon_set_str = _waktu_terbenam(observer, moon, year, month, day, tz, elevation_m)

    if t_sun_set is None or t_moon_set is None:
        raise ValueError("Tidak dapat mengira waktu terbenam bagi lokasi/tarikh ini.")

    sela_masa = abs((t_sun_set.tt - t_moon_set.tt) * 24 * 60)  # dalam minit

    # --- Kedudukan matahari & bulan SEBAIK sahaja matahari terbenam ---
    t_cerapan = t_sun_set
    sun_astro = observer.at(t_cerapan).observe(sun).apparent()
    moon_astro = observer.at(t_cerapan).observe(moon).apparent()

    sun_alt, sun_az, _ = sun_astro.altaz()
    moon_alt, moon_az, _ = moon_astro.altaz()

    elongasi = sun_astro.separation_from(moon_astro).degrees
    beza_altitud = abs(moon_alt.degrees - sun_alt.degrees)

    # --- Umur bulan: cari waktu ijtimak (konjunksi) terdekat ---
    t0 = ts.utc(year, month, day - 2)
    t1 = ts.utc(year, month, day + 2)
    f = almanac.oppositions_conjunctions(eph, eph["Moon"])
    t_conj, y_conj = almanac.find_discrete(t0, t1, f)

    jd_konjunksi = None
    for ti, yi in zip(t_conj, y_conj):
        if yi == 1:  # 1 = konjunksi (ijtimak), 0 = oposisi (purnama)
            jd_konjunksi = ti.tt
            break

    umur_bulan_jam = (t_cerapan.tt - jd_konjunksi) * 24 if jd_konjunksi else None

    # --- Semakan kriteria kenampakan ---
    if beza_altitud >= kriteria_altitude and elongasi >= kriteria_elongasi:
        kenampakan = "Melepasi Kriteria"
    else:
        kenampakan = "Tidak Melepasi Kriteria"

    return {
        "lokasi": lokasi,
        "tarikh": f"{day}/{month}/{year}",
        "lat": lat, "lon": lon, "elevation_m": elevation_m, "tz": tz,
        "sun_set_str": sun_set_str,
        "moon_set_str": moon_set_str,
        "sela_masa_minit": sela_masa,
        "sun_alt": sun_alt.degrees,
        "sun_az": sun_az.degrees,
        "moon_alt": moon_alt.degrees,
        "moon_az": moon_az.degrees,
        "beza_altitud": beza_altitud,
        "elongasi": elongasi,
        "umur_bulan_jam": umur_bulan_jam,
        "kriteria_altitude": kriteria_altitude,
        "kriteria_elongasi": kriteria_elongasi,
        "nama_kriteria": nama_kriteria,
        "kenampakan": kenampakan,
    }


import io
import math
import urllib.request
from datetime import datetime, timezone, timedelta

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Arc
from scipy.ndimage import rotate
from PIL import Image

from skyfield.api import load, wgs84
from skyfield import almanac

# ==========================================
# Default GitHub Asset URLs
# ==========================================
DEFAULT_CRESCENT_URL = "https://raw.githubusercontent.com/msyazwanfaid/falakpy/main/crescent180v2.1.png"
DEFAULT_HORIZON_URL  = "https://raw.githubusercontent.com/msyazwanfaid/falakpy/main/horizon-sea.jpg"
DEFAULT_LOGO_URL     = "https://raw.githubusercontent.com/msyazwanfaid/falakpy/main/logo.png"


def _resolve_image(image_input, mode='RGBA'):
    """
    Resolves an image input into a NumPy array.
    Supports: None, local paths, HTTP/HTTPS/GitHub raw URLs, PIL Images, and NumPy arrays.
    """
    if image_input is None:
        return None

    if isinstance(image_input, np.ndarray):
        return image_input

    if isinstance(image_input, Image.Image):
        return np.array(image_input.convert(mode))

    if isinstance(image_input, str):
        # Web or GitHub URL
        if image_input.startswith(('http://', 'https://')):
            req = urllib.request.Request(
                image_input, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response:
                img_data = response.read()
            pil_img = Image.open(io.BytesIO(img_data)).convert(mode)
            return np.array(pil_img)

        # Local file path
        pil_img = Image.open(image_input).convert(mode)
        return np.array(pil_img)

    raise ValueError(f"Unsupported image input type: {type(image_input)}")


def plot_hilal_visibility(config,
                          crescent_img_path=None,
                          logo_path=None,
                          logo_zoom=0.25,
                          logo_alpha=0.20,
                          background_image_path=None,
                          horizon_y_ratio=0.50,
                          sky_palette='twilight'):
    """
    Menjana visualisasi kriteria keterlihatan anak bulan (hilal) pada waktu terbenam matahari.
    """
    plt.close('all')

    # 1. Ekstrak data konfigurasi
    lat = config["lat"]
    lon = config["lon"]
    elevation_m = config.get("elevation_m", 0)
    tz_offset = config.get("tz", 8)
    year = config["year"]
    month = config["month"]
    day = config["day"]
    kriteria_altitude = config.get("kriteria_altitude", 3.0)
    kriteria_elongasi = config.get("kriteria_elongasi", 6.4)
    lokasi = config.get("lokasi", "Lokasi Cerapan")

    # 2. Pengiraan astronomi (Skyfield)
    ts = load.timescale()
    eph = load('de440s.bsp')
    earth, sun, moon = eph['earth'], eph['sun'], eph['moon']

    topos = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elevation_m)
    observer = earth + topos
    tz_info = timezone(timedelta(hours=tz_offset))

    # Waktu Matahari Terbenam (Sunset)
    t0 = ts.from_datetime(datetime(year, month, day, 0, 0, tzinfo=tz_info))
    t1 = ts.from_datetime(datetime(year, month, day, 23, 59, tzinfo=tz_info))
    f = almanac.sunrise_sunset(eph, topos)
    times, events = almanac.find_discrete(t0, t1, f)

    sunset_times = [t for t, event in zip(times, events) if event == 0]
    if not sunset_times:
        raise ValueError("Waktu terbenam matahari tidak ditemui bagi tarikh dan koordinat ini.")
    t_sunset = sunset_times[0]

    # Koordinat Alt-Az Topisentrik
    sun_app = observer.at(t_sunset).observe(sun).apparent()
    moon_app = observer.at(t_sunset).observe(moon).apparent()

    sun_alt_deg = float(sun_app.altaz()[0].degrees)
    sun_az_deg = float(sun_app.altaz()[1].degrees)
    moon_alt_deg = float(moon_app.altaz()[0].degrees)
    moon_az_deg = float(moon_app.altaz()[1].degrees)

    arcv = np.round(moon_alt_deg - sun_alt_deg, 2)
    daz = np.round(moon_az_deg - sun_az_deg, 2)
    arcl = np.round(sun_app.separation_from(moon_app).degrees, 2)

    # 3. Penyediaan Kanvas Graf
    fig, ax = plt.subplots(figsize=(16, 9))

    xlim_min = sun_az_deg - 10
    xlim_max = sun_az_deg + 10
    ylim_min = min(sun_alt_deg - 2, -2.8)
    ylim_max = max(moon_alt_deg + 4, kriteria_altitude + 4)

    ax.set_xlim((xlim_min, xlim_max))
    ax.set_ylim((ylim_min, ylim_max))

    # 4. Latar Belakang (Foto Ufuk Laut atau Skema Gradien)
    # Gunakan default GitHub jika None, atau URL/path milik pengguna
    bg_source = background_image_path if background_image_path is not None else DEFAULT_HORIZON_URL
    bg_loaded = False

    if bg_source:
        try:
            bg_arr = _resolve_image(bg_source, mode='RGB')
            # Laraskan ufuk gambar supaya tepat berada di y = 0 darjah
            total_alt_height = ylim_max / (1.0 - horizon_y_ratio)
            img_y_bottom = ylim_max - total_alt_height

            ax.imshow(bg_arr, extent=[xlim_min, xlim_max, img_y_bottom, ylim_max],
                      aspect='auto', zorder=0)
            bg_loaded = True
        except Exception as e:
            print(f"[*] Amaran imej latar belakang: {e}")

    if not bg_loaded:
        palettes = {
            'twilight': ['#102542', '#33658A', '#F6AE2D', '#F26419'],
            'sunset_warm': ['#2b1055', '#75225b', '#b33939', '#e17055', '#f39c12'],
            'deep_night': ['#02050e', '#091833', '#133b5c', '#1d2a44'],
            'clear_blue': ['#0f2027', '#203a43', '#2c5364', '#4ca1af']
        }
        colors = palettes.get(sky_palette, palettes['twilight']) if isinstance(sky_palette, str) else sky_palette
        sky = LinearSegmentedColormap.from_list('custom_sky', colors)
        ax.imshow([[1, 1], [0, 0]], cmap=sky, interpolation='bicubic',
                  extent=[xlim_min, xlim_max, ylim_min, ylim_max], aspect='auto', zorder=0)

    # 5. Logo Syarikat / Universiti (Watermark di Tengah Kanvas)
    logo_source = logo_path if logo_path is not None else DEFAULT_LOGO_URL
    if logo_source:
        try:
            logo_arr = _resolve_image(logo_source, mode='RGBA')
            imagebox_logo = OffsetImage(logo_arr, zoom=logo_zoom, alpha=logo_alpha)
            ab_logo = AnnotationBbox(imagebox_logo, (0.5, 0.5), xycoords='axes fraction',
                                     frameon=False, zorder=1)
            ax.add_artist(ab_logo)
        except Exception as e:
            print(f"[*] Amaran memuatkan logo: {e}")

    # 6. Ufuk Hakiki (0 darjah)
    horizon_x = np.linspace(xlim_min, xlim_max, 100)
    ax.plot(horizon_x, np.zeros_like(horizon_x), color='black', linestyle='-', linewidth=1.8, label='Ufuk Hakiki (0°)', zorder=2)

    # 7. Kedudukan Matahari
    ax.scatter(sun_az_deg, sun_alt_deg, color='red', s=850, label='Matahari', zorder=10)

    # 8. Kedudukan dan Orientasi Bulan Sabit (Hilal)
    opposite = moon_alt_deg - sun_alt_deg
    adjacent = (moon_az_deg - sun_az_deg)
    angle_rad = math.atan2(opposite, adjacent)
    angle_degrees = math.degrees(angle_rad)

    crescent_source = crescent_img_path if crescent_img_path is not None else DEFAULT_CRESCENT_URL
    try:
        crescent_img = _resolve_image(crescent_source, mode='RGBA')
        # Rotate crescent image berdasarkan sudut kedudukan matahari-bulan
        rotated_img = rotate(crescent_img, angle_degrees, reshape=True)

        imagebox = OffsetImage(rotated_img, zoom=0.1)
        ab = AnnotationBbox(imagebox, (moon_az_deg, moon_alt_deg), frameon=False, zorder=11)
        ax.add_artist(ab)
    except Exception as e:
        print(f"[*] Amaran memuatkan imej bulan: {e}")
        ax.scatter(moon_az_deg, moon_alt_deg, color='gold', s=400, label='Bulan', zorder=11)

    # 9. Sembulan Kriteria Elongasi (Arka Lengkok)
    semicircle_patch = Arc((sun_az_deg, sun_alt_deg), 2 * kriteria_elongasi, 2 * kriteria_elongasi,
                           theta1=0, theta2=180, fill=False, color='blue', linestyle='--', linewidth=2,
                           label=f'Kriteria Elongasi ({kriteria_elongasi}°)', zorder=5)
    ax.add_patch(semicircle_patch)

    # 10. Sembulan Kriteria Altitud
    ax.hlines(y=kriteria_altitude, xmin=xlim_min, xmax=max(xlim_min, sun_az_deg - kriteria_elongasi),
              color='red', linestyle='--', linewidth=1.8, label=f'Kriteria Altitud ({kriteria_altitude}°)', zorder=5)
    ax.hlines(y=kriteria_altitude, xmin=min(xlim_max, sun_az_deg + kriteria_elongasi), xmax=xlim_max,
              color='red', linestyle='--', linewidth=1.8, zorder=5)

    # 11. Label, Tajuk & Kotak Maklumat
    sunset_local = t_sunset.astimezone(tz_info).strftime('%H:%M:%S')
    ax.set_xlabel('Azimut (darjah)', fontsize=12)
    ax.set_ylabel('Altitud (darjah)', fontsize=12)
    ax.set_title(f'Kedudukan Bulan-Matahari Ketika Terbenam Matahari\n{lokasi} | Tarikh: {year}-{month:02d}-{day:02d} ({sunset_local} Waktu Tempatan)',
                 fontsize=14, fontweight='bold')

    # Garisan Altitud
    ax.vlines(x=moon_az_deg, ymin=0, ymax=moon_alt_deg, color='blue', linestyle='--')
    ax.text(moon_az_deg + 0.5, moon_alt_deg / 2, 'Altitud Bulan', fontsize=10, ha='left')

    # Garisan Elongasi
    ax.plot([moon_az_deg, sun_az_deg], [moon_alt_deg, sun_alt_deg], color='green', linestyle='--')
    ax.text((daz) / 2 + sun_az_deg, arcv / 2 + sun_alt_deg, 'Elongasi Bulan', fontsize=10, ha='left')

    info_text = (
        f"Altitud Bulan : {moon_alt_deg:.2f}°\n"
        f"Altitud Matahari : {sun_alt_deg:.2f}°\n"
        f"ARCV (ΔAlt) : {arcv:.2f}°\n"
        f"DAZ (ΔAz) : {daz:.2f}°\n"
        f"Elongasi (ARCL): {arcl:.2f}°"
    )
    ax.text(0.02, 0.95, info_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85), zorder=12)

    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(color='white', linestyle=':', linewidth=0.5, alpha=0.4)

    plt.tight_layout()


    # Save canvas buffer into a PIL Image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    buf.seek(0)
    img = Image.open(buf)
    img.load()  # Load image data into memory before closing buffer
    buf.close()

    plt.close(fig)  # Free Matplotlib memory
    return img


from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
import geojsoncontour

from shapely.geometry import Point, MultiPolygon
from shapely.prepared import prep

from skyfield.api import Topos, load
from skyfield.almanac import find_settings
from tqdm import tqdm


def globalvisibilitymap(year, month, day, lat_res=200, lon_res=400, save_html=True):
    """
    Generates an interactive Folium crescent visibility map at sunset using MABIMS 2021.
    Saves an exportable, interactive HTML file.
    """
    csv_filename = f"visibility_data_adjusted_{year}_{month}_{day}.csv"
    html_filename = f"visibility_map_{year}_{month}_{day}.html"
    print(f"--- Starting Calculation for {day:02d}-{month:02d}-{year} ---")

    # 1. Ephemeris & Timescale
    try:
        eph = load('de440s.bsp')
    except Exception:
        eph = load('de421.bsp')

    earth, moon, sun_obj = eph['earth'], eph['moon'], eph['sun']
    ts = load.timescale()

    lat_values = np.linspace(-60, 60, lat_res)
    lon_values = np.linspace(-179.9, 179.9, lon_res)

    csv_data = []

    # 2. Main Calculation Loop
    for lat in tqdm(lat_values, desc="Calculating Visibility"):
        for lon in lon_values:
            is_visible = False
            arcv, arcl, daz = np.nan, np.nan, np.nan

            try:
                approx_utc_offset = lon / 15.0
                dt_sunset_approx = datetime(year, month, day, 18, 0, tzinfo=timezone.utc) - timedelta(hours=approx_utc_offset)

                t0_sf = ts.from_datetime(dt_sunset_approx - timedelta(hours=4))
                t1_sf = ts.from_datetime(dt_sunset_approx + timedelta(hours=4))

                obs_site = earth + Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=0)

                t_set, _ = find_settings(obs_site, sun_obj, t0_sf, t1_sf, horizon_degrees=-0.8333)
                if t_set:
                    t_observe = t_set[0]

                    moon_app = obs_site.at(t_observe).observe(moon).apparent()
                    sun_app = obs_site.at(t_observe).observe(sun_obj).apparent()

                    moon_alt = float(moon_app.altaz()[0].degrees)
                    sun_alt = float(sun_app.altaz()[0].degrees)
                    arcl = float(sun_app.separation_from(moon_app).degrees)
                    arcv = float(moon_alt - sun_alt)
                    daz = float(abs(sun_app.altaz()[1].degrees - moon_app.altaz()[1].degrees))

                    # MABIMS (2021) Criteria
                    is_visible = (moon_alt >= 3.0) and (arcl >= 6.4)
            except Exception:
                pass

            csv_data.append([
                lat, lon, arcv, arcl, daz,
                "Visible" if is_visible else "Not Visible",
                1 if is_visible else 0
            ])

    columns = ["Latitude", "Longitude", "ArcV", "ArcL", "Daz", "Visibility", "Map Value"]
    df = pd.DataFrame(csv_data, columns=columns)
    df.to_csv(csv_filename, index=False)
    print(f"CSV Saved: {csv_filename}")




    # 3. Find First Land Visibility (No Cartopy required)
    print("Searching for first land visibility...")
    east_point = None
    try:
        import json
        import urllib.request
        from shapely.geometry import shape

        geojson_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson"
        req = urllib.request.Request(geojson_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            land_data = json.loads(resp.read().decode('utf-8'))

        geoms = [shape(f['geometry']) for f in land_data['features']]
        land_geom = prep(MultiPolygon(geoms) if len(geoms) > 1 else geoms[0])

        visible_df = df[df['Visibility'] == 'Visible'].sort_values(by='Longitude', ascending=False)

        for _, row in visible_df.iterrows():
            if land_geom.contains(Point(row['Longitude'], row['Latitude'])):
                lat_dir = 'N' if row['Latitude'] >= 0 else 'S'
                lon_dir = 'E' if row['Longitude'] >= 0 else 'W'
                print(f"Found: {abs(row['Latitude']):.2f}°{lat_dir}, {abs(row['Longitude']):.2f}°{lon_dir}")
                east_point = row
                break
    except Exception as e:
        print(f"Land lookup skipped: {e}")

    # 4. Generate Interactive Folium Map
    print("Generating Folium Map...")
    pivot = df.pivot_table(index='Latitude', columns='Longitude', values='Map Value', fill_value=0)
    lon_grid, lat_grid = np.meshgrid(pivot.columns, pivot.index)


    # Base Folium Map
    m = folium.Map(
        location=[10, 0],
        zoom_start=2,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, HERE, Garmin, © OpenStreetMap contributors, and the GIS user community",
        world_copy_jump=True
    )

    # Convert contour to geojson
    fig_dummy, ax_dummy = plt.subplots()
    contour = ax_dummy.contourf(
        lon_grid, lat_grid, pivot.values,
        levels=[-0.1, 0.5, 1.1],
        colors=['#e74c3c', '#2ecc71'],
        alpha=0.4
    )
    plt.close(fig_dummy)

    # Convert contour layer to geojson and add to Folium
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contour,
        min_angle_deg=3.0,
        ndigits=3,
        stroke_width=1,
        fill_opacity=0.35
    )

    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            'color': x['properties']['stroke'],
            'weight': x['properties']['stroke-width'],
            'fillColor': x['properties']['fill'],
            'opacity': 0.5,
            'fillOpacity': 0.35
        },
        name="MABIMS 2021 Visibility"
    ).add_to(m)

    # Add Star Marker for First Land Point
    if east_point is not None:
        elat, elon = east_point['Latitude'], east_point['Longitude']
        folium.Marker(
            location=[elat, elon],
            popup=f"<b>First Land Visibility</b><br>Lat: {elat:.2f}°, Lon: {elon:.2f}°",
            tooltip="First Land Visibility",
            icon=folium.Icon(color="orange", icon="star")
        ).add_to(m)

    # Add Title Banner
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 60px; width: 380px; height: 60px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; font-weight:bold; padding: 6px; border-radius: 6px;">
        Global Crescent Visibility (MABIMS 2021)<br>
        Date: {day:02d}/{month:02d}/{year}<br>
        <span style="color:#2ecc71;">■</span> Visible &nbsp;&nbsp; 
        <span style="color:#e74c3c;">■</span> Not Visible
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Save to downloadable HTML
    if save_html:
        m.save(html_filename)
        print(f"Interactive map saved: {html_filename}")

    return m