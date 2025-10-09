# 🌙 falakpy — Islamic Astronomy Toolkit for Python

[![PyPI version](https://img.shields.io/pypi/v/falakpy.svg)](https://pypi.org/project/falakpy/)
[![Python Version](https://img.shields.io/pypi/pyversions/falakpy.svg)](https://pypi.org/project/falakpy/)
[![License](https://img.shields.io/github/license/syazwanfaid/falakpy.svg)](https://github.com/syazwanfaid/falakpy)
[![Downloads](https://static.pepy.tech/badge/falakpy)](https://pepy.tech/project/falakpy)

**falakpy** is a Python package for **Islamic astronomical computations (ʿIlm al-Falak)** — covering  
🕋 *Qibla Direction*, 🕌 *Prayer Times*, and 🌙 *Lunar Observation Data*.  
It’s designed for students, researchers, and enthusiasts who wish to integrate classical *Falak* knowledge with modern astronomical computation via [Skyfield](https://rhodesmill.org/skyfield/).

---

## 🚀 Installation

Install directly from PyPI:

```bash
pip install falakpy


| Module               | Description                                                                                   |
| -------------------- | --------------------------------------------------------------------------------------------- |
| `falakpy.qibla`      | Compute Qibla direction (great-circle azimuth from observer to Kaabah).                       |
| `falakpy.prayertime` | Calculate prayer times (Subuh, Syuruk, Zuhur, Asar, Maghrib, Isyak).                          |
| `falakpy.lunar`      | Determine sunset, moonset, lag time, and visibility parameters (Arc of Vision, Arc of Light). |

```
## 💫 Quick Start Guide
# 🕋 falakpy

**falakpy** is a lightweight Python library for **Islamic Astronomy (Falak)** —  
designed for calculating **Qibla direction**, **Prayer Times**, and **Lunar (Hilal) data**  
using accurate astronomical algorithms.
````markdown
---

## ⚙️ Installation

```bash
pip install falakpy
````

---

## 🧭 Example 1: Qibla Direction

```python
from falakpy import qibla

latitude = 3.1390      # Kuala Lumpur latitude (°N → positive)
longitude = 101.6869   # Kuala Lumpur longitude (°E → positive)

s = qibla.direction(latitude, longitude)

print("Qibla (DMS):", s.degree)
print("Qibla (Decimal):", s.decimal)
```

### Output:

```
Qibla (DMS): 292° 60′ 0″
Qibla (Decimal): 292.7056910716602
```

### 📘 Variable Explanation

| Variable    | Meaning                                                     | Example                        |
| ----------- | ----------------------------------------------------------- | ------------------------------ |
| `latitude`  | Observer’s latitude (°N or °S) — **use negative for South** | `3.1390` (Kuala Lumpur)        |
| `longitude` | Observer’s longitude (°E or °W) — **use negative for West** | `101.6869` (East of Greenwich) |

📘 *This function calculates the great-circle direction to the Kaabah (21.4225° N, 39.8262° E).*

---

## 🕌 Example 2: Prayer Time Calculation

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

### Output:

```
Fajr     : 05:53
Sunrise  : 07:13
Dhuhr    : 13:26
Asr      : 16:46
Maghrib  : 19:28
Isha     : 20:41
```

### 📘 Variable Explanation

| Variable           | Meaning                                                 | Example          |
| ------------------ | ------------------------------------------------------- | ---------------- |
| `latitude`         | Your location’s latitude (°N or °S) — **S = negative**  | `3.1390`         |
| `longitude`        | Your location’s longitude (°E or °W) — **W = negative** | `101.6869`       |
| `elevation`        | Height above sea level (m)                              | `40`             |
| `timezone`         | UTC offset                                              | `8` for Malaysia |
| `year, month, day` | Gregorian date                                          | `2025, 1, 28`    |

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
prayertime.daily(51.5072, -0.1276, 25, 0, 2025, 1, 28)
```

*(Use negative latitude for South, and negative longitude for West.)*

---

## 🌙 Example 3: Lunar Observation Data

The **`lunar`** module provides parameters for **hilal (crescent moon) visibility**,
including sunset, moonset, lag time, moon age, altitude, and elongation angles.

```python
from falakpy import lunar

lunar.observedata(3, 101, 40.0, 8, 2025, 1, 28)
```

### Output:

```
+------------+----------+----------+----------+----------+----------+----------+----------+----------+
|    Date    |  Sunset  |  Moonset | LagTime  | MoonAge  | MoonAlt  |   DAZ    |   ArcV   |   ArcL   |
+------------+----------+----------+----------+----------+----------+----------+----------+----------+
| 2025-01-28 | 19:29:23 | 18:29:31 | 23:00:08 |   23.01  |  -13.98  |   7.50   |  12.95   |  14.92   |
+------------+----------+----------+----------+----------+----------+----------+----------+----------+
```

### 📘 Variable Explanation

| Variable           | Meaning                                            | Example                      |
| ------------------ | -------------------------------------------------- | ---------------------------- |
| `latitude`         | Observer’s latitude (°N or °S) — **S = negative**  | `3.0000` (North = positive)  |
| `longitude`        | Observer’s longitude (°E or °W) — **W = negative** | `101.0000` (East = positive) |
| `elevation`        | Height above sea level (m)                         | `40`                         |
| `timezone`         | UTC offset                                         | `8` for Malaysia             |
| `year, month, day` | Gregorian date of observation                      | `2025, 1, 28`                |

---

### 🪶 Interpretation

* **Positive MoonAlt** → Moon above horizon → *possible to observe*
* **Negative MoonAlt** → Moon set before sunset → *not visible*
* **Higher ArcL & ArcV** → Better visibility chance for crescent

---

## 📘 Module Summary

| Module       | Description                                                   |
| ------------ | ------------------------------------------------------------- |
| `qibla`      | Calculate Qibla direction using great-circle geometry         |
| `prayertime` | Compute daily prayer times for any location                   |
| `lunar`      | Compute hilal data: sunset, moonset, altitude, and visibility |

---

## 👨‍💻 Author

**Dr. Muhamad Syazwan Faid**
Universiti Tun Hussein Onn Malaysia (UTHM)
mdsyazwan@uthm.edu.my
---

## ⚖️ License

MIT License © 2025

**Dr. Muhamad Syazwan Faid**
Universiti Tun Hussein Onn Malaysia (UTHM)


