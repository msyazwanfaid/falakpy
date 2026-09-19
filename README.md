
```markdown
# 🌙 falakpy — Islamic Astronomy Toolkit for Python

[![PyPI version](https://img.shields.io/pypi/v/falakpy.svg)](https://pypi.org/project/falakpy/)
[![Python Version](https://img.shields.io/pypi/pyversions/falakpy.svg)](https://pypi.org/project/falakpy/)
[![License](https://img.shields.io/github/license/syazwanfaid/falakpy.svg)](https://github.com/msyazwanfaid/falakpy/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/falakpy)](https://pepy.tech/project/falakpy)

**falakpy** is a Python package for **Islamic astronomical computations (ʿIlm al-Falak)** — covering:  
🕋 *Qibla Direction*, 🕌 *Prayer Times*, and 🌙 *Lunar Observation & Visibility Modeling*.  
It is designed for students, researchers, and enthusiasts who wish to integrate classical *Falak* knowledge with modern astronomical computation via [Skyfield](https://rhodesmill.org/skyfield/).

---

## 🚀 Installation

Install directly from PyPI:

```bash
pip install falakpy

```

### Module Summary

| Module | Description |
| --- | --- |
| `falakpy.qibla` | Compute Qibla direction, solar alignment windows (anti-Qibla), and generate polar compass plots. |
| `falakpy.prayertime` | Calculate daily and multi-day prayer schedules with customizable twilight angles and madhhab rules. |
| `falakpy.lunar` | Determine sunset, moonset, lag time, topocentric crescent parameters, global visibility curves, and physical contrast modeling. |

---

# 🕋 Qibla Direction (`falakpy.qibla`)

The **`falakpy.qibla`** module calculates the **Qibla direction** (great-circle azimuth toward the Kaabah) and identifies when the **Sun’s azimuth** aligns with or opposes the Qibla direction — useful for **Qibla verification** via sunlight alignment.

---

### ⚙️ Function Overview: `falakpy.qibla`

| Function | Signature | Description |
| --- | --- | --- |
| `direction` | `direction(lat, lon)` | Computes the great-circle Qibla azimuth in degrees and DMS format from coordinates. |
| `dailyqibla` | `dailyqibla(lat, lon, ele, y, m, d, tz, tolerance)` | Finds time intervals when the Sun aligns with or opposes the Qibla azimuth on a single day. |
| `multiday_qibla` | `multiday_qibla(lat, lon, ele, timezone, y, m, d_start, num_days, tolerance, csv_filename)` | Runs multi-day simulations of solar alignment windows and exports results to CSV. |
| `qiblacompass` | `qiblacompass(latitude, longitude, year, month, day, timezone, time_hour, time_minute)` | Generates a polar plot visualizing Qibla direction, current Sun azimuth, and cast shadow azimuth. |

---

### 🧭 Example 1 — Basic Qibla Direction

```python
from falakpy import qibla

latitude = 3.1390      # Kuala Lumpur latitude (°N → positive)
longitude = 101.6869   # Kuala Lumpur longitude (°E → positive)

s = qibla.direction(latitude, longitude)

print("Qibla (DMS):", s.degree)
print("Qibla (Decimal):", s.decimal)

```

**Output:**

```text
Qibla (DMS): 292° 60′ 0″
Qibla (Decimal): 292.7056910716602

```

---

### 🌞 Example 2 — Daily Qibla–Sun Alignment

Find when the Sun’s azimuth is parallel or opposite to the Qibla direction on a specific date.

```python
from falakpy import qibla

z, y = qibla.dailyqibla(2.1484, 102.7308, 50.0, 2025, 10, 14, 8, 5)

print(y)   # Opposite alignment
print(z)   # Qibla alignment

```

**Output:**

```text
[OPPOSITE (Qibla - 180°)] Sun azimuth ~ 112.84° ±5° on 2025-10-14.
  • Entry ~ 10:42:59 | Exit ~ 11:35:37 

