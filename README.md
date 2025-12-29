# VEX Robotics Competition Analytics Model

> Michael Lam, Programmer & Strategist, Team 86254, Hong Kong 🇭🇰

Data-driven strategy development for VEX Robotics Competition (HS) through predictive modeling and match analysis. This tool was instrumental in our team's preparation for the **VEX Robotics World Championship 2025** (High Stakes, 2425).

Repository and code: [https://github.com/Michael-ML7/vrc_teamanalysis](https://github.com/Michael-ML7/vrc_teamanalysis)

---

## 📋 Table of Contents
- [🎯 Project Overview](#-project-overview)
- [📊 Key Features & Methodology](#-key-features--methodology)
  - [📈 Strength Differential Predictive Analytics](#-strength-differential-predictive-analytics)
  - [🏆 Team Performance Analysis (Sample: Team 86254B)](#-team-performance-analysis-sample-team-86254b)
  - [📈 Normalized data for our team](#-normalized-data-for-our-team)
- [🚀 Usage](#-usage)
- [📈 Model Performance](#-model-performance)
- [🛠 Technical Implementation](#-technical-implementation)
- [📝 Application Note](#-application-note)

---

## 🎯 Project Overview

This project develops analytical tools for VEX Robotics Competition (VRC) teams, featuring a **match strength difference prediction model** with **70%+ accuracy** and **0.6 correlation index** to actual score margins across 208 games. It also provides a summary page for all the teams in Innovate Division, Worlds '25.

The system processes all recorded match data from all teams (recorded on [robotevents](https://www.robotevents.com)) across the entire High Stakes season from official APIs to calculate **weighted Key Performance Indicators (KPIs)** and then:

1. Computes a summary page for each team, showing KPI rankings
2. Computes a match strength difference prediction model for all matches (see [Strength Differential Predictive Analytics](#-strength-differential-predictive-analytics))

**Proven Impact:** The analysis directly supported our team, allowing us to allocate precious preparation time on games where small strategic gains matter most (actual *High Stake* games lol).

---

## 📊 Key Features & Methodology

Weighted KPIs are calculated for each team's every single match played in the High Stakes season. Matches of higher level of importance (regional / signature; qualifications / eliminations) are associated with larger weights.

### 📈 Strength Differential Predictive Analytics
Simple math model predicting match strength difference.

General Model: [inno_matches.ipynb](https://github.com/Michael-ML7/vrc_teamanalysis/blob/main/inno_matches.ipynb)

*Internal Model: [us_86254_matches.ipynb](https://github.com/Michael-ML7/vrc_teamanalysis/blob/main/us_86254_matches.ipynb)

#### Approach
1. **KPI Calculation**: Compute weighted performance metrics for every match, prioritizing high-stakes events
2. **Normalization**: Scale each KPI to [0,1] range using division-wide min-max values
3. **Radar Analysis**: Visualize alliance capabilities across 7 dimensions
4. **Predicted winner** is the alliance with greater area on the radar diagram
5. **Strength Calculation**: Predict outcomes based on comparative radar area
   - General Model: `Strength Differential = AreaRed - AreaBlue`
   - *Internal Model: `Normalized Differential = (AreaWinner - AreaLoser) / AreaOurAlliance`

#### Interpretation
- **Large magnitude** → Predicted decisive outcome
- **Small magnitude** → Predicted close match
- **Positive value** → Favors (general) Red / (internal) our alliance
- **Negative value** → Favors Blue / opponent alliance

### Example Predictions

| Match | Red Score | Blue Score | Red Alliance | Blue Alliance | General Model | *Internal Model |
|-------|-----------|------------|--------------|---------------|---------------|-----------------|
| Qualifier #41 | 27 | 44 | 719S, 12478X | 86254B, 3131V | **–0.775** | +0.445 |
| Qualifier #57 | 38 | 21 | 86254B, 19122B | 14241A, 3333W | **+0.252** | +0.163 |

*Normalized relative to our alliance for improved strategic accuracy

---

### 🏆 Team Performance Analysis (Sample: Team 86254B)
General info. Calculated KPIs from raw match data for each team. Generate rankings. Summarises major awards and how the team qualified for World Championship.

1. **Selected KPIs** shown (more are calculated and recorded in a .csv file, not shown):
   - All Win Rate
   - Weighted Avg For
   - Weighted Avg Against
   - Weighted Normalized Win Margin
   - Regional+ Win Rate
   - Signature+ Win Rate
   - Elim Win Rate

2. **Qualification Path** for World Championship
   *e.g. 2024-2025 PAS-VEX VEX V5 Robotics Competition Signature Event: High School*

3. **Signature Events** Participation
   Lists all sig. events the team has participated in and the **furthest round reached**

4. **Major Awards**
   Excellence Award / Tournament Champion / Regional Award, etc. are listed

---

## 🚀 Usage

Access analytical reports through the following endpoints:

| Report Type | URL Format | Description | Example |
|-------------|------------|-------------|---------|
| ⭐ **Team Analysis** | `michael-ml7.github.io/vrc_teamanalysis/[team_number]` | KPIs, respective rankings, high-level awards | [86254B](https://michael-ml7.github.io/vrc_teamanalysis/86254B) |
| ⭐ **Division Match Analysis** | `michael-ml7.github.io/vrc_teamanalysis/inno_matches` | Complete division match data with **alliance advantage metrics** | [inno_matches](https://michael-ml7.github.io/vrc_teamanalysis/inno_matches) |
| Team Match Analysis | `michael-ml7.github.io/vrc_teamanalysis/[team_number]_matches` | Pre-worlds match performance for all teams | [86254B_matches](https://michael-ml7.github.io/vrc_teamanalysis/86254B_matches) |
| Award History | `michael-ml7.github.io/vrc_teamanalysis/[team_number]_awards` | All pre-worlds award tracking | [86254B_awards](https://michael-ml7.github.io/vrc_teamanalysis/86254B_awards) |
| Strong Teams Information | `michael-ml7.github.io/vrc_teamanalysis/inno` | Identified strong teams in our division | [inno](https://michael-ml7.github.io/vrc_teamanalysis/inno) |

---

## 📈 Model Performance

> Detailed evaluation data can be downloaded from [this Excel file on Github](https://michael-ml7.github.io/vrc_teamanalysis/PostWorldsEval_reflection.xlsx)

**Across all 208 qualification games** played in the Innovate Division at Worlds '25:
- **70.67% accuracy** in predicting match winner
- **0.5995 correlation index** between predicted strength difference and actual score margins

![Correlation Analysis for all 208 matches in Innovate Division](https://michael-ml7.github.io/vrc_teamanalysis/PostWorldsEval_all_matches_plot.jpg)


**Across the 10 Qualification games our team played**
- **0.7984 correlation index** between predicted strength difference and actual score margins
 - ⭐ **CRITICAL** assistance in allocating match preparation time
- 80% outcome prediction accuracy
![Correlation Analysis for the 10 qualification matches played by our team, 86254B](https://michael-ml7.github.io/vrc_teamanalysis/PostWorldsEval_86254_matches_plot.jpg)

**Correlation between predict match strength difference and actual score margins were plotted and calculated with Excel*

---

## 🛠 Technical Implementation

- **Python**-based data processing and API integration
- **Web hosting on Github** for markdown files for easy and rapid access for all teammates on field

---

## 📝 Application Note

This project demonstrates the practical application of data science and mathematical modelling in competitive robotics, showcasing how algorithmic analysis can translate into real-world strategic advantages. The tools developed were directly used in our journey to compete at the **VEX Robotics World Championship 2025** in Dallas.