# 🌐 AI-Driven Geospatial Analytics & Supply Chain Optimization
### Large-Scale Spatial Intelligence (21,000 Nodes) & Prescriptive Linear Programming (LP)

<div align="center">

[![Live Optimization Dashboard](https://img.shields.io/badge/Live_Demo-Optimization_Dashboard-2563eb?style=for-the-badge&logo=githubpages&logoColor=white)](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/)
[![Live GIS Web Map](https://img.shields.io/badge/Live_Demo-21k_Node_GIS_Map-22c55e?style=for-the-badge&logo=leaflet&logoColor=white)](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/map_visualization.html)
[![Optimization](https://img.shields.io/badge/Optimization-Gurobi_LP_Solver-E3242B?style=for-the-badge)](https://www.gurobi.com/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Geospatial](https://img.shields.io/badge/GIS-Leaflet_%26_Contextily-4285F4?style=for-the-badge)](https://leafletjs.com/)

<br/>

**[🚀 Launch Live Optimization & Analytics Dashboard](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/)** &bull; **[🗺️ Explore 21k Node GIS Demand Map](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/map_visualization.html)** &bull; **[📄 View Cartographic PDF](supply_chain_map.pdf)** &bull; **[📊 Jupyter Notebook Model](AI%20Jupyer%20Notebook%20Example%20-%20Supply_Chain_Planning.ipynb)**

</div>

---

## 📌 Executive Summary

This repository demonstrates an end-to-end **AI & Advanced Analytics Portfolio Project** showcasing how **AI-driven prescriptive optimization** and **large-scale geospatial data intelligence** solve complex enterprise logistics and network planning challenges.

### Core Pillars
1. **Prescriptive Mathematical Optimization (Gurobi LP)**: Solves multi-echelon continuous flow across suppliers, 3 factories, 2 operations, 5 warehouses (road & rail modes), and 9 regional consumer markets.
2. **Autonomous Dual Sensitivity & Shadow Price Analytics**: Automatically pinpoints binding operational bottlenecks, calculates the exact marginal value of plant debottlenecking ($506.15/unit ROI), and surfaces hidden trade-offs.
3. **Interactive Scenario Studio & What-If Simulator**: Real-time client-side simulation engine empowering executives to model tariffs, fuel price shocks, and overtime investments on the fly.
4. **Large-Scale Spatial Intelligence (21,000 Nodes)**: Big data geospatial pipeline engineering 20,999 customer delivery locations into publication-grade cartographic maps and a 60 FPS interactive Leaflet GIS canvas.

---

## ⚡ Skills & Efficiency with AI for Analytics

| Analytics Capability | Traditional Approach | AI & Optimization Approach | Business Impact |
| :--- | :--- | :--- | :--- |
| **Network Planning** | Manual trial-and-error heuristics or static spreadsheets | Continuous Linear Programming (LP) with Gurobi optimizer | Provably optimal cost-to-serve with zero guesswork across 222 decision variables |
| **Bottleneck Discovery** | Retrospective post-mortem after delays occur | Dual shadow price extraction ($\lambda_i$) directly from solver basis | Identifies Operation 1 capacity ceiling as the exact \$506.15/unit bottleneck |
| **Executive Decision Support** | Static static slides requiring days to recalculate | Dynamic What-If Scenario Studio with client-side solver | Instantaneous evaluation of supply shocks and overtime debottlenecking |
| **Geospatial Intelligence** | Low-resolution aggregated zip-code summaries | Sub-second rendering of 20,999 discrete GPS demand coordinates | Uncovers micro-corridors in Eastern UP and national outliers (Bangalore, Surat, Raipur) |

---

## 🎯 Key Optimization Findings & Strategic Insights

### 1. The Bottleneck: Operation 1 Capacity Ceiling
* **Total Demand**: 15.45 units (Product 1: 6.30 u, Product 2: 9.15 u).
* **Delivered**: 15.00 units (Service level: 97.1%).
* **Shortage**: 0.45 units in **Market 4 (Product 2)**.
* **The Cause**: All three manufacturing plants hit 100.0% max utilization on Operation 1 (5.0 units each, 15.00 unit total fleet ceiling).
* **The Penalty**: The 0.45 unit shortage triggers a **-$45.00k penalty**, depressing the net objective to **-$17.43k** despite a healthy **+$27.57k operating profit**.

### 2. High-ROI Overtime Strategy (+10% Capacity)
* The shadow price of Operation 1 is **+$506.15 / unit**.
* Expanding Operation 1 limit from 5.0 to 5.5 units per factory completely clears the 0.45 unit shortfall in Market 4.
* **Financial Impact**: Eliminates the \$45.00k penalty and swings net bottom-line earnings from **-$17.43k to +$28.18k (+$45.61k net turnaround)**.

### 3. Network Architecture & Direct Bypass
* **Warehouse Hub Modality**:
  * **W2 (Rail Mega-Hub)**: 3.70 units throughput (servicing M1, M3, M4).
  * **W4 (Road Mega-Hub)**: 3.70 units throughput (servicing M4, M5, M9).
  * **W1 & W5 (Regional Hubs)**: 1.30 units and 0.85 units respectively.
  * **W3 (Idle Hub)**: 0.00 units throughput (economically suboptimal).
* **Direct Factory Corridors**: Factory 1 ships 1.30 units directly to Market 2; Factory 3 ships 4.15 units directly to Markets 7 & 8, bypassing warehouses to minimize handling and freight fees.

---

## 🖥️ Live Interactive Deliverables

### 1. [Supply Chain Planning & Optimization Cockpit](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/)
* **Executive Overview & P&L**: Interactive financial waterfall bridge and delivered cost breakdown.
* **Multi-Echelon Network Flow**: Glowing interactive SVG diagram connecting suppliers, plants, warehouses, and markets.
* **Factory Fleet & Utilization**: Stacked capacity charts showing binding operations.
* **Warehouse Logistics & Freight**: Modal split breakdown (Road trucking vs. Rail freight).
* **Market Fulfillment Matrix**: 9-market demand, delivery, fill rates, and channel allocation.
* **Dual Sensitivity Analysis**: Shadow prices, constraint slacks, and reduced costs.
* **What-If Scenario Studio**: Real-time sliders for capacity, tariffs, raw material, and penalty multipliers.
* **Master Flow Ledger**: Filterable table with CSV export.

### 2. [21,000 Node Geospatial Demand GIS Map](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/map_visualization.html)
* **20,999 Discrete Customer Locations**: Interactive Leaflet canvas rendering 34,871.5 units of demand across India.
* **Dynamic Cartographic Controls**: Real-time radius scaling, demand-tier filtering, and Esri / OSM base layer toggles.
* **National Outlier Inset**: Highlights geographic reach across Eastern UP, Surat, Raipur, and Bangalore.

---

## 📂 Repository File Structure

```
├── index.html                            # Executive Optimization Dashboard (GitHub Pages entrypoint)
├── managerial_dashboard.html             # Standalone Executive Optimization Dashboard
├── map_visualization.html                # Interactive 21k Node Leaflet GIS web map
├── AI Jupyer Notebook Example...ipynb    # Gurobi Linear Programming supply chain model
├── generate_managerial_dashboard.py      # Python generator & Gurobi LP solver script
├── generate_map.py                       # Python pipeline generating 300 DPI map & PDF
├── AI for DS Sample Data.csv             # 20,999 geospatial customer delivery records
├── supply_chain_map.png                  # Publication-ready 300 DPI cartographic graphic
├── supply_chain_map.pdf                  # High-resolution vector PDF map
├── AI Hands-On Slides.pdf                # Executive optimization presentation deck
└── README.md                             # Project portfolio documentation
```

---

## 🚀 Quickstart & Reproduction

### 1. Clone the Repository
```bash
git clone https://github.com/devashishajaywork-stack/supply-chain-optimization-map.git
cd supply-chain-optimization-map
```

### 2. Install Python Dependencies
```bash
pip install gurobipy pandas numpy matplotlib contextily xyzservices
```

### 3. Run Optimization & Rebuild Dashboards
```bash
python generate_managerial_dashboard.py
python generate_map.py
```

### 4. Access Live Dashboards
* **Optimization Cockpit**: Visit **[devashishajaywork-stack.github.io/supply-chain-optimization-map](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/)**
* **Geospatial GIS Map**: Visit **[devashishajaywork-stack.github.io/supply-chain-optimization-map/map_visualization.html](https://devashishajaywork-stack.github.io/supply-chain-optimization-map/map_visualization.html)**

---

<div align="center">

Developed as an **AI for Data Science & Supply Chain Optimization Portfolio Project**  
*Demonstrating expertise in Mathematical Optimization, Spatial Big Data Analytics, and Analytics Engineering.*

</div>