[QIBLA] No Sun azimuth within 292.84° ±5° on 2025-10-14.

```

☀️ *This shows when sunlight falls directly opposite the Qibla direction (known as the anti-Qibla event).*

---

### 📅 Example 3 — Multi-Day Qibla Windows

Run a **5-day analysis** to find daily solar Qibla alignments and their times.

```python
from falakpy import qibla

qibla.multiday_qibla(
    lat=3.1390, lon=101.6869, ele=40,
    timezone=8, y=2025, m=10, d_start=20,
    num_days=5, tolerance=2.0,
    csv_filename="qibla_windows_5days.csv"
)

```

**Output (Excerpt):**

```text
=== 2025-10-20 ===
[QIBLA] No Sun azimuth within 292.54° ±2.0° on 2025-10-20.
[OPPOSITE (Qibla - 180°)] Sun azimuth ~ 112.54° ±2.0° on 2025-10-20.
  • Entry ~ 10:29:09 | Exit ~ 10:56:47  

=== 2025-10-21 ===
[QIBLA] No Sun azimuth within 292.54° ±2.0° on 2025-10-21.
[OPPOSITE (Qibla - 180°)] Sun azimuth ~ 112.54° ±2.0° on 2025-10-21.
  • Entry ~ 10:24:31 | Exit ~ 10:53:07  

✅ Saved multi-day Qibla windows to qibla_windows_5days.csv

```

---

### 🧭 Example 4 — Visual Qibla Compass (Sun & Shadow)

Generate a polar plot (compass) to visually verify the Qibla direction using the Sun's current azimuth and the shadow it casts on a vertical object.

```python
from falakpy import qibla

# Parameters: Lat, Lon, Year, Month, Day, Timezone, Hour, Minute
qibla.qiblacompass(
    latitude=3.1390, 
    longitude=101.6869, 
    year=2025, 
    month=10, 
    day=14, 
    timezone=8, 
    time_hour=10, 
    time_minute=42
)

```

---

### 📘 Qibla Parameter Explanation

| Parameter | Meaning | Example |
| --- | --- | --- |
| `lat` | Latitude (°N → positive, °S → negative) | `3.1390` |
| `lon` | Longitude (°E → positive, °W → negative) | `101.6869` |
| `ele` | Elevation above sea level (m) | `40` |
| `timezone` | UTC offset | `8` for Malaysia |
| `y, m, d_start` | Starting Gregorian date | `2025, 10, 20` |
| `num_days` | Consecutive days to calculate | `5` |
| `tolerance` | Acceptable range (±°) around Qibla azimuth | `2.0` |
| `csv_filename` | Output CSV file name | `"qibla_windows_5days.csv"` |

---

# 🕌 Prayer Time Calculation (`falakpy.prayertime`)

Calculate accurate daily and multi-day prayer schedules using precise astronomical solar depression angles.

---

### ⚙️ Function Overview: `falakpy.prayertime`

| Function | Signature | Description |
| --- | --- | --- |
| `singleday` | `singleday(lat, lon, ele, tz, y, m, d, csv_filename, deg_subuh, deg_isha, asar_shadow_lenght)` | Computes prayer times (Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha) for a single Gregorian date. |
| `multiday` | `multiday(lat, lon, ele, tz, y, m, d_start, num_days, csv_filename, deg_subuh, deg_isha, asar_shadow_length)` | Computes prayer schedules across multiple consecutive days and exports them to a CSV file. |

---

### 🕰️ Example 1 — Single Day Calculation

```python
from falakpy import prayertime

latitude = 3.1390      # Kuala Lumpur latitude (°N → positive)
longitude = 101.6869   # Kuala Lumpur longitude (°E → positive)
elevation = 40         # Elevation in meters
timezone = 8           # UTC +8 for Malaysia
year, month, day = 2025, 1, 28

times = prayertime.singleday(latitude, longitude, elevation, timezone, year, month, day)

print(times)

