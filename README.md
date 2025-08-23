# VEX Robotics Competition Analytics Engine

> Michael Lam, Team 86254, Hong Kong

Data-driven strategy development for VEX Robotics Competition through predictive modeling and match analysis. This tool was instrumental in our team's qualification for the **VEX Robotics World Championship 2025**.

## 🎯 Project Overview

This project develops analytical tools for VEX Robotics Competition (VRC) teams, featuring a **match strength prediction model** with **70%+ accuracy** and **0.6 correlation index** to actual score margins across 208 games. The system processes real-time data from official APIs to provide strategic insights for competition preparation.

**Proven Impact:** Our analysis directly supported **Team CAPMIL (86254B)** from Hong Kong, contributing to their successful qualification for the VEX Worlds Championship.

## 📊 Key Features & Proven Results

### Predictive Analytics
- **Match Outcome Prediction**: Machine learning model predicting match results with >70% accuracy
- **Strength Differential Analysis**: Correlation index of 0.6 between predicted and actual score margins
- **Strategic Prioritization**: Identifies high-stake matches where minimal strategic adjustments yield maximum impact

### Team Performance Analysis (Sample: Team 86254B)
| Metric | Value | Rank in Division | Top % |
| :--- | :--- | :--- | :--- |
| **Signature Event Win Rate** | **71.4%** | 9th | Top 18% |
| **Worlds Qualification Event** | **Tournament Champions** | Finals | Qualified |
| **Overall Win Rate** | 58.8% | 58th | Top 70% |

**Highlight:** The model helped analyze key performance indicators (KPIs) like Weighted Avg Score (30.3) and Win Margin (0.14), providing a strategic edge in alliance selection and match preparation.

## 🚀 Usage

Access analytical reports through the following endpoints:

| Report Type | URL Format | Description |
|-------------|------------|-------------|
| Team Match Analysis | `michael-ml7.github.io/vrc_teamanalysis/[team_number]_matches` | Detailed match performance for specific teams |
| Award History | `michael-ml7.github.io/vrc_teamanalysis/[team_number]_awards` | Comprehensive award tracking |
| Team Information | `michael-ml7.github.io/vrc_teamanalysis/inno` | Key team metadata and statistics |
| Division Analysis | `michael-ml7.github.io/vrc_teamanalysis/inno_matches` | Complete division match data with alliance advantage metrics |

## 📈 Model Performance

- **208 games analyzed** with predictive modeling
- **70%+ accuracy** in match outcome predictions
- **0.6 correlation index** between predicted and actual score margins
- **Strategic advantage** in allocating preparation time and resources

![Accuracy Analysis](graph_accuracy.png)
*Model accuracy across different tournament scenarios*

![Correlation Visualization](graph_correlation.png)
*Correlation between predicted strength differential and actual score margins*

## 🛠 Technical Implementation

- **Python**-based data processing and API integration
- **Machine Learning** models for predictive analytics
- **Statistical analysis** for correlation and trend identification
- **Web hosting** for accessible result visualization

## 📝 Application Note

This project demonstrates the practical application of data science and machine learning in competitive robotics, showcasing how algorithmic analysis can translate into real-world strategic advantages. The tools developed were directly used in our journey to qualify for and compete at the **VEX Robotics World Championship 2025**.

