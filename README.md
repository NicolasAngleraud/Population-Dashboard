# Japan Population Dashboard

## 📊 Project Overview

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://japan-yearly-population-dashboard.streamlit.app/)

The Japan Population Dashboard app built with Streamlit provides insights into yearly population dynamics across different prefectures of Japan and nation wise between 1975 and 2023 as well as predictions for 2024.

---

## 📈 Data Sources

The dashboard draws the following data:
1. **Yearly Population data**: Data provides yearly prefecture population numbers between 1975 and 2023 from [e-Stat Portal Site of Official Statistics of Japan](https://dashboard.e-stat.go.jp/en/timeSeries).
2. **Japan GIS data**: Data includes geographical information for prefectures to include them in a map visualization from  [Simplemaps](https://simplemaps.com/gis/country/jp#admin1); license: Creative Commons Attribution 4.0.

---

## 🔄 Data Transformation

The raw data from various sources has been cleaned and processed to enable interactive visualization on Streamlit. Here’s a summary of the transformation steps:

- **Data Validation**: Handling potential missing values, duplicates, and format inconsistencies.
- **Aggregation**: Organized by prefecture and year.
- **Calculation**: Population difference between the current year and the previous year to get population dynamics.
- **Prediction**: Population figures for 2024 were predicted using Exponential Smoothing (ETS) models at prefecture level.

---

## 🗂️ Project Structure

- **`app.py`**: Main Streamlit app script that loads and visualizes the data.
- **`data/`**: Folder for storing data files used by the dashboard.
- **`requirements.txt`**: File listing necessary Python packages/libraries.

---

Code notebook for the project: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1-jcfI9QZlUJ0wEnR7H_hWE-cjK9gc5Qb?usp=sharing)

Inspiration of the project: [![Open in GitHub](https://img.shields.io/badge/Open%20in-GitHub-24292F?style=flat&logo=github)](https://github.com/dataprofessor/population-dashboard?tab=readme-ov-file)