```

**Output:**

```text
Fajr     : 05:53
Sunrise  : 07:13
Dhuhr    : 13:26
Asr      : 16:46
Maghrib  : 19:28
Isha     : 20:41

```

---

### 📘 Variable Explanation

| Variable | Meaning | Example |
| --- | --- | --- |
| `latitude` | Your location’s latitude (°N or °S) — **S = negative** | `3.1390` |
| `longitude` | Your location’s longitude (°E or °W) — **W = negative** | `101.6869` |
| `elevation` | Height above sea level (m) | `40` |
| `timezone` | UTC offset | `8` for Malaysia |
| `year, month, day` | Gregorian date | `2025, 1, 28` |

---

### 🕰️ Example for Other Locations

#### Jakarta, Indonesia

```python
prayertime.singleday(-6.2088, 106.8456, 30, 7, 2025, 1, 28)

```

#### Mecca, Saudi Arabia

```python
prayertime.singleday(21.3891, 39.8579, 300, 3, 2025, 1, 28)

```

#### London, UK

```python
prayertime.singleday(51.5072, -0.1276, 25, 0, 2025, 1, 28)

```

*(Use negative latitude for South, and negative longitude for West.)*

---

### 🕌 `prayertime.singleday()` Function Reference

```python
def singleday(
    lat, lon, ele, tz, y, m, d,
    csv_filename="prayer_times.csv",
    deg_subuh=-18,
    deg_isha=-18,
    asar_shadow_lenght=1
)

```

**Defaults:**

| Parameter | Default | Description |
| --- | --- | --- |
| `csv_filename` | `"prayer_times.csv"` | Output file name |
| `deg_subuh` | `-18` | Subuh twilight angle (° below horizon) |
| `deg_isha` | `-18` | Isyak twilight angle (° below horizon) |
| `asar_shadow_lenght` | `1` | Asar shadow ratio (1 = Shafi‘i, 2 = Hanafi) |

---

### 🕌 Multi-Day Prayer Time Calculation

The `multiday()` function in **`falakpy.prayertime`** computes prayer times for **multiple consecutive days**, with flexible options to adjust Subuh and Isyak twilight angles as well as Asar shadow length (madhhab).

```python
def multiday(
    lat, lon, ele, tz, y, m, d_start, num_days,
    csv_filename="prayer_times_multi.csv",
    deg_subuh=-18,
    deg_isha=-18,
    asar_shadow_length=1
)

```

---

### 📘 Parameter Explanation: `multiday()`

| Parameter | Description | Example |
| --- | --- | --- |
| `lat` | Latitude of observer (**°N positive, °S negative**) | `3.1699` |
| `lon` | Longitude of observer (**°E positive, °W negative**) | `101.9384` |
| `ele` | Elevation above sea level (m) | `40` |
| `tz` | Time zone (UTC offset) | `8` for Malaysia |
| `y, m, d_start` | Start date (Gregorian) | `2025, 12, 21` |
| `num_days` | Number of consecutive days to compute | `5` |
| `csv_filename` | Output CSV file name | `"prayer_times_multi.csv"` |
| `deg_subuh` | Sun altitude (° below horizon) for **Fajr/Subuh** | `-18` (default) |
| `deg_isha` | Sun altitude (° below horizon) for **Isyak** | `-18` (default) |
| `asar_shadow_length` | Shadow ratio for **Asar** (1 = Shafi‘i, 2 = Hanafi) | `1` (default) |

---

### 🧭 Example 1 — Standard Multi-Day Schedule

```python
from falakpy import prayertime

s = prayertime.multiday(3.1699, 101.9384, 40, 8, 2025, 12, 21, 5)
print(s)

```

**Output:**

```text
Date        Fajr   Sunrise   Dhuhr   Asr   Maghrib   Isha
----------------------------------------------------------
2025-12-21  05:53  07:11     13:26  16:46  19:28     20:41
2025-12-22  05:53  07:12     13:26  16:47  19:29     20:41
2025-12-23  05:54  07:12     13:26  16:47  19:29     20:41
2025-12-24  05:54  07:12     13:27  16:48  19:30     20:42
2025-12-25  05:54  07:12     13:27  16:48  19:30     20:42

```

---

### 🌅 Example 2 — Custom Subuh and Isyak Angles

```python
from falakpy import prayertime

s = prayertime.multiday(
    3.1699, 101.9384, 40, 8, 2025, 12, 21, 5,
    deg_subuh=-15, deg_isha=-15
)
print(s)

```

This setting shortens twilight time, suitable for regions near the equator or institutions using adjusted twilight depression angles.

---

### ☀️ Example 3 — Hanafi Asar Definition

```python
from falakpy import prayertime

s = prayertime.multiday(
    3.1699, 101.9384, 40, 8, 2025, 12, 21, 5,
    asar_shadow_length=2
)
print(s)

```

Setting `asar_shadow_length=2` follows the **Hanafi** school, where Asar begins when an object’s shadow equals **twice** its length plus noon shadow.

---

### 💾 CSV Output

By default, a file named **`prayer_times_multi.csv`** will be saved in your working directory containing all computed prayer times formatted for downstream spreadsheet or tabular analysis.

---

# 🌙 Lunar Observation Data (`falakpy.lunar`)

The **`lunar`** module provides comprehensive parameters for **hilal (crescent moon) visibility**, including sunset, moonset, lag time, moon age, altitude, elongation angles, global visibility maps, and physical contrast modeling.

---

### ⚙️ Function Overview: `falakpy.lunar`

| Function | Signature | Description |
| --- | --- | --- |
| `tabeldata` | `tabeldata(latitude, longitude, elevation, timezone, year, month, day)` | Generates a quick terminal summary table of sunset, moonset, lag time, altitude, DAZ, ArcV, and ArcL. |
| `observedata` | `observedata(latitude, longitude, elevation, timezone, year, month, day)` | Computes a 10-element tuple of high-precision topocentric hilal parameters at local sunset. |
| `globalvisibilitymap` | `globalvisibilitymap(year, month, day, LAT_RES, LON_RES)` | Renders a terminal-based global ASCII map illustrating zones of crescent visibility and first sighting point. |
| `visibilitycontrast` | `visibilitycontrast(lat, long, year, month, day, ele, tz, temperature_celcius, relative_humidity, light_pollution_magsec, location)` | Simulates minute-by-minute physical contrast between lunar crescent and twilight sky from sunset to moonset. |

---

### 📊 Method 1: Summary Table (`tabeldata`)

```python
from falakpy import lunar

latitude = 3.1390      # Kuala Lumpur latitude (°N → positive)
longitude = 101.6869   # Kuala Lumpur longitude (°E → positive)
elevation = 40         # Elevation in meters
timezone = 8           # UTC +8 for Malaysia
year, month, day = 2025, 1, 28

times = lunar.tabeldata(latitude, longitude, elevation, timezone, year, month, day)

```

**Output:**

```text
+------------+----------+----------+----------+----------+----------+----------+----------+----------+
|    Date    |  Sunset  |  Moonset | LagTime  | MoonAge  | MoonAlt  |   DAZ    |   ArcV   |   ArcL   |
+------------+----------+----------+----------+----------+----------+----------+----------+----------+
| 2025-01-28 | 19:29:23 | 18:29:31 | 23:00:08 |   23.01  |  -13.98  |   7.50   |  12.95   |  14.92   |
+------------+----------+----------+----------+----------+----------+----------+----------+----------+

```

---

### 🌘 Method 2: Single-Date Hilal Observation Data (`observedata`)

The **`observedata`** function computes detailed **hilal (crescent moon) visibility parameters** for a single date and location, including sunset, moonset, lag time, moon age, altitude, elongation, and crescent width — using precise astronomical calculations via Skyfield.

```python
from falakpy import lunar

latitude = 3.1390      # Kuala Lumpur latitude (°N → positive)
longitude = 101.6869   # Kuala Lumpur longitude (°E → positive)
elevation = 40         # Elevation in meters
timezone = 8           # UTC +8 for Malaysia
year, month, day = 2026, 7, 17

result = lunar.observedata(latitude, longitude, elevation, timezone, year, month, day)

```

#### Raw Output

`observedata()` returns a **plain tuple** of 10 values, in a fixed order:

```text
('19:28:45', '22:11:51', datetime.timedelta(seconds=9786, microseconds=896487),
 73.75224318355322, 38.225342043865936, 12.799197207168163,
 39.26100361950058, 40.996077346868155, 3.9693035958188423, 238.15821574913053)

```

---

### 📘 Variable Explanation: `observedata()`

| Variable | Meaning | Example |
| --- | --- | --- |
| `latitude` | Observer's latitude (°N or °S) — **S = negative** | `3.1390` (North = positive) |
| `longitude` | Observer's longitude (°E or °W) — **W = negative** | `101.6869` (East = positive) |
| `elevation` | Height above sea level (m) | `40` |
| `timezone` | UTC offset | `8` for Malaysia |
| `year, month, day` | Gregorian date of observation | `2026, 7, 17` |

---

### 📗 Return Value Reference

| # | Name | Type | Unit | Description |
| --- | --- | --- | --- | --- |
| 0 | `sunset` | `str` | `HH:MM:SS` | Local sunset time (upper-limb, refraction-corrected) |
| 1 | `moonset` | `str` | `HH:MM:SS` | Local moonset time, or `"—"` if the moon doesn't set that day |
| 2 | `lag_time` | `datetime.timedelta` | — | Moonset − sunset duration (`.total_seconds()/60` for minutes) |
| 3 | `moon_age` | `float` | hours | Time elapsed since conjunction (new moon) before sunset |
| 4 | `moon_alt` | `float` | degrees | Topocentric Moon altitude at sunset |
| 5 | `daz` | `float` | degrees | Relative azimuth difference (DAZ) between Sun and Moon |
| 6 | `arcv` | `float` | degrees | Arc of Vision — altitude difference between Moon and Sun |
| 7 | `arcl` | `float` | degrees | Arc of Light — angular separation (elongation) between Sun and Moon |
| 8 | `width_arcmin` | `float` | arcminutes | Crescent width |
| 9 | `width_arcsec` | `float` | arcseconds | Crescent width (in arcseconds) |

---

### 🏷️ Named Access with `HilalObservation`

For enhanced readability, wrap the raw tuple in a `NamedTuple`:

```python
from typing import NamedTuple
from falakpy import lunar

class HilalObservation(NamedTuple):
    sunset: str             # HH:MM:SS local sunset time
    moonset: str            # HH:MM:SS local moonset time, or "—" if none
    lag_time: object        # datetime.timedelta, moonset - sunset
    moon_age: float         # hours since last conjunction
    moon_alt: float         # degrees, moon altitude at sunset
    daz: float              # degrees, relative azimuth (DAZ)
    arcv: float             # degrees, Arc of Vision
    arcl: float             # degrees, Arc of Light (elongation)
    width_arcmin: float     # arcminutes, crescent width
    width_arcsec: float     # arcseconds, crescent width

raw = lunar.observedata(3.1390, 101.6869, 40, 8, 2026, 7, 17)
result = HilalObservation(*raw)

print(result.sunset)         # '19:28:45'
print(result.arcl)           # 40.996...
print(result.width_arcmin)   # 3.969...

# Positional unpacking works identically:
sunset, moonset, lag_time, moon_age, moon_alt, daz, arcv, arcl, width_arcm, width_arcs = result

```

---

### 🪶 Interpretation

* **Positive `moon_alt**`: Moon is above the horizon at sunset → *potentially visible*.
* **Positive `arcv**`: Moon sits higher than the setting Sun → improves sighting probability.
* **Higher `arcl` (elongation) & `width_arcmin**`: Crescent has sufficient width and separation to clear the Danjon limit (~7°–8°).
* `moonset` and `lag_time` will be `"—"` on dates where the moon does not set locally within the calendar day.

---

### 🗺️ Method 3: Global Visibility Maps (`globalvisibilitymap`)

Generate an ASCII/terminal-rendered global visibility map predicting crescent sighting zones:

```python
from falakpy import lunar

# Generate a map for Eid al-Fitr observation (e.g., 30 March 2025)
# Lowering LAT_RES and LON_RES speeds up computation (Default is 100x200)
df = lunar.globalvisibilitymap(year=2025, month=3, day=30, LAT_RES=100, LON_RES=200)

```

**Output:**

```text
Global Visibility MAP
┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌙 GLOBAL HILAL VISIBILITY MAP (ADJUSTED CRITERION)                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ DATE: 17 February 2026   |   RESOLUTION: 100x200   |   STATUS: COMPUTED      │
├──────────────────────────────────────────────────────────────────────────────┤
│  LAT                                                                         │
│  90°N │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  60°N │ ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  30°N │ ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│    0° │ ██████████████████████⭐░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  30°S │ ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  60°S │ ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  90°S │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│       └────────────────────────────────────────────────────────────────────│
│         180°W                90°W                  0°                 90°E   │
├──────────────────────────────────────────────────────────────────────────────┤
│ 📊 LEGEND & DATA POINTS:                                                     │
│  [ █ ] VISIBLE ZONE (Curve of Visibility)                                    │
│  [ ░ ] NOT VISIBLE                                                           │
│  [ ⭐ ] FIRST LAND SIGHTING -> 📍 Lat: 7.88°N, Lon: -60.57°E                  │
└──────────────────────────────────────────────────────────────────────────────┘

```

---

### 🌗 Method 4: Physical Contrast & Sky Brightness Modeling (`visibilitycontrast`)

The **`visibilitycontrast`** function evaluates the actual optical detection of the crescent (*hilal*) by modeling the physical luminance contrast between the lunar surface and the twilight sky background from sunset until moonset.

Instead of relying solely on geometric thresholds (such as MABIMS or Odeh geometric criteria), this function implements a physical and physiological model:

1. **Topocentric Crescent Luminance ($B_{\text{moon}}$):** Evaluates phase angle, illuminated area, extra-atmospheric crescent brightness, and four atmospheric extinction components ($k_R$ Rayleigh, $k_e$ aerosol, $k_o$ ozone, $k_W$ water vapor) derived from elevation, ambient temperature, and relative humidity.
2. **Twilight Sky Luminance ($B_{\text{sky}}$):** Evaluates twilight sky background brightness combined with local night-sky quality ($Z_{\text{lp}}$ in $\text{mag/arcsec}^2$).
3. **Contrast & Physiological Threshold:** Calculates the Weber contrast:

$$C = \frac{B_{\text{moon}} - B_{\text{sky}}}{B_{\text{sky}}}$$



and tests whether $C$ exceeds the contrast detection threshold ($C_{\text{th}}$) of the human eye for the topocentric crescent semidiameter at each minute after sunset.

#### ⚙️ Function Signature

```python
def visibilitycontrast(
    lat, long, year, month, day, ele, tz, 
    temperature_celcius, relative_humidity, 
    light_pollution_magsec, location
)

```

#### 📘 Parameter Breakdown

| Parameter | Type | Unit | Description | Example |
| --- | --- | --- | --- | --- |
| `lat` | `float` | Degrees | Observer latitude (°N positive, °S negative) | `-6.8247` |
| `long` | `float` | Degrees | Observer longitude (°E positive, °W negative) | `107.6171` |
| `year, month, day` | `int` | Date | Gregorian observation date | `2026, 4, 18` |
| `ele` | `float` | Meters | Elevation above sea level (m) | `1310.0` |
| `tz` | `float` / `int` | Hours | Timezone offset relative to UTC | `7` (UTC+7) |
| `temperature_celcius` | `float` | °C | Ambient surface temperature | `19.0` |
| `relative_humidity` | `float` | % | Relative humidity (0 to 100) | `75.0` |
| `light_pollution_magsec` | `float` | $\text{mag/arcsec}^2$ | Sky quality meter measurement (higher is darker; 21.8 = pristine, 18.0 = urban) | `19.8` |
| `location` | `str` | Text | Site label for plot titles and terminal logs | `"Bosscha Observatory"` |

#### 📤 Function Outputs & Side Effects

* **Console Logging:** Prints computed sunset/moonset times, lag time, visibility window duration, and visibility ratio ($T_{\text{vis}} / T_{\text{lag}}$).
* **CSV Export:** Automatically exports `twilight_sky_brightness_results.csv` with 1-minute steps for `[Time, Twilight Mag, Contrast, Contrast Threshold, Visibility]`.
* **Return Value:** Returns a `PIL.Image` object containing a semi-log plot comparing Moon/Sky Contrast ($C$) against the Visibility Threshold ($C_{\text{th}}$). The crescent is visible during intervals where the solid contrast curve rises above the dashed threshold curve.

---

#### 🔭 Contrast Example 1: Modern Observation (Bosscha Observatory, Indonesia)

```python
from falakpy import lunar

# Run contrast modeling for upcoming observation
plot_image = lunar.visibilitycontrast(
    lat=-6.8247,                 # Lembang, West Java (South is negative)
    long=107.6171,               # East is positive
    year=2026,
    month=4,
    day=18,
    ele=1310.0,                  # Highland elevation in meters
    tz=7,                        # Western Indonesia Time (UTC+7)
    temperature_celcius=19.0,    # Nighttime temperature
    relative_humidity=75.0,      # Relative humidity
    light_pollution_magsec=19.8, # Sub-urban night sky brightness
    location="Bosscha Observatory"
)

# Display or save the resulting plot
if plot_image:
    plot_image.show()
    plot_image.save("bosscha_visibility_curve.png")

```

---

#### 📜 Contrast Example 2: Ancient Historical Record (Tang Dynasty Imperial Skies)

Historical Chinese court astronomers at the imperial capital in **Luoyang** recorded early lunar crescent sightings (*chu chu*, 初朏) to calibrate imperial lunisolar calendars.

Because ancient observations took place prior to modern artificial lighting, `light_pollution_magsec` should be set to pristine natural levels (`~21.8–22.0 mag/arcsec²`), and the timezone approximates local mean solar time (UTC+7.5 for central China):

```python
from falakpy import lunar

# Historical astronomical verification: Luoyang Imperial Capital, 8th Century
plot_ancient = lunar.visibilitycontrast(
    lat=34.6200,                 # Ancient Luoyang Observatory (North)
    long=112.4500,               # Luoyang Longitude (East)
    year=755,                    # Tang Dynasty record
    month=9,
    day=11,
    ele=140.0,                   # Yellow River basin plain elevation (m)
    tz=7.5,                      # Local solar time approximation (UTC+7.5)
    temperature_celcius=21.0,    # Early autumn evening temperature
    relative_humidity=65.0,      # Atmospheric humidity
    light_pollution_magsec=21.9, # Natural pristine pre-industrial skyglow
    location="Luoyang Imperial Observatory (Tang Dynasty)"
)

if plot_ancient:
    plot_ancient.show()
    plot_ancient.save("luoyang_tang_dynasty_crescent.png")

```

---

## 👨‍💻 Author

**Dr. Muhamad Syazwan Faid**

Universiti Tun Hussein Onn Malaysia (UTHM)

📧 mdsyazwan@uthm.edu.my

---

## ⚖️ License

MIT License © 2025–2026

**Dr. Muhamad Syazwan Faid**

Universiti Tun Hussein Onn Malaysia (UTHM)

```

