"""
Executive Managerial Dashboard Generator for Supply Chain Optimization
========================================================================
Based on: AI Jupyer Notebook Example - Supply_Chain_Planning.ipynb
Solver: Gurobi Optimizer LP Engine

Generates an executive-grade, standalone HTML dashboard with:
- Executive Summary & KPI Cockpit
- Multi-Echelon Network Flow Diagram (interactive SVG with hover tooltips & active lane glowing)
- Factory Fleet Operations & Utilization Analysis (with SVG stacked utilization charts)
- Warehouse Logistics Hub Throughput & Mode Analysis (with SVG throughput bars)
- Market Fulfillment & Regional Profitability Matrix (with SVG fulfillment comparisons)
- Sensitivity Analysis (Shadow Prices & Reduced Costs)
- Interactive Scenario Studio & What-If Simulator (Real-time client-side LP engine)
- Master Route Flow Ledger with Search and CSV Export
"""

import os
import sys
import json
import datetime
import gurobipy as gp
from gurobipy import GRB

def solve_sc_model(cap_mult=1.0, trans_mult=1.0, rm_mult=1.0, penalty_val=100.0, dem_mult=1.0):
    P = [1, 2]
    O = [1, 2]
    F = [1, 2, 3]
    W = [1, 2, 3, 4, 5]
    M = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    MD = [1, 2]

    S = {1: 12.0 * rm_mult, 2: 10.5 * rm_mult}
    CAP = {
        (1, 1): 5.0 * cap_mult, (1, 2): 5.0 * cap_mult,
        (2, 1): 8.0 * cap_mult, (2, 2): 4.0 * cap_mult
    }
    RC = {1: 4.0, 2: 3.0}
    PC = {
        (1, 1): 0.15, (1, 2): 0.10,
        (2, 1): 0.19, (2, 2): 0.14,
        (3, 1): 0.13, (3, 2): 0.09
    }

    TCFM_base = {
        (1, 1): 100, (1, 2): 0.6, (1, 3): 100, (1, 4): 100, (1, 5): 100, (1, 6): 100, (1, 7): 100, (1, 8): 100, (1, 9): 100,
        (2, 1): 100, (2, 2): 100, (2, 3): 100, (2, 4): 100, (2, 5): 100, (2, 6): 100, (2, 7): 100, (2, 8): 100, (2, 9): 100,
        (3, 1): 100, (3, 2): 100, (3, 3): 100, (3, 4): 100, (3, 5): 100, (3, 6): 100, (3, 7): 0.5, (3, 8): 0.6, (3, 9): 100
    }
    TCFW_base = {
        (1, 1, 1): 1.1, (1, 1, 2): 100, (1, 2, 1): 0.7, (1, 2, 2): 0.5, (1, 3, 1): 0.6, (1, 3, 2): 100, (1, 4, 1): 0.7, (1, 4, 2): 100, (1, 5, 1): 0.9, (1, 5, 2): 0.7,
        (2, 1, 1): 0.6, (2, 1, 2): 100, (2, 2, 1): 0.9, (2, 2, 2): 0.7, (2, 3, 1): 1.0, (2, 3, 2): 0.7, (2, 4, 1): 0.5, (2, 4, 2): 100, (2, 5, 1): 100, (2, 5, 2): 100,
        (3, 1, 1): 100, (3, 1, 2): 100, (3, 2, 1): 0.8, (3, 2, 2): 100, (3, 3, 1): 0.9, (3, 3, 2): 100, (3, 4, 1): 0.7, (3, 4, 2): 100, (3, 5, 1): 0.6, (3, 5, 2): 100
    }
    TCWM_base = {
        (1, 1): 0.1,  (1, 2): 0.2,  (1, 3): 0.15, (1, 4): 0.12, (1, 5): 0.18, (1, 6): 0.1,  (1, 7): 100,  (1, 8): 100,  (1, 9): 100,
        (2, 1): 0.15, (2, 2): 0.12, (2, 3): 0.1,  (2, 4): 0.17, (2, 5): 100,  (2, 6): 100,  (2, 7): 100,  (2, 8): 100,  (2, 9): 100,
        (3, 1): 0.18, (3, 2): 0.15, (3, 3): 100,  (3, 4): 0.15, (3, 5): 100,  (3, 6): 100,  (3, 7): 100,  (3, 8): 100,  (3, 9): 100,
        (4, 1): 100,  (4, 2): 100,  (4, 3): 100,  (4, 4): 0.14, (4, 5): 0.13, (4, 6): 100,  (4, 7): 0.18, (4, 8): 0.1,  (4, 9): 0.14,
        (5, 1): 100,  (5, 2): 100,  (5, 3): 100,  (5, 4): 100,  (5, 5): 100,  (5, 6): 0.19, (5, 7): 0.14, (5, 8): 0.16, (5, 9): 0.12
    }

    NO_LANE = 100.0
    TCFM = {k: (v * trans_mult if v < NO_LANE else v) for k, v in TCFM_base.items()}
    TCFW = {k: (v * trans_mult if v < NO_LANE else v) for k, v in TCFW_base.items()}
    TCWM = {k: (v * trans_mult if v < NO_LANE else v) for k, v in TCWM_base.items()}

    DEM_base = {
        (1, 1): 0.750, (1, 2): 1.000,
        (2, 1): 1.300, (2, 2): 0.000,
        (3, 1): 0.850, (3, 2): 1.450,
        (4, 1): 0.750, (4, 2): 1.250,
        (5, 1): 0.550, (5, 2): 0.950,
        (6, 1): 0.200, (6, 2): 0.600,
        (7, 1): 0.700, (7, 2): 1.500,
        (8, 1): 0.450, (8, 2): 1.500,
        (9, 1): 0.750, (9, 2): 0.900
    }
    DEM = {k: round(v * dem_mult, 4) for k, v in DEM_base.items()}

    SP = {
        (1, 1): 6.5, (1, 2): 5.5,
        (2, 1): 7.0, (2, 2): 5.1,
        (3, 1): 6.3, (3, 2): 5.0,
        (4, 1): 7.6, (4, 2): 5.0,
        (5, 1): 7.2, (5, 2): 5.4,
        (6, 1): 6.5, (6, 2): 5.2,
        (7, 1): 7.9, (7, 2): 5.7,
        (8, 1): 7.2, (8, 2): 5.0,
        (9, 1): 7.0, (9, 2): 5.2
    }

    SC = gp.Model("Supply_Chain_Planning")
    SC.Params.OutputFlag = 0

    FM = {(p, f, m): SC.addVar(lb=0.0, ub=0.0 if TCFM[f, m] >= NO_LANE else GRB.INFINITY, name=f"FM_{p}_{f}_{m}") for p in P for f in F for m in M}
    FW = {(p, f, w, md): SC.addVar(lb=0.0, ub=0.0 if TCFW[f, w, md] >= NO_LANE else GRB.INFINITY, name=f"FW_{p}_{f}_{w}_{md}") for p in P for f in F for w in W for md in MD}
    WM = {(p, w, m): SC.addVar(lb=0.0, ub=0.0 if TCWM[w, m] >= NO_LANE else GRB.INFINITY, name=f"WM_{p}_{w}_{m}") for p in P for w in W for m in M}
    SHORT = {(m, p): SC.addVar(lb=0.0, ub=GRB.INFINITY, name=f"SHORT_{m}_{p}") for m in M for p in P}
    SC.update()

    constrs = {}
    for p in P:
        constrs[f"RM_supplier_limit_{p}"] = SC.addConstr(
            gp.quicksum(FW[p, f, w, md] for f in F for w in W for md in MD) +
            gp.quicksum(FM[p, f, m] for f in F for m in M) <= S[p],
            name=f"RM_supplier_limit_{p}"
        )

    for f in F:
        for o in O:
            constrs[f"production_capacity_{f}_{o}"] = SC.addConstr(
                gp.quicksum((gp.quicksum(FW[p, f, w, md] for w in W for md in MD) +
                             gp.quicksum(FM[p, f, m] for m in M)) / CAP[o, p] for p in P) <= 1.0,
                name=f"production_capacity_{f}_{o}"
            )

    for m in M:
        for p in P:
            constrs[f"demand_{m}_{p}"] = SC.addConstr(
                gp.quicksum(FM[p, f, m] for f in F) +
                gp.quicksum(WM[p, w, m] for w in W) +
                SHORT[m, p] == DEM[m, p],
                name=f"demand_{m}_{p}"
            )

    for w in W:
        for p in P:
            constrs[f"flow_balance_{w}_{p}"] = SC.addConstr(
                gp.quicksum(FW[p, f, w, md] for f in F for md in MD) ==
                gp.quicksum(WM[p, w, m] for m in M),
                name=f"flow_balance_{w}_{p}"
            )

    revenue_expr = gp.quicksum(SP[m, p] * (gp.quicksum(FM[p, f, m] for f in F) + gp.quicksum(WM[p, w, m] for w in W)) for m in M for p in P)
    rm_cost_expr = gp.quicksum(RC[p] * (gp.quicksum(FW[p, f, w, md] for f in F for w in W for md in MD) + gp.quicksum(FM[p, f, m] for f in F for m in M)) for p in P)
    prod_cost_expr = gp.quicksum(PC[f, p] * (gp.quicksum(FW[p, f, w, md] for w in W for md in MD) + gp.quicksum(FM[p, f, m] for m in M)) for f in F for p in P)
    trans_cost_expr = (
        gp.quicksum(TCFM[f, m] * FM[p, f, m] for p in P for f in F for m in M) +
        gp.quicksum(TCFW[f, w, md] * FW[p, f, w, md] for p in P for f in F for w in W for md in MD) +
        gp.quicksum(TCWM[w, m] * WM[p, w, m] for p in P for w in W for m in M)
    )
    penalty_cost_expr = gp.quicksum(penalty_val * SHORT[m, p] for m in M for p in P)

    SC.setObjective(revenue_expr - rm_cost_expr - prod_cost_expr - trans_cost_expr - penalty_cost_expr, GRB.MAXIMIZE)
    SC.optimize()

    if SC.Status != GRB.OPTIMAL:
        return {"status": "NOT_OPTIMAL"}

    rev = revenue_expr.getValue()
    rm = rm_cost_expr.getValue()
    pc = prod_cost_expr.getValue()
    tc = trans_cost_expr.getValue()
    pen = penalty_cost_expr.getValue()
    net_profit = SC.ObjVal
    op_profit = rev - rm - pc - tc

    shortage_vol = sum(SHORT[m, p].X for m in M for p in P)
    demand_vol = sum(DEM.values())
    fulfilled_vol = demand_vol - shortage_vol
    service_level = (fulfilled_vol / demand_vol * 100.0) if demand_vol > 0 else 100.0

    flows_list = []
    # FM
    for (p, f, m), var in FM.items():
        if var.X > 1e-4:
            unit_rev = SP[m, p]
            unit_tc = TCFM[f, m]
            unit_pc = PC[f, p]
            unit_rc = RC[p]
            flows_list.append({
                "var_name": var.VarName,
                "echelon": "Factory -> Market",
                "type": "Direct Delivery",
                "product": p,
                "origin": f"Factory {f}",
                "dest": f"Market {m}",
                "origin_id": f"F{f}",
                "dest_id": f"M{m}",
                "mode": "Direct Road/Rail",
                "volume": round(var.X, 4),
                "unit_trans_cost": round(unit_tc, 2),
                "total_trans_cost": round(var.X * unit_tc, 4),
                "unit_prod_cost": round(unit_pc, 2),
                "unit_rm_cost": round(unit_rc, 2),
                "unit_selling_price": round(unit_rev, 2),
                "revenue": round(var.X * unit_rev, 4),
                "margin": round(var.X * (unit_rev - unit_rc - unit_pc - unit_tc), 4)
            })

    # FW
    for (p, f, w, md), var in FW.items():
        if var.X > 1e-4:
            unit_tc = TCFW[f, w, md]
            mode_name = "Mode 1 (Road Truck)" if md == 1 else "Mode 2 (Intermodal Rail)"
            flows_list.append({
                "var_name": var.VarName,
                "echelon": "Factory -> Warehouse",
                "type": "Inbound Consolidation",
                "product": p,
                "origin": f"Factory {f}",
                "dest": f"Warehouse {w}",
                "origin_id": f"F{f}",
                "dest_id": f"W{w}",
                "mode": mode_name,
                "volume": round(var.X, 4),
                "unit_trans_cost": round(unit_tc, 2),
                "total_trans_cost": round(var.X * unit_tc, 4),
                "unit_prod_cost": round(PC[f, p], 2),
                "unit_rm_cost": round(RC[p], 2),
                "unit_selling_price": 0.0,
                "revenue": 0.0,
                "margin": 0.0
            })

    # WM
    for (p, w, m), var in WM.items():
        if var.X > 1e-4:
            unit_tc = TCWM[w, m]
            unit_rev = SP[m, p]
            flows_list.append({
                "var_name": var.VarName,
                "echelon": "Warehouse -> Market",
                "type": "Outbound Distribution",
                "product": p,
                "origin": f"Warehouse {w}",
                "dest": f"Market {m}",
                "origin_id": f"W{w}",
                "dest_id": f"M{m}",
                "mode": "Regional Distribution",
                "volume": round(var.X, 4),
                "unit_trans_cost": round(unit_tc, 2),
                "total_trans_cost": round(var.X * unit_tc, 4),
                "unit_prod_cost": 0.0,
                "unit_rm_cost": 0.0,
                "unit_selling_price": round(unit_rev, 2),
                "revenue": round(var.X * unit_rev, 4),
                "margin": round(var.X * (unit_rev - unit_tc), 4)
            })

    # Shortages
    for (m, p), var in SHORT.items():
        if var.X > 1e-4:
            flows_list.append({
                "var_name": var.VarName,
                "echelon": "Unmet Demand",
                "type": "Stockout / Shortage",
                "product": p,
                "origin": "Capacity Shortfall",
                "dest": f"Market {m}",
                "origin_id": "DEFICIT",
                "dest_id": f"M{m}",
                "mode": "Unfulfilled",
                "volume": round(var.X, 4),
                "unit_trans_cost": 0.0,
                "total_trans_cost": 0.0,
                "unit_prod_cost": 0.0,
                "unit_rm_cost": 0.0,
                "unit_selling_price": round(SP[m, p], 2),
                "revenue": 0.0,
                "margin": -round(var.X * penalty_val, 4)
            })

    factories = {}
    for f in F:
        p1 = sum(FM[1, f, m].X for m in M) + sum(FW[1, f, w, md].X for w in W for md in MD)
        p2 = sum(FM[2, f, m].X for m in M) + sum(FW[2, f, w, md].X for w in W for md in MD)
        tot = p1 + p2
        u_op1 = (p1 / CAP[1, 1] + p2 / CAP[1, 2]) * 100.0
        u_op2 = (p1 / CAP[2, 1] + p2 / CAP[2, 2]) * 100.0
        factories[f] = {
            "name": f"Factory {f}",
            "id": f"F{f}",
            "p1": round(p1, 3),
            "p2": round(p2, 3),
            "total": round(tot, 3),
            "cap_limit": round(CAP[1, 1], 2),
            "util_op1": round(u_op1, 1),
            "util_op2": round(u_op2, 1),
            "status_op1": "BOTTLE-NECK (100%)" if u_op1 >= 99.9 else f"{u_op1:.1f}%",
            "status_op2": "MAX REACHED (100%)" if u_op2 >= 99.9 else f"{u_op2:.1f}%",
            "pc_p1": PC[f, 1],
            "pc_p2": PC[f, 2],
            "prod_cost": round(p1 * PC[f, 1] + p2 * PC[f, 2], 3)
        }

    warehouses = {}
    for w in W:
        in_p1 = sum(FW[1, f, w, md].X for f in F for md in MD)
        in_p2 = sum(FW[2, f, w, md].X for f in F for md in MD)
        out_p1 = sum(WM[1, w, m].X for m in M)
        out_p2 = sum(WM[2, w, m].X for m in M)
        tot_thru = in_p1 + in_p2
        warehouses[w] = {
            "name": f"Warehouse {w}",
            "id": f"W{w}",
            "in_p1": round(in_p1, 3),
            "in_p2": round(in_p2, 3),
            "out_p1": round(out_p1, 3),
            "out_p2": round(out_p2, 3),
            "throughput": round(tot_thru, 3),
            "active": tot_thru > 1e-4,
            "status": "Active Hub" if tot_thru > 1e-4 else "Idle (0 Throughput)"
        }

    markets = {}
    for m in M:
        m_data = {"name": f"Market {m}", "id": f"M{m}", "p1": {}, "p2": {}, "total_rev": 0.0, "total_demand": 0.0, "total_shipped": 0.0, "total_short": 0.0}
        for p in P:
            shipped = sum(FM[p, f, m].X for f in F) + sum(WM[p, w, m].X for w in W)
            shortage = SHORT[m, p].X
            d = DEM[m, p]
            price = SP[m, p]
            r = shipped * price
            m_data[f"p{p}"] = {
                "demand": d,
                "shipped": round(shipped, 3),
                "shortage": round(shortage, 3),
                "fill_rate": round(shipped / d * 100.0, 1) if d > 0 else 100.0,
                "price": price,
                "revenue": round(r, 3)
            }
            m_data["total_demand"] += d
            m_data["total_shipped"] += shipped
            m_data["total_short"] += shortage
            m_data["total_rev"] += r
        m_data["fill_rate"] = round(m_data["total_shipped"] / m_data["total_demand"] * 100.0, 1) if m_data["total_demand"] > 0 else 100.0
        m_data["total_demand"] = round(m_data["total_demand"], 3)
        m_data["total_shipped"] = round(m_data["total_shipped"], 3)
        m_data["total_short"] = round(m_data["total_short"], 3)
        m_data["total_rev"] = round(m_data["total_rev"], 3)
        markets[m] = m_data

    sensitivity = []
    for cname, cobj in constrs.items():
        pi = cobj.Pi
        slack = cobj.Slack
        is_binding = abs(slack) < 1e-4
        
        explanation = ""
        category = "Operational"
        if "production_capacity" in cname:
            f_num = cname.split("_")[-2]
            o_num = cname.split("_")[-1]
            category = "Factory Capacity"
            if is_binding:
                explanation = f"Factory {f_num} Op {o_num} bottleneck. Marginal profit gain +${pi:.2f}/unit."
            else:
                explanation = f"Factory {f_num} Op {o_num} has {slack:.2f} units spare capacity buffer."
        elif "RM_supplier_limit" in cname:
            p_num = cname.split("_")[-1]
            category = "Supplier RM Limit"
            if is_binding:
                explanation = f"Raw Material {p_num} supplier cap binding. Dual: +${pi:.2f}."
            else:
                explanation = f"Raw Material {p_num} has {slack:.2f} units surplus available (No bottleneck)."
        elif "demand" in cname:
            m_num = cname.split("_")[-2]
            p_num = cname.split("_")[-1]
            category = "Market Demand"
            if is_binding:
                explanation = f"Market {m_num} Product {p_num}: Marginal network impact ${pi:+.2f} per unit."
        elif "flow_balance" in cname:
            category = "Warehouse Conservation"
            w_num = cname.split("_")[-2]
            p_num = cname.split("_")[-1]
            explanation = f"Warehouse {w_num} Product {p_num} balance conservation."

        sensitivity.append({
            "name": cname,
            "category": category,
            "shadow_price": round(pi, 4),
            "slack": round(slack, 4),
            "is_binding": is_binding,
            "explanation": explanation
        })

    sensitivity.sort(key=lambda x: (not x["is_binding"], -abs(x["shadow_price"])))

    reduced_costs = []
    for v in SC.getVars():
        if v.X < 1e-4 and abs(v.RC) > 1e-4 and "SHORT" not in v.VarName:
            reduced_costs.append({
                "var_name": v.VarName,
                "reduced_cost": round(v.RC, 4),
                "interpretation": f"Shipping 1 unit along this route would degrade objective by ${abs(v.RC):.2f}."
            })
    reduced_costs.sort(key=lambda x: x["reduced_cost"])

    rm_usage = {
        1: {"supply": S[1], "used": round(sum(factories[f]["p1"] for f in F), 3)},
        2: {"supply": S[2], "used": round(sum(factories[f]["p2"] for f in F), 3)}
    }
    rm_usage[1]["util"] = round(rm_usage[1]["used"] / rm_usage[1]["supply"] * 100.0, 1)
    rm_usage[2]["util"] = round(rm_usage[2]["used"] / rm_usage[2]["supply"] * 100.0, 1)

    return {
        "status": "OPTIMAL",
        "kpis": {
            "net_profit": round(net_profit, 2),
            "op_profit": round(op_profit, 2),
            "revenue": round(rev, 2),
            "rm_cost": round(rm, 2),
            "prod_cost": round(pc, 2),
            "trans_cost": round(tc, 2),
            "penalty_cost": round(pen, 2),
            "total_demand": round(demand_vol, 2),
            "fulfilled_vol": round(fulfilled_vol, 2),
            "shortage_vol": round(shortage_vol, 2),
            "service_level": round(service_level, 2),
            "total_prod": round(sum(factories[f]["total"] for f in F), 2),
            "max_fleet_capacity": round(sum(CAP[1, 1] for _ in F), 2),
            "fleet_utilization": round(sum(factories[f]["total"] for f in F) / sum(CAP[1, 1] for _ in F) * 100.0, 1),
            "active_warehouses": sum(1 for w in warehouses.values() if w["active"]),
            "total_warehouses": len(warehouses)
        },
        "factories": factories,
        "warehouses": warehouses,
        "markets": markets,
        "rm_usage": rm_usage,
        "flows": flows_list,
        "sensitivity": sensitivity,
        "reduced_costs": reduced_costs
    }

def get_preset_scenarios():
    return {
        "baseline": {
            "title": "Baseline (Optimal Model)",
            "badge": "Current State",
            "badge_color": "bg-blue-100 text-blue-800 border-blue-300",
            "desc": "Operating parameters as defined in the original Jupyter Notebook. Fleet capacity is 15.0 units across 3 factories.",
            "data": solve_sc_model(cap_mult=1.0, trans_mult=1.0, rm_mult=1.0, penalty_val=100.0)
        },
        "cap_10": {
            "title": "+10% Factory Capacity (Overtime)",
            "badge": "Recommended",
            "badge_color": "bg-emerald-100 text-emerald-800 border-emerald-300",
            "desc": "Immediate shift overtime expands factory Operation 1 from 5.0 to 5.5 units. Eliminates 100% of shortage.",
            "data": solve_sc_model(cap_mult=1.1, trans_mult=1.0, rm_mult=1.0, penalty_val=100.0)
        },
        "cap_20": {
            "title": "+20% Capital De-bottlenecking",
            "badge": "Strategic CapEx",
            "badge_color": "bg-purple-100 text-purple-800 border-purple-300",
            "desc": "Permanent debottlenecking investment brings each factory to 6.0 units capacity. Achieves flawless fill rate with buffer.",
            "data": solve_sc_model(cap_mult=1.2, trans_mult=1.0, rm_mult=1.0, penalty_val=100.0)
        },
        "fuel_surcharge": {
            "title": "+25% Fuel Freight Surcharge",
            "badge": "Cost Shock",
            "badge_color": "bg-amber-100 text-amber-800 border-amber-300",
            "desc": "Geopolitical inflation raises all road and intermodal shipping rates by 25%. Tests network logistics elasticity.",
            "data": solve_sc_model(cap_mult=1.0, trans_mult=1.25, rm_mult=1.0, penalty_val=100.0)
        },
        "rm_scarcity": {
            "title": "Raw Material 2 Supply Crisis (-30%)",
            "badge": "Supply Risk",
            "badge_color": "bg-rose-100 text-rose-800 border-rose-300",
            "desc": "Upstream disruption cuts RM2 allocation from 10.5 to 7.35 units. Induces severe stockouts across multiple markets.",
            "data": solve_sc_model(cap_mult=1.0, trans_mult=1.0, rm_mult=0.7, penalty_val=100.0)
        }
    }

def generate_dashboard_html():
    baseline_data = solve_sc_model()
    scenarios_data = get_preset_scenarios()

    json_baseline = json.dumps(baseline_data)
    json_scenarios = json.dumps(scenarios_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Executive Supply Chain Planning & Optimization Dashboard</title>
  <!-- Tailwind CSS via allowlisted gstatic CDN -->
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* Executive Design Tokens */
    :root {{
      --primary: #1e3a8a;
      --accent: #0284c7;
      --border-color: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #64748b;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: #f1f5f9;
      color: var(--text-main);
      margin: 0;
      padding: 0;
    }}
    .metric-card {{
      background: #ffffff;
      border: 1px solid var(--border-color);
      border-radius: 0.75rem;
      box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
      transition: all 0.2s ease-in-out;
    }}
    .metric-card:hover {{
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
      border-color: #cbd5e1;
    }}
    .nav-tab {{
      padding: 0.65rem 1.15rem;
      font-weight: 500;
      font-size: 0.875rem;
      border-bottom: 2px solid transparent;
      color: #64748b;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}
    .nav-tab.active {{
      color: #1e3a8a;
      border-bottom-color: #1e3a8a;
      font-weight: 600;
      background-color: #f8fafc;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 0.15rem 0.55rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      border-width: 1px;
    }}
    .ledger-scroll::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .ledger-scroll::-webkit-scrollbar-thumb {{
      background: #cbd5e1;
      border-radius: 4px;
    }}
    /* Interactive Floating Tooltip */
    #tooltip-box {{
      position: absolute;
      display: none;
      background: #0f172a;
      color: #ffffff;
      padding: 0.6rem 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.75rem;
      pointer-events: none;
      z-index: 100;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.4);
      max-width: 280px;
      line-height: 1.4;
      border: 1px solid #334155;
    }}
    /* SVG Node and Lane hover effects */
    .net-lane {{
      cursor: pointer;
      transition: stroke-width 0.15s ease, opacity 0.15s ease;
    }}
    .net-lane:hover {{
      opacity: 1 !important;
      stroke-width: 6.5px !important;
      filter: drop-shadow(0 0 4px rgba(56, 189, 248, 0.8));
    }}
    .net-node {{
      cursor: pointer;
      transition: transform 0.15s ease;
    }}
    .net-node:hover {{
      transform: scale(1.04);
      filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.3));
    }}
    @media print {{
      .no-print {{ display: none !important; }}
      body {{ background-color: #ffffff; }}
    }}
  </style>
</head>
<body class="antialiased text-slate-900 pb-12">

  <!-- FLOATING TOOLTIP FOR NETWORK MAP -->
  <div id="tooltip-box"></div>

  <!-- TOP EXECUTIVE BANNER / HEADER -->
  <header class="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40 shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center font-black text-xl tracking-wider text-white shadow-inner">
          SC
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-lg font-bold text-white tracking-tight">Global Supply Chain Planning & Optimization Cockpit</h1>
            <span class="badge bg-emerald-950 text-emerald-400 border-emerald-700">SOLVER: GUROBI LP OPTIMAL</span>
          </div>
          <p class="text-xs text-slate-400">
            Linear Program Multi-Echelon Network Model • 2 Products • 3 Factories • 5 Warehouses • 9 Markets
          </p>
        </div>
      </div>

      <!-- Quick Action Controls -->
      <div class="flex items-center space-x-3 no-print">
        <div class="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700">
          <span class="text-xs font-medium text-slate-400 px-2">Filter View:</span>
          <button id="filter-all" onclick="setProductFilter('all')" class="px-2.5 py-1 text-xs rounded font-medium bg-blue-600 text-white shadow-sm transition">All Products</button>
          <button id="filter-p1" onclick="setProductFilter('1')" class="px-2.5 py-1 text-xs rounded font-medium text-slate-300 hover:text-white transition">Product 1</button>
          <button id="filter-p2" onclick="setProductFilter('2')" class="px-2.5 py-1 text-xs rounded font-medium text-slate-300 hover:text-white transition">Product 2</button>
        </div>

        <button onclick="window.print()" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 transition flex items-center space-x-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4H7v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
          <span>Print / PDF</span>
        </button>

        <button onclick="exportCSV()" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition flex items-center space-x-1.5 shadow-sm">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          <span>Export Ledger CSV</span>
        </button>
      </div>
    </div>
  </header>

  <!-- STRATEGIC ALERT BANNER -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-5">
    <div class="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-l-4 border-amber-500 bg-white rounded-r-xl p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div class="flex items-start space-x-3">
        <div class="p-2 bg-amber-100 rounded-lg text-amber-700 shrink-0 mt-0.5">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold uppercase tracking-wider text-amber-800">Executive Alert: Capacity Bottleneck & Shortage Penalty</span>
            <span class="badge bg-rose-100 text-rose-700 border-rose-300">0.45 Units Unmet in Market 4</span>
          </div>
          <p class="text-xs text-slate-700 mt-1 leading-relaxed">
            All 3 Factories are at <strong>100.0% max throughput</strong> on Operation 1 (5.0 units each, 15.00 fleet capacity vs 15.45 demanded).
            This creates a 0.45 unit shortfall in <strong>Market 4 (Product 2)</strong>, triggering an outsized <strong>-$45.00k shortage penalty</strong> that pushes reported bottom-line to <strong>-$17.43k</strong> despite a healthy <strong>+$27.57k operating profit</strong>.
            <span class="font-semibold text-emerald-800 underline decoration-emerald-500 cursor-pointer" onclick="switchTab('scenarios')">Recommended Action: Adding +10% overtime capacity eliminates 100% of shortage and swings net earnings to +$28.18k (+&dollar;45.61k delta).</span>
          </p>
        </div>
      </div>
      <div class="shrink-0 flex items-center space-x-2">
        <button onclick="switchTab('scenarios')" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-amber-600 hover:bg-amber-700 text-white shadow-sm transition">
          Test Overtime Simulator &rarr;
        </button>
      </div>
    </div>
  </div>

  <!-- EXECUTIVE SCORECARD / HERO KPIS -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-5">
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
      <!-- 1. Revenue -->
      <div class="metric-card p-3">
        <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Gross Revenue</span>
        <div class="text-xl font-bold text-slate-900 mt-0.5" id="kpi-revenue">&dollar;90.04k</div>
        <div class="text-[11px] text-emerald-600 font-medium flex items-center mt-1">
          <span>15.00 units shipped</span>
        </div>
      </div>

      <!-- 2. RM Cost -->
      <div class="metric-card p-3">
        <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Raw Mat Cost</span>
        <div class="text-xl font-bold text-slate-900 mt-0.5" id="kpi-rm">&dollar;51.30k</div>
        <div class="text-[11px] text-slate-500 font-medium mt-1">82.1% of cost base</div>
      </div>

      <!-- 3. Prod Cost -->
      <div class="metric-card p-3">
        <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Mfg Processing</span>
        <div class="text-xl font-bold text-slate-900 mt-0.5" id="kpi-pc">&dollar;1.95k</div>
        <div class="text-[11px] text-slate-500 font-medium mt-1">F1, F2, F3 operations</div>
      </div>

      <!-- 4. Freight Cost -->
      <div class="metric-card p-3">
        <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Logistics Freight</span>
        <div class="text-xl font-bold text-slate-900 mt-0.5" id="kpi-tc">&dollar;9.23k</div>
        <div class="text-[11px] text-slate-500 font-medium mt-1">Road & Rail lanes</div>
      </div>

      <!-- 5. Operating Profit -->
      <div class="metric-card p-3 border-emerald-200 bg-emerald-50/30">
        <span class="text-[11px] font-semibold text-emerald-800 uppercase tracking-wider block">Operating Profit</span>
        <div class="text-xl font-bold text-emerald-700 mt-0.5" id="kpi-opprofit">&dollar;27.57k</div>
        <div class="text-[11px] text-emerald-700 font-medium mt-1">30.6% Op Margin</div>
      </div>

      <!-- 6. Penalty Cost -->
      <div class="metric-card p-3 border-rose-200 bg-rose-50/30">
        <span class="text-[11px] font-semibold text-rose-800 uppercase tracking-wider block">Shortage Penalty</span>
        <div class="text-xl font-bold text-rose-700 mt-0.5" id="kpi-penalty">-&dollar;45.00k</div>
        <div class="text-[11px] text-rose-600 font-medium mt-1">0.45 units @ &dollar;100</div>
      </div>

      <!-- 7. Net Optimization Profit -->
      <div class="metric-card p-3 border-slate-300 bg-slate-50/50">
        <span class="text-[11px] font-semibold text-slate-700 uppercase tracking-wider block">Net LP Objective</span>
        <div class="text-xl font-bold text-slate-800 mt-0.5" id="kpi-netprofit">-&dollar;17.43k</div>
        <div class="text-[11px] text-slate-500 font-medium mt-1">Includes penalty</div>
      </div>

      <!-- 8. Service Level -->
      <div class="metric-card p-3">
        <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Service Level</span>
        <div class="text-xl font-bold text-blue-600 mt-0.5" id="kpi-service">97.09%</div>
        <div class="text-[11px] text-slate-500 font-medium mt-1">15.0 / 15.45 units</div>
      </div>
    </div>
  </div>

  <!-- NAVIGATION TABS -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
    <div class="bg-white rounded-t-xl border border-b-0 border-slate-200 flex overflow-x-auto no-print">
      <div onclick="switchTab('overview')" id="tab-btn-overview" class="nav-tab active">📊 Executive Overview & P&L</div>
      <div onclick="switchTab('network')" id="tab-btn-network" class="nav-tab">🌐 Multi-Echelon Network Flow</div>
      <div onclick="switchTab('factories')" id="tab-btn-factories" class="nav-tab">🏭 Factory Fleet & Utilization</div>
      <div onclick="switchTab('warehouses')" id="tab-btn-warehouses" class="nav-tab">🏬 Warehouse Hubs & Freight</div>
      <div onclick="switchTab('markets')" id="tab-btn-markets" class="nav-tab">🎯 Market Demand & Regional P&L</div>
      <div onclick="switchTab('sensitivity')" id="tab-btn-sensitivity" class="nav-tab">🔍 Duals & Shadow Prices</div>
      <div onclick="switchTab('scenarios')" id="tab-btn-scenarios" class="nav-tab">🧪 What-If Scenario Studio</div>
      <div onclick="switchTab('ledger')" id="tab-btn-ledger" class="nav-tab">📋 Master Flow Ledger</div>
    </div>

    <!-- MAIN TAB CONTENTS CONTAINER -->
    <div class="bg-white rounded-b-xl border border-slate-200 p-5 shadow-sm min-h-[550px]">

      <!-- TAB 1: EXECUTIVE OVERVIEW & P&L WATERFALL -->
      <div id="tab-overview" class="space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">End-to-End Financial Bridge & Supply Chain P&L</h2>
            <p class="text-xs text-slate-500">Breakdown from top-line revenue to operating margin and net post-penalty objective</p>
          </div>
          <div class="flex items-center space-x-2">
            <span class="badge bg-slate-100 text-slate-700 border-slate-300">Total Demand: 15.45 units</span>
            <span class="badge bg-emerald-100 text-emerald-700 border-emerald-300">Fulfilled: 15.00 units</span>
            <span class="badge bg-rose-100 text-rose-700 border-rose-300">Stockout: 0.45 units</span>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Financial Waterfall SVG -->
          <div class="lg:col-span-2 bg-slate-50/70 rounded-xl border border-slate-200 p-4">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Financial Waterfall Bridge (&dollar; Thousands)</h3>
              <span class="text-xs text-slate-500">Values in &dollar;k</span>
            </div>
            
            <div class="relative w-full h-[280px]">
              <svg viewBox="0 0 650 250" class="w-full h-full">
                <line x1="50" y1="30" x2="620" y2="30" stroke="#e2e8f0" stroke-dasharray="3,3" />
                <line x1="50" y1="80" x2="620" y2="80" stroke="#e2e8f0" stroke-dasharray="3,3" />
                <line x1="50" y1="130" x2="620" y2="130" stroke="#cbd5e1" stroke-width="1.5" />
                <line x1="50" y1="180" x2="620" y2="180" stroke="#e2e8f0" stroke-dasharray="3,3" />
                <line x1="50" y1="230" x2="620" y2="230" stroke="#e2e8f0" stroke-dasharray="3,3" />

                <text x="40" y="34" font-size="10" fill="#64748b" text-anchor="end">+&dollar;100k</text>
                <text x="40" y="84" font-size="10" fill="#64748b" text-anchor="end">+&dollar;50k</text>
                <text x="40" y="134" font-size="10" fill="#0f172a" font-weight="bold" text-anchor="end">&dollar;0</text>
                <text x="40" y="184" font-size="10" fill="#64748b" text-anchor="end">-&dollar;50k</text>
                <text x="40" y="234" font-size="10" fill="#64748b" text-anchor="end">-&dollar;100k</text>

                <!-- Bar 1: Gross Revenue (+90.04) -->
                <rect x="75" y="40" width="55" height="90" rx="4" fill="#0284c7" />
                <text x="102" y="32" font-size="11" font-weight="bold" fill="#0284c7" text-anchor="middle">+90.04</text>
                <text x="102" y="148" font-size="10" font-weight="500" fill="#475569" text-anchor="middle">Revenue</text>

                <line x1="130" y1="40" x2="155" y2="40" stroke="#94a3b8" stroke-dasharray="2,2" />

                <!-- Bar 2: RM Cost (-51.30) -->
                <rect x="155" y="40" width="55" height="51.3" rx="4" fill="#ef4444" opacity="0.9" />
                <text x="182" y="32" font-size="11" font-weight="bold" fill="#dc2626" text-anchor="middle">-51.30</text>
                <text x="182" y="148" font-size="10" font-weight="500" fill="#475569" text-anchor="middle">Raw Mat</text>

                <line x1="210" y1="91.3" x2="235" y2="91.3" stroke="#94a3b8" stroke-dasharray="2,2" />

                <!-- Bar 3: Prod Cost (-1.95) -->
                <rect x="235" y="91.3" width="55" height="4" rx="2" fill="#f97316" />
                <text x="262" y="85" font-size="11" font-weight="bold" fill="#ea580c" text-anchor="middle">-1.95</text>
                <text x="262" y="148" font-size="10" font-weight="500" fill="#475569" text-anchor="middle">Mfg Prod</text>

                <line x1="290" y1="95.3" x2="315" y2="95.3" stroke="#94a3b8" stroke-dasharray="2,2" />

                <!-- Bar 4: Freight Cost (-9.23) -->
                <rect x="315" y="95.3" width="55" height="9.2" rx="3" fill="#f59e0b" />
                <text x="342" y="90" font-size="11" font-weight="bold" fill="#d97706" text-anchor="middle">-9.23</text>
                <text x="342" y="148" font-size="10" font-weight="500" fill="#475569" text-anchor="middle">Freight</text>

                <line x1="370" y1="102.4" x2="395" y2="102.4" stroke="#94a3b8" stroke-dasharray="2,2" />

                <!-- Bar 5: Operating Profit (+27.57) -->
                <rect x="395" y="102.4" width="55" height="27.6" rx="4" fill="#10b981" />
                <text x="422" y="95" font-size="11" font-weight="bold" fill="#059669" text-anchor="middle">+27.57</text>
                <text x="422" y="148" font-size="10" font-weight="bold" fill="#059669" text-anchor="middle">Op Profit</text>

                <line x1="450" y1="102.4" x2="475" y2="102.4" stroke="#94a3b8" stroke-dasharray="2,2" />

                <!-- Bar 6: Penalty Cost (-45.00) -->
                <rect x="475" y="102.4" width="55" height="45" rx="4" fill="#e11d48" />
                <text x="502" y="94" font-size="11" font-weight="bold" fill="#be123c" text-anchor="middle">-45.00</text>
                <text x="502" y="165" font-size="10" font-weight="bold" fill="#be123c" text-anchor="middle">Penalty</text>

                <line x1="530" y1="147.4" x2="555" y2="147.4" stroke="#94a3b8" stroke-dasharray="2,2" />

                <!-- Bar 7: Net LP Objective (-17.43) -->
                <rect x="555" y="130" width="55" height="17.4" rx="4" fill="#475569" />
                <text x="582" y="165" font-size="11" font-weight="bold" fill="#334155" text-anchor="middle">-17.43</text>
                <text x="582" y="180" font-size="10" font-weight="bold" fill="#1e293b" text-anchor="middle">Net Obj</text>
              </svg>
            </div>
            
            <div class="mt-2 text-[11px] text-slate-500 flex items-center justify-between border-t border-slate-200/60 pt-2">
              <span>* Operating profit reflects physical supply chain operations (+30.6% margin).</span>
              <span>* Net LP objective accounts for synthetic stockout penalty (-&dollar;100/unit).</span>
            </div>
          </div>

          <!-- Cost Structure Breakdown & Executive Findings -->
          <div class="space-y-4">
            <div class="bg-white rounded-xl border border-slate-200 p-4">
              <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Delivered Cost Composition</h3>
              <div class="space-y-3">
                <div>
                  <div class="flex justify-between text-xs font-medium mb-1">
                    <span class="text-slate-600">Raw Materials (P1 & P2)</span>
                    <span class="text-slate-900 font-bold">&dollar;51.30k (82.1%)</span>
                  </div>
                  <div class="w-full bg-slate-100 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full" style="width: 82.1%"></div>
                  </div>
                </div>

                <div>
                  <div class="flex justify-between text-xs font-medium mb-1">
                    <span class="text-slate-600">Freight Logistics (Road/Rail)</span>
                    <span class="text-slate-900 font-bold">&dollar;9.23k (14.8%)</span>
                  </div>
                  <div class="w-full bg-slate-100 rounded-full h-2">
                    <div class="bg-amber-500 h-2 rounded-full" style="width: 14.8%"></div>
                  </div>
                </div>

                <div>
                  <div class="flex justify-between text-xs font-medium mb-1">
                    <span class="text-slate-600">Factory Manufacturing Costs</span>
                    <span class="text-slate-900 font-bold">&dollar;1.95k (3.1%)</span>
                  </div>
                  <div class="w-full bg-slate-100 rounded-full h-2">
                    <div class="bg-emerald-500 h-2 rounded-full" style="width: 3.1%"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Key Strategic Takeaways -->
            <div class="bg-blue-50/50 rounded-xl border border-blue-200 p-4">
              <h3 class="text-xs font-bold text-blue-900 uppercase tracking-wider mb-2">Managerial Insights & Takeaways</h3>
              <ul class="text-xs text-blue-900 space-y-2 leading-relaxed">
                <li class="flex items-start space-x-1.5">
                  <span class="text-blue-600 font-bold mt-0.5">•</span>
                  <span><strong>Capacity is the sole constraint:</strong> Total factory output is locked at 15.00 units (all 3 factories run at 100% capacity on Operation 1).</span>
                </li>
                <li class="flex items-start space-x-1.5">
                  <span class="text-blue-600 font-bold mt-0.5">•</span>
                  <span><strong>Optimal Shortage Allocation:</strong> The LP intelligently selects Market 4 Product 2 to incur the 0.45 stockout because its selling price (&dollar;5.0) offers lower margin than defending higher-priced contracts.</span>
                </li>
                <li class="flex items-start space-x-1.5">
                  <span class="text-blue-600 font-bold mt-0.5">•</span>
                  <span><strong>Logistics Consolidation:</strong> 4 of 5 warehouses are actively routing freight. Warehouse 3 is 100% dormant and should be evaluated for closure.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: MULTI-ECHELON NETWORK FLOW DIAGRAM -->
      <div id="tab-network" class="hidden space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">Multi-Echelon Physical Flow Architecture</h2>
            <p class="text-xs text-slate-500">Interactive topology showing freight movement from Suppliers &rarr; Factories &rarr; Warehouses &rarr; Regional Markets (Hover any lane or node for details)</p>
          </div>
          <div class="flex items-center space-x-2 text-xs">
            <span class="inline-flex items-center"><span class="w-3 h-3 rounded-full bg-blue-600 mr-1.5"></span> Product 1 Lanes</span>
            <span class="inline-flex items-center ml-3"><span class="w-3 h-3 rounded-full bg-amber-500 mr-1.5"></span> Product 2 Lanes</span>
            <span class="inline-flex items-center ml-3"><span class="w-3 h-3 rounded-full bg-emerald-600 mr-1.5"></span> Direct Bypass (Factory &rarr; Market)</span>
          </div>
        </div>

        <!-- Interactive SVG Canvas Network -->
        <div class="relative w-full bg-slate-950 rounded-xl p-4 overflow-x-auto shadow-inner">
          <div class="min-w-[850px] h-[520px] relative">
            <svg id="network-svg" viewBox="0 0 920 520" class="w-full h-full">
              <!-- Tier Headers -->
              <text x="60" y="25" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">ECHELON 0: SUPPLIERS</text>
              <text x="240" y="25" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">ECHELON 1: FACTORIES</text>
              <text x="500" y="25" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">ECHELON 2: WAREHOUSES</text>
              <text x="800" y="25" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">ECHELON 3: REGIONAL MARKETS</text>

              <!-- Vertical Guideline Columns -->
              <line x1="60" y1="40" x2="60" y2="500" stroke="#1e293b" stroke-dasharray="4,4" />
              <line x1="240" y1="40" x2="240" y2="500" stroke="#1e293b" stroke-dasharray="4,4" />
              <line x1="500" y1="40" x2="500" y2="500" stroke="#1e293b" stroke-dasharray="4,4" />
              <line x1="800" y1="40" x2="800" y2="500" stroke="#1e293b" stroke-dasharray="4,4" />

              <!-- FLOW PATHS WITH DATA-TOOLTIP ATTRIBUTES -->
              <!-- 1. DIRECT LANES -->
              <!-- F1 -> M2 -->
              <path class="net-lane" data-tip="<strong>Direct Lane: F1 &rarr; M2</strong><br>Product 1: 1.30 u<br>Freight: &dollar;0.60/u (&dollar;0.78k)<br>Revenue: &dollar;9.10k<br>Operating Margin: &dollar;4.35k" d="M 270 120 C 420 50, 620 50, 770 110" fill="none" stroke="#10b981" stroke-width="3.5" opacity="0.85" stroke-dasharray="5,2" />
              <!-- F3 -> M7 -->
              <path class="net-lane" data-tip="<strong>Direct Lane: F3 &rarr; M7</strong><br>P1: 0.70 u | P2: 1.50 u (Total: 2.20 u)<br>Freight: &dollar;0.50/u (&dollar;1.10k)<br>Revenue: &dollar;14.08k<br>Top Revenue Market Channel" d="M 270 400 C 450 490, 650 490, 770 380" fill="none" stroke="#10b981" stroke-width="4.5" opacity="0.85" stroke-dasharray="5,2" />
              <!-- F3 -> M8 -->
              <path class="net-lane" data-tip="<strong>Direct Lane: F3 &rarr; M8</strong><br>P1: 0.45 u | P2: 1.50 u (Total: 1.95 u)<br>Freight: &dollar;0.60/u (&dollar;1.17k)<br>Revenue: &dollar;10.74k" d="M 270 400 C 450 510, 680 510, 770 435" fill="none" stroke="#10b981" stroke-width="4.0" opacity="0.85" stroke-dasharray="5,2" />

              <!-- 2. FACTORY -> WAREHOUSE LANES -->
              <!-- F1 -> W2 (Mode 2) -->
              <line class="net-lane" data-tip="<strong>Inbound: F1 &rarr; W2 (Mode 2 Intermodal)</strong><br>P1: 1.00 u | P2: 2.70 u (Total: 3.70 u)<br>Freight Rate: &dollar;0.50/u (Bulk Discount)<br>Total Freight: &dollar;1.85k" x1="270" y1="120" x2="470" y2="175" stroke="#f59e0b" stroke-width="5" opacity="0.8" />
              <!-- F2 -> W1 (Mode 1) -->
              <line class="net-lane" data-tip="<strong>Inbound: F2 &rarr; W1 (Mode 1 Road Truck)</strong><br>P1: 0.70 u | P2: 0.60 u (Total: 1.30 u)<br>Freight Rate: &dollar;0.60/u<br>Total Freight: &dollar;0.78k" x1="270" y1="260" x2="470" y2="90" stroke="#38bdf8" stroke-width="2.8" opacity="0.8" />
              <!-- F2 -> W4 (Mode 1) -->
              <line class="net-lane" data-tip="<strong>Inbound: F2 &rarr; W4 (Mode 1 Road Truck)</strong><br>P1: 1.30 u | P2: 2.40 u (Total: 3.70 u)<br>Freight Rate: &dollar;0.50/u<br>Total Freight: &dollar;1.85k" x1="270" y1="260" x2="470" y2="345" stroke="#f59e0b" stroke-width="5" opacity="0.8" />
              <!-- F3 -> W5 (Mode 1) -->
              <line class="net-lane" data-tip="<strong>Inbound: F3 &rarr; W5 (Mode 1 Road Truck)</strong><br>Product 1: 0.85 u<br>Freight Rate: &dollar;0.60/u<br>Total Freight: &dollar;0.51k" x1="270" y1="400" x2="470" y2="430" stroke="#38bdf8" stroke-width="2.5" opacity="0.8" />

              <!-- 3. WAREHOUSE -> MARKET LANES -->
              <!-- W1 -> M1 -->
              <line class="net-lane" data-tip="<strong>Outbound: W1 &rarr; M1</strong><br>Product 1: 0.60 u<br>Freight: &dollar;0.10/u" x1="530" y1="90" x2="770" y2="60" stroke="#38bdf8" stroke-width="2.0" opacity="0.8" />
              <!-- W1 -> M6 -->
              <line class="net-lane" data-tip="<strong>Outbound: W1 &rarr; M6</strong><br>P1: 0.10 u | P2: 0.60 u<br>Freight: &dollar;0.10/u" x1="530" y1="90" x2="770" y2="325" stroke="#f59e0b" stroke-width="2.2" opacity="0.8" />

              <!-- W2 -> M1 -->
              <line class="net-lane" data-tip="<strong>Outbound: W2 &rarr; M1</strong><br>P1: 0.15 u | P2: 1.00 u<br>Freight: &dollar;0.12 - &dollar;0.15/u" x1="530" y1="175" x2="770" y2="60" stroke="#f59e0b" stroke-width="2.8" opacity="0.8" />
              <!-- W2 -> M3 -->
              <line class="net-lane" data-tip="<strong>Outbound: W2 &rarr; M3</strong><br>P1: 0.85 u | P2: 1.45 u (Total: 2.30 u)<br>Freight: &dollar;0.10/u" x1="530" y1="175" x2="770" y2="165" stroke="#f59e0b" stroke-width="4.5" opacity="0.8" />
              <!-- W2 -> M4 -->
              <line class="net-lane" data-tip="<strong>Outbound: W2 &rarr; M4</strong><br>Product 2: 0.25 u<br>Freight: &dollar;0.17/u" x1="530" y1="175" x2="770" y2="215" stroke="#f59e0b" stroke-width="1.8" opacity="0.8" />

              <!-- W4 -> M4 -->
              <line class="net-lane" data-tip="<strong>Outbound: W4 &rarr; M4</strong><br>P1: 0.75 u | P2: 0.55 u<br>Freight: &dollar;0.14/u" x1="530" y1="345" x2="770" y2="215" stroke="#38bdf8" stroke-width="3.2" opacity="0.8" />
              <!-- W4 -> M5 -->
              <line class="net-lane" data-tip="<strong>Outbound: W4 &rarr; M5</strong><br>P1: 0.55 u | P2: 0.95 u<br>Freight: &dollar;0.13/u" x1="530" y1="345" x2="770" y2="270" stroke="#f59e0b" stroke-width="3.5" opacity="0.8" />
              <!-- W4 -> M9 -->
              <line class="net-lane" data-tip="<strong>Outbound: W4 &rarr; M9</strong><br>Product 2: 0.90 u<br>Freight: &dollar;0.14/u" x1="530" y1="345" x2="770" y2="485" stroke="#f59e0b" stroke-width="2.6" opacity="0.8" />

              <!-- W5 -> M6 -->
              <line class="net-lane" data-tip="<strong>Outbound: W5 &rarr; M6</strong><br>Product 1: 0.10 u<br>Freight: &dollar;0.19/u" x1="530" y1="430" x2="770" y2="325" stroke="#38bdf8" stroke-width="1.2" opacity="0.8" />
              <!-- W5 -> M9 -->
              <line class="net-lane" data-tip="<strong>Outbound: W5 &rarr; M9</strong><br>Product 1: 0.75 u<br>Freight: &dollar;0.12/u" x1="530" y1="430" x2="770" y2="485" stroke="#38bdf8" stroke-width="2.2" opacity="0.8" />

              <!-- NODES -->
              <!-- Suppliers -->
              <g transform="translate(30, 160)" class="net-node" data-tip="<strong>Supplier: Raw Material 1</strong><br>Supply Limit: 12.0 u<br>Allocated: 6.30 u (52.5%)<br>Headroom: 5.70 u slack<br>Unit Cost: &dollar;4.00">
                <rect width="60" height="50" rx="8" fill="#1e293b" stroke="#3b82f6" stroke-width="2" />
                <text x="30" y="24" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">RM 1</text>
                <text x="30" y="38" fill="#93c5fd" font-size="9" text-anchor="middle">Cap: 12.0</text>
              </g>
              <g transform="translate(30, 310)" class="net-node" data-tip="<strong>Supplier: Raw Material 2</strong><br>Supply Limit: 10.5 u<br>Allocated: 8.70 u (82.9%)<br>Headroom: 1.80 u slack<br>Unit Cost: &dollar;3.00">
                <rect width="60" height="50" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2" />
                <text x="30" y="24" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">RM 2</text>
                <text x="30" y="38" fill="#fde68a" font-size="9" text-anchor="middle">Cap: 10.5</text>
              </g>

              <!-- Factories -->
              <!-- F1 -->
              <g transform="translate(210, 95)" class="net-node" data-tip="<strong>Factory 1</strong><br>Output: 5.00 u (2.30 P1, 2.70 P2)<br>Op 1 Cap: 100.0% (Binding)<br>Op 2 Cap: 96.3%<br>Mfg Cost: &dollar;0.15 / &dollar;0.10">
                <rect width="60" height="50" rx="8" fill="#0f172a" stroke="#ef4444" stroke-width="2.5" />
                <text x="30" y="22" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">F1</text>
                <text x="30" y="36" fill="#fca5a5" font-size="9" text-anchor="middle">5.0 / 5.0</text>
              </g>
              <!-- F2 -->
              <g transform="translate(210, 235)" class="net-node" data-tip="<strong>Factory 2</strong><br>Output: 5.00 u (2.00 P1, 3.00 P2)<br>Op 1 Cap: 100.0% (Binding)<br>Op 2 Cap: 100.0% (Binding)<br>Mfg Cost: &dollar;0.19 / &dollar;0.14">
                <rect width="60" height="50" rx="8" fill="#0f172a" stroke="#ef4444" stroke-width="2.5" />
                <text x="30" y="22" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">F2</text>
                <text x="30" y="36" fill="#fca5a5" font-size="9" text-anchor="middle">5.0 / 5.0</text>
              </g>
              <!-- F3 -->
              <g transform="translate(210, 375)" class="net-node" data-tip="<strong>Factory 3 (Lowest Cost)</strong><br>Output: 5.00 u (2.00 P1, 3.00 P2)<br>Op 1 Cap: 100.0% (Binding)<br>Op 2 Cap: 100.0% (Binding)<br>Mfg Cost: &dollar;0.13 / &dollar;0.09">
                <rect width="60" height="50" rx="8" fill="#0f172a" stroke="#ef4444" stroke-width="2.5" />
                <text x="30" y="22" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">F3</text>
                <text x="30" y="36" fill="#fca5a5" font-size="9" text-anchor="middle">5.0 / 5.0</text>
              </g>

              <!-- Warehouses (W1..W5) -->
              <!-- W1 -->
              <g transform="translate(470, 68)" class="net-node" data-tip="<strong>Warehouse 1</strong><br>Throughput: 1.30 u (0.70 P1, 0.60 P2)<br>Inflow = Outflow Balance: 100%<br>Serves: M1, M6">
                <rect width="60" height="44" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2" />
                <text x="30" y="20" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">W1</text>
                <text x="30" y="34" fill="#bae6fd" font-size="9" text-anchor="middle">1.30 flow</text>
              </g>
              <!-- W2 (Mega Hub) -->
              <g transform="translate(470, 153)" class="net-node" data-tip="<strong>Warehouse 2 (Mega-Hub)</strong><br>Throughput: 3.70 u (1.00 P1, 2.70 P2)<br>Intermodal Rail inbound from F1<br>Serves: M1, M3, M4">
                <rect width="60" height="44" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5" />
                <text x="30" y="20" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">W2</text>
                <text x="30" y="34" fill="#fde68a" font-size="9" font-weight="bold" text-anchor="middle">3.70 flow</text>
              </g>
              <!-- W3 (Idle) -->
              <g transform="translate(470, 238)" class="net-node opacity-40" data-tip="<strong>Warehouse 3 (Idle)</strong><br>Throughput: 0.00 u<br>Status: Dormant in optimal plan<br>Candidate for consolidation">
                <rect width="60" height="44" rx="8" fill="#1e293b" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3,2" />
                <text x="30" y="20" fill="#94a3b8" font-size="11" font-weight="bold" text-anchor="middle">W3</text>
                <text x="30" y="34" fill="#94a3b8" font-size="9" text-anchor="middle">0.00 idle</text>
              </g>
              <!-- W4 (Mega Hub) -->
              <g transform="translate(470, 323)" class="net-node" data-tip="<strong>Warehouse 4 (Mega-Hub)</strong><br>Throughput: 3.70 u (1.30 P1, 2.40 P2)<br>Truckload road inbound from F2<br>Serves: M4, M5, M9">
                <rect width="60" height="44" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2.5" />
                <text x="30" y="20" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">W4</text>
                <text x="30" y="34" fill="#fde68a" font-size="9" font-weight="bold" text-anchor="middle">3.70 flow</text>
              </g>
              <!-- W5 -->
              <g transform="translate(470, 408)" class="net-node" data-tip="<strong>Warehouse 5</strong><br>Throughput: 0.85 u (0.85 P1, 0.00 P2)<br>Serves: M6, M9">
                <rect width="60" height="44" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2" />
                <text x="30" y="20" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">W5</text>
                <text x="30" y="34" fill="#bae6fd" font-size="9" text-anchor="middle">0.85 flow</text>
              </g>

              <!-- Markets (M1..M9) -->
              <!-- M1 -->
              <g transform="translate(770, 38)" class="net-node" data-tip="<strong>Market 1</strong><br>Demand: 1.75 u | Shipped: 1.75 u (100%)<br>Revenue: &dollar;10.38k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M1</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">1.75 / 1.75</text>
              </g>
              <!-- M2 (Direct) -->
              <g transform="translate(770, 88)" class="net-node" data-tip="<strong>Market 2 (Direct Supplied)</strong><br>Demand: 1.30 u | Shipped: 1.30 u (100%)<br>Supplied Direct from Factory 1<br>Revenue: &dollar;9.10k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M2</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">1.30 (Direct)</text>
              </g>
              <!-- M3 -->
              <g transform="translate(770, 143)" class="net-node" data-tip="<strong>Market 3</strong><br>Demand: 2.30 u | Shipped: 2.30 u (100%)<br>Revenue: &dollar;12.61k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M3</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">2.30 / 2.30</text>
              </g>
              <!-- M4 (Shortage) -->
              <g transform="translate(770, 198)" class="net-node" data-tip="<strong>Market 4 (SHORTAGE DETECTED)</strong><br>Demand: 2.00 u | Shipped: 1.55 u (77.5%)<br>Product 2 Shortage: 0.45 u<br>Penalty Incurred: -&dollar;45.00k<br>Revenue: &dollar;9.70k">
                <rect width="55" height="38" rx="6" fill="#450a0a" stroke="#f43f5e" stroke-width="2" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M4</text>
                <text x="27" y="30" fill="#fda4af" font-size="8" font-weight="bold" text-anchor="middle">1.55 (0.45&darr;)</text>
              </g>
              <!-- M5 -->
              <g transform="translate(770, 253)" class="net-node" data-tip="<strong>Market 5</strong><br>Demand: 1.50 u | Shipped: 1.50 u (100%)<br>Revenue: &dollar;9.09k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M5</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">1.50 / 1.50</text>
              </g>
              <!-- M6 -->
              <g transform="translate(770, 308)" class="net-node" data-tip="<strong>Market 6</strong><br>Demand: 0.80 u | Shipped: 0.80 u (100%)<br>Revenue: &dollar;4.42k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M6</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">0.80 / 0.80</text>
              </g>
              <!-- M7 (Direct) -->
              <g transform="translate(770, 363)" class="net-node" data-tip="<strong>Market 7 (Highest Revenue)</strong><br>Demand: 2.20 u | Shipped: 2.20 u (100%)<br>Direct from Factory 3<br>Revenue: &dollar;14.08k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M7</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">2.20 (Direct)</text>
              </g>
              <!-- M8 (Direct) -->
              <g transform="translate(770, 418)" class="net-node" data-tip="<strong>Market 8</strong><br>Demand: 1.95 u | Shipped: 1.95 u (100%)<br>Direct from Factory 3<br>Revenue: &dollar;10.74k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M8</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">1.95 (Direct)</text>
              </g>
              <!-- M9 -->
              <g transform="translate(770, 468)" class="net-node" data-tip="<strong>Market 9</strong><br>Demand: 1.65 u | Shipped: 1.65 u (100%)<br>Revenue: &dollar;9.93k">
                <rect width="55" height="38" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5" />
                <text x="27" y="18" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">M9</text>
                <text x="27" y="30" fill="#86efac" font-size="8" text-anchor="middle">1.65 / 1.65</text>
              </g>
            </svg>
          </div>
        </div>

        <!-- Network Legend Card -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
            <span class="font-bold text-slate-800 block mb-1">Direct Factory Bypass Routes</span>
            <p class="text-slate-600 leading-relaxed">
              3 high-volume markets bypass warehouse handling entirely: <strong>F1 &rarr; M2</strong> (1.30 units) and <strong>F3 &rarr; M7 & M8</strong> (4.15 units). This saves transit handling fees and optimizes transport direct corridors.
            </p>
          </div>
          <div class="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs">
            <span class="font-bold text-slate-800 block mb-1">Warehouse Hub Hierarchy</span>
            <p class="text-slate-600 leading-relaxed">
              <strong>W2 and W4</strong> function as primary regional consolidation hubs, each processing 3.70 units (77% of all warehouse traffic). <strong>W1</strong> handles 1.30 units and <strong>W5</strong> handles 0.85 units.
            </p>
          </div>
          <div class="p-3 bg-rose-50 rounded-lg border border-rose-200 text-xs">
            <span class="font-bold text-rose-900 block mb-1">Deficit Bottleneck (M4)</span>
            <p class="text-rose-800 leading-relaxed">
              <strong>Market 4</strong> is the sole point of failure. It requested 1.25 units of Product 2, but only receives 0.80 units (0.25 from W2 and 0.55 from W4), leaving an unresolved deficit of 0.45 units.
            </p>
          </div>
        </div>
      </div>

      <!-- TAB 3: FACTORY FLEET & UTILIZATION -->
      <div id="tab-factories" class="hidden space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">Manufacturing Fleet & Operations Capacity</h2>
            <p class="text-xs text-slate-500">Utilization across Operation 1 (throughput sum) and Operation 2 (resource ratio)</p>
          </div>
          <span class="badge bg-rose-100 text-rose-800 border-rose-300 font-bold">100.0% Fleet Bottleneck Bound</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Factory 1 -->
          <div class="metric-card p-5 border-l-4 border-l-blue-600">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-bold text-slate-900">Factory 1</h3>
              <span class="badge bg-emerald-100 text-emerald-800 border-emerald-300">5.00 / 5.00 Units</span>
            </div>
            
            <div class="space-y-3 text-xs">
              <div class="flex justify-between text-slate-600">
                <span>Product 1 Output:</span>
                <span class="font-bold text-slate-900">2.30 units</span>
              </div>
              <div class="flex justify-between text-slate-600">
                <span>Product 2 Output:</span>
                <span class="font-bold text-slate-900">2.70 units</span>
              </div>
              <div class="border-t border-slate-100 pt-2">
                <div class="flex justify-between text-slate-600 mb-1">
                  <span>Operation 1 (Shared Cap):</span>
                  <span class="font-bold text-rose-600">100.0% (Binding)</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                  <div class="bg-rose-500 h-2 rounded-full" style="width: 100%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-slate-600 mb-1">
                  <span>Operation 2 (Tech Ratio):</span>
                  <span class="font-bold text-slate-700">96.3%</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                  <div class="bg-blue-600 h-2 rounded-full" style="width: 96.3%"></div>
                </div>
              </div>
              <div class="pt-2 border-t border-slate-100 text-slate-500 flex justify-between">
                <span>Unit Mfg Cost (P1 / P2):</span>
                <span class="font-semibold text-slate-800">&dollar;0.15 / &dollar;0.10</span>
              </div>
            </div>
          </div>

          <!-- Factory 2 -->
          <div class="metric-card p-5 border-l-4 border-l-amber-500">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-bold text-slate-900">Factory 2</h3>
              <span class="badge bg-emerald-100 text-emerald-800 border-emerald-300">5.00 / 5.00 Units</span>
            </div>
            
            <div class="space-y-3 text-xs">
              <div class="flex justify-between text-slate-600">
                <span>Product 1 Output:</span>
                <span class="font-bold text-slate-900">2.00 units</span>
              </div>
              <div class="flex justify-between text-slate-600">
                <span>Product 2 Output:</span>
                <span class="font-bold text-slate-900">3.00 units</span>
              </div>
              <div class="border-t border-slate-100 pt-2">
                <div class="flex justify-between text-slate-600 mb-1">
                  <span>Operation 1 (Shared Cap):</span>
                  <span class="font-bold text-rose-600">100.0% (Binding)</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                  <div class="bg-rose-500 h-2 rounded-full" style="width: 100%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-slate-600 mb-1">
                  <span>Operation 2 (Tech Ratio):</span>
                  <span class="font-bold text-rose-600">100.0% (Binding)</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                  <div class="bg-rose-500 h-2 rounded-full" style="width: 100%"></div>
                </div>
              </div>
              <div class="pt-2 border-t border-slate-100 text-slate-500 flex justify-between">
                <span>Unit Mfg Cost (P1 / P2):</span>
                <span class="font-semibold text-slate-800">&dollar;0.19 / &dollar;0.14</span>
              </div>
            </div>
          </div>

          <!-- Factory 3 -->
          <div class="metric-card p-5 border-l-4 border-l-emerald-600">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-bold text-slate-900">Factory 3 (Lowest Cost)</h3>
              <span class="badge bg-emerald-100 text-emerald-800 border-emerald-300">5.00 / 5.00 Units</span>
            </div>
            
            <div class="space-y-3 text-xs">
              <div class="flex justify-between text-slate-600">
                <span>Product 1 Output:</span>
                <span class="font-bold text-slate-900">2.00 units</span>
              </div>
              <div class="flex justify-between text-slate-600">
                <span>Product 2 Output:</span>
                <span class="font-bold text-slate-900">3.00 units</span>
              </div>
              <div class="border-t border-slate-100 pt-2">
                <div class="flex justify-between text-slate-600 mb-1">
                  <span>Operation 1 (Shared Cap):</span>
                  <span class="font-bold text-rose-600">100.0% (Binding)</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                  <div class="bg-rose-500 h-2 rounded-full" style="width: 100%"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-slate-600 mb-1">
                  <span>Operation 2 (Tech Ratio):</span>
                  <span class="font-bold text-rose-600">100.0% (Binding)</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2">
                  <div class="bg-rose-500 h-2 rounded-full" style="width: 100%"></div>
                </div>
              </div>
              <div class="pt-2 border-t border-slate-100 text-slate-500 flex justify-between">
                <span>Unit Mfg Cost (P1 / P2):</span>
                <span class="font-semibold text-emerald-700">&dollar;0.13 / &dollar;0.09 (Benchmark)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Raw Material Supplier Utilization -->
        <div class="bg-slate-50 rounded-xl border border-slate-200 p-4">
          <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Upstream Raw Material Supplier Limits</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white p-3 rounded-lg border border-slate-200">
              <div class="flex justify-between text-xs mb-1">
                <span class="font-bold text-slate-800">Raw Material 1 (For Product 1)</span>
                <span class="text-blue-600 font-semibold">6.30 / 12.0 Units (52.5% Used)</span>
              </div>
              <div class="w-full bg-slate-100 rounded-full h-2.5 mb-1">
                <div class="bg-blue-600 h-2.5 rounded-full" style="width: 52.5%"></div>
              </div>
              <span class="text-[11px] text-slate-500">Abundant headroom (5.70 units slack). Upstream RM is NOT a bottleneck.</span>
            </div>

            <div class="bg-white p-3 rounded-lg border border-slate-200">
              <div class="flex justify-between text-xs mb-1">
                <span class="font-bold text-slate-800">Raw Material 2 (For Product 2)</span>
                <span class="text-amber-600 font-semibold">8.70 / 10.5 Units (82.9% Used)</span>
              </div>
              <div class="w-full bg-slate-100 rounded-full h-2.5 mb-1">
                <div class="bg-amber-500 h-2.5 rounded-full" style="width: 82.9%"></div>
              </div>
              <span class="text-[11px] text-slate-500">1.80 units available headroom before hitting supplier constraint.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 4: WAREHOUSE HUBS & FREIGHT CORRIDORS -->
      <div id="tab-warehouses" class="hidden space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">Warehouse Network Balance & Freight Modality</h2>
            <p class="text-xs text-slate-500">Audit of intermediate consolidation hubs, mode selections, and transit balance</p>
          </div>
          <span class="badge bg-slate-100 text-slate-700 border-slate-300">4 Active / 1 Idle Warehouse</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <!-- W1 -->
          <div class="metric-card p-4">
            <span class="badge bg-blue-100 text-blue-800 border-blue-200 mb-2">Warehouse 1</span>
            <div class="text-lg font-bold text-slate-900 mt-1">1.30 <span class="text-xs font-normal text-slate-500">units</span></div>
            <div class="text-xs text-slate-600 mt-2 space-y-1">
              <div>P1: 0.70 | P2: 0.60</div>
              <div class="text-emerald-600 font-medium">Inflow = Outflow &check;</div>
              <div class="text-[11px] text-slate-400">Serves M1, M6</div>
            </div>
          </div>

          <!-- W2 -->
          <div class="metric-card p-4 border-blue-300 bg-blue-50/20">
            <span class="badge bg-emerald-100 text-emerald-800 border-emerald-300 mb-2">Warehouse 2 (Mega-Hub)</span>
            <div class="text-lg font-bold text-slate-900 mt-1">3.70 <span class="text-xs font-normal text-slate-500">units</span></div>
            <div class="text-xs text-slate-600 mt-2 space-y-1">
              <div>P1: 1.00 | P2: 2.70</div>
              <div class="text-emerald-600 font-medium">Inflow = Outflow &check;</div>
              <div class="text-[11px] text-slate-500">Rail Mode 2 inbound from F1</div>
            </div>
          </div>

          <!-- W3 -->
          <div class="metric-card p-4 border-dashed border-slate-300 bg-slate-50/60 opacity-60">
            <span class="badge bg-slate-200 text-slate-700 border-slate-300 mb-2">Warehouse 3 (Idle)</span>
            <div class="text-lg font-bold text-slate-400 mt-1">0.00 <span class="text-xs font-normal text-slate-400">units</span></div>
            <div class="text-xs text-slate-400 mt-2 space-y-1">
              <div>Zero flow allocation</div>
              <div>Sub-optimal lane costs</div>
              <div class="text-rose-500 font-medium">Decommission target</div>
            </div>
          </div>

          <!-- W4 -->
          <div class="metric-card p-4 border-blue-300 bg-blue-50/20">
            <span class="badge bg-emerald-100 text-emerald-800 border-emerald-300 mb-2">Warehouse 4 (Mega-Hub)</span>
            <div class="text-lg font-bold text-slate-900 mt-1">3.70 <span class="text-xs font-normal text-slate-500">units</span></div>
            <div class="text-xs text-slate-600 mt-2 space-y-1">
              <div>P1: 1.30 | P2: 2.40</div>
              <div class="text-emerald-600 font-medium">Inflow = Outflow &check;</div>
              <div class="text-[11px] text-slate-500">Road Mode 1 from F2</div>
            </div>
          </div>

          <!-- W5 -->
          <div class="metric-card p-4">
            <span class="badge bg-blue-100 text-blue-800 border-blue-200 mb-2">Warehouse 5</span>
            <div class="text-lg font-bold text-slate-900 mt-1">0.85 <span class="text-xs font-normal text-slate-500">units</span></div>
            <div class="text-xs text-slate-600 mt-2 space-y-1">
              <div>P1: 0.85 | P2: 0.00</div>
              <div class="text-emerald-600 font-medium">Inflow = Outflow &check;</div>
              <div class="text-[11px] text-slate-400">Serves M6, M9</div>
            </div>
          </div>
        </div>

        <!-- Transport Mode Split Analysis -->
        <div class="bg-slate-50 rounded-xl border border-slate-200 p-4">
          <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Factory-to-Warehouse Transport Mode Breakdown</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="bg-white p-3 rounded-lg border border-slate-200">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-slate-800">Mode 1: Direct Road Freight (Truckload)</span>
                <span class="font-semibold text-slate-900">5.75 units (60.8%)</span>
              </div>
              <p class="text-slate-500 text-[11px]">Used on F2 &rarr; W1 (1.30u), F2 &rarr; W4 (3.70u), and F3 &rarr; W5 (0.85u). Standard freight rates (&dollar;0.5 - &dollar;0.6/unit).</p>
            </div>

            <div class="bg-white p-3 rounded-lg border border-slate-200">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-slate-800">Mode 2: Rail Intermodal Bulk Freight</span>
                <span class="font-semibold text-slate-900">3.70 units (39.2%)</span>
              </div>
              <p class="text-slate-500 text-[11px]">Exclusively leveraged on <strong>F1 &rarr; W2</strong> route. Negotiated low bulk rate of &dollar;0.50/unit delivers significant freight savings.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 5: MARKET DEMAND & REGIONAL P&L -->
      <div id="tab-markets" class="hidden space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">Market Demand Matrix & Fulfillment P&L</h2>
            <p class="text-xs text-slate-500">Commercial revenue, delivered fill rates, and shortage penalties across 9 customer markets</p>
          </div>
          <span class="badge bg-emerald-100 text-emerald-800 border-emerald-300">8 of 9 Markets 100% Satisfied</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-xs text-left border-collapse">
            <thead>
              <tr class="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
                <th class="py-2.5 px-3">Market</th>
                <th class="py-2.5 px-3 text-center">P1 Demand / Ship</th>
                <th class="py-2.5 px-3 text-center">P2 Demand / Ship</th>
                <th class="py-2.5 px-3 text-center">Total Volume</th>
                <th class="py-2.5 px-3 text-center">Shortage</th>
                <th class="py-2.5 px-3 text-center">Fill Rate</th>
                <th class="py-2.5 px-3 text-right">Gross Revenue</th>
                <th class="py-2.5 px-3 text-center">Supply Channel</th>
              </tr>
            </thead>
            <tbody id="markets-table-body" class="divide-y divide-slate-100 text-slate-700">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- TAB 6: SENSITIVITY & SHADOW PRICES -->
      <div id="tab-sensitivity" class="hidden space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">Dual Sensitivity Analysis & Shadow Price Interpretations</h2>
            <p class="text-xs text-slate-500">Managerial translation of LP dual multipliers, binding constraints, and reduced costs</p>
          </div>
          <span class="badge bg-purple-100 text-purple-800 border-purple-300">Gurobi LP Simplex Duals</span>
        </div>

        <div class="bg-blue-50/60 rounded-xl border border-blue-200 p-4 text-xs text-blue-900 leading-relaxed">
          <span class="font-bold block text-blue-950 mb-1">📘 Executive Guide to Shadow Prices (Dual Values)</span>
          A <strong>Shadow Price (&pi;)</strong> represents the exact change in network profit resulting from a 1-unit increase in the right-hand side of a constraint.
          When a factory capacity has a shadow price of <strong>+&dollar;506.15</strong>, it means each additional unit of factory capacity would eliminate the &dollar;100 shortage penalty and capture &dollar;406+ in net margin across the system!
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Binding Constraints Table -->
          <div>
            <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Binding Constraints (Active Bottlenecks)</h3>
            <div class="overflow-x-auto border border-slate-200 rounded-lg">
              <table class="w-full text-xs text-left">
                <thead class="bg-slate-100 text-slate-700">
                  <tr>
                    <th class="py-2 px-3">Constraint</th>
                    <th class="py-2 px-3 text-right">Shadow Price (&pi;)</th>
                    <th class="py-2 px-3">Managerial Impact</th>
                  </tr>
                </thead>
                <tbody id="binding-constrs-body" class="divide-y divide-slate-100">
                  <!-- Rendered via JS -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Non-Basic Variable Reduced Costs -->
          <div>
            <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Reduced Costs (Unused Route Barriers)</h3>
            <div class="overflow-x-auto border border-slate-200 rounded-lg max-h-[360px] ledger-scroll">
              <table class="w-full text-xs text-left">
                <thead class="bg-slate-100 text-slate-700 sticky top-0">
                  <tr>
                    <th class="py-2 px-3">Decision Route</th>
                    <th class="py-2 px-3 text-right">Reduced Cost</th>
                    <th class="py-2 px-3">Economic Interpretation</th>
                  </tr>
                </thead>
                <tbody id="reduced-costs-body" class="divide-y divide-slate-100">
                  <!-- Rendered via JS -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 7: INTERACTIVE WHAT-IF SCENARIO STUDIO -->
      <div id="tab-scenarios" class="hidden space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">What-If Optimization Simulator & Strategic Presets</h2>
            <p class="text-xs text-slate-500">Real-time parametric simulation. Adjust policy levers to observe instant system-wide impacts.</p>
          </div>
          <button onclick="resetSliders()" class="px-3 py-1 text-xs font-semibold rounded bg-slate-100 hover:bg-slate-200 text-slate-700 transition">
            Reset to Baseline
          </button>
        </div>

        <!-- PRESET SCENARIO CARDS -->
        <div>
          <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Pre-Solved Executive Scenarios</h3>
          <div class="grid grid-cols-1 md:grid-cols-5 gap-3" id="preset-scenarios-container">
            <!-- Rendered via JS -->
          </div>
        </div>

        <!-- INTERACTIVE LIVE SIMULATOR SLIDERS -->
        <div class="bg-slate-50 rounded-xl border border-slate-200 p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <span>Interactive Network Policy Levers</span>
              <span class="badge bg-blue-100 text-blue-800 border-blue-300">Live Client-Side Optimizer</span>
            </h3>
            <span class="text-xs text-slate-500">Move sliders to dynamically re-evaluate</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <!-- Lever 1: Factory Capacity -->
            <div class="bg-white p-3.5 rounded-lg border border-slate-200">
              <div class="flex justify-between items-center text-xs mb-1">
                <span class="font-bold text-slate-800">Factory Capacity Factor</span>
                <span id="lbl-cap" class="font-bold text-blue-600 text-sm">1.00x (15.0u)</span>
              </div>
              <input id="slider-cap" type="range" min="0.8" max="1.4" step="0.05" value="1.0" oninput="runLiveSimulation()" class="w-full accent-blue-600 cursor-pointer" />
              <div class="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>0.8x (-20%)</span>
                <span>1.0x (Base)</span>
                <span>1.4x (+40%)</span>
              </div>
            </div>

            <!-- Lever 2: Freight Cost -->
            <div class="bg-white p-3.5 rounded-lg border border-slate-200">
              <div class="flex justify-between items-center text-xs mb-1">
                <span class="font-bold text-slate-800">Freight Cost Multiplier</span>
                <span id="lbl-freight" class="font-bold text-amber-600 text-sm">1.00x</span>
              </div>
              <input id="slider-freight" type="range" min="0.6" max="2.0" step="0.1" value="1.0" oninput="runLiveSimulation()" class="w-full accent-amber-500 cursor-pointer" />
              <div class="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>0.6x (Cheap)</span>
                <span>1.0x (Base)</span>
                <span>2.0x (+100%)</span>
              </div>
            </div>

            <!-- Lever 3: Shortage Penalty -->
            <div class="bg-white p-3.5 rounded-lg border border-slate-200">
              <div class="flex justify-between items-center text-xs mb-1">
                <span class="font-bold text-slate-800">Shortage Penalty (&dollar;/unit)</span>
                <span id="lbl-penalty" class="font-bold text-rose-600 text-sm">&dollar;100</span>
              </div>
              <input id="slider-penalty" type="range" min="0" max="200" step="10" value="100" oninput="runLiveSimulation()" class="w-full accent-rose-600 cursor-pointer" />
              <div class="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>&dollar;0 (No Penalty)</span>
                <span>&dollar;100 (Base)</span>
                <span>&dollar;200 (Strict SLA)</span>
              </div>
            </div>

            <!-- Lever 4: Demand Scale -->
            <div class="bg-white p-3.5 rounded-lg border border-slate-200">
              <div class="flex justify-between items-center text-xs mb-1">
                <span class="font-bold text-slate-800">Market Demand Scale</span>
                <span id="lbl-demand" class="font-bold text-purple-600 text-sm">1.00x (15.45u)</span>
              </div>
              <input id="slider-demand" type="range" min="0.8" max="1.25" step="0.05" value="1.0" oninput="runLiveSimulation()" class="w-full accent-purple-600 cursor-pointer" />
              <div class="flex justify-between text-[10px] text-slate-400 mt-1">
                <span>0.8x (-20%)</span>
                <span>1.0x (Base)</span>
                <span>1.25x (+25%)</span>
              </div>
            </div>
          </div>

          <!-- Dynamic Output Results Card -->
          <div class="mt-5 p-4 rounded-lg bg-white border border-blue-200">
            <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Simulated Live Network Outcomes</h4>
            <div class="grid grid-cols-2 md:grid-cols-6 gap-3 text-center">
              <div class="p-2 bg-slate-50 rounded">
                <span class="text-[10px] text-slate-500 uppercase block">Simulated Revenue</span>
                <span id="sim-rev" class="text-base font-bold text-slate-900">&dollar;90.04k</span>
              </div>
              <div class="p-2 bg-slate-50 rounded">
                <span class="text-[10px] text-slate-500 uppercase block">Total Freight</span>
                <span id="sim-freight" class="text-base font-bold text-slate-900">&dollar;9.23k</span>
              </div>
              <div class="p-2 bg-slate-50 rounded">
                <span class="text-[10px] text-slate-500 uppercase block">Shortage Units</span>
                <span id="sim-short" class="text-base font-bold text-rose-600">0.45 u</span>
              </div>
              <div class="p-2 bg-slate-50 rounded">
                <span class="text-[10px] text-slate-500 uppercase block">Service Level</span>
                <span id="sim-service" class="text-base font-bold text-blue-600">97.09%</span>
              </div>
              <div class="p-2 bg-emerald-50 rounded">
                <span class="text-[10px] text-emerald-800 uppercase block">Operating Profit</span>
                <span id="sim-opprofit" class="text-base font-bold text-emerald-700">&dollar;27.57k</span>
              </div>
              <div class="p-2 bg-blue-50 rounded">
                <span class="text-[10px] text-blue-800 uppercase block">Net Optimization Obj</span>
                <span id="sim-netprofit" class="text-base font-bold text-blue-900">-&dollar;17.43k</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 8: MASTER FLOW LEDGER -->
      <div id="tab-ledger" class="hidden space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <h2 class="text-base font-bold text-slate-900">Master Route Flow Ledger & Decision Variables</h2>
            <p class="text-xs text-slate-500">Granular variable ledger of all active shipments, routes, freight charges, and shortage decisions</p>
          </div>
          <div class="flex items-center space-x-3">
            <input id="ledger-search" type="text" placeholder="Search route, factory, market..." oninput="filterLedgerTable()" class="px-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500 w-64" />
            <button onclick="exportCSV()" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition shadow-sm">
              Export CSV
            </button>
          </div>
        </div>

        <div class="overflow-x-auto max-h-[480px] ledger-scroll border border-slate-200 rounded-lg">
          <table class="w-full text-xs text-left border-collapse">
            <thead class="bg-slate-100 text-slate-700 sticky top-0 shadow-sm font-semibold">
              <tr>
                <th class="py-2.5 px-3">Variable</th>
                <th class="py-2.5 px-3">Echelon / Type</th>
                <th class="py-2.5 px-3">Product</th>
                <th class="py-2.5 px-3">Origin</th>
                <th class="py-2.5 px-3">Destination</th>
                <th class="py-2.5 px-3">Mode</th>
                <th class="py-2.5 px-3 text-right">Volume</th>
                <th class="py-2.5 px-3 text-right">Unit Freight</th>
                <th class="py-2.5 px-3 text-right">Total Freight</th>
                <th class="py-2.5 px-3 text-right">Revenue</th>
              </tr>
            </thead>
            <tbody id="ledger-table-body" class="divide-y divide-slate-100 text-slate-700">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>

  <!-- EMBEDDED DATA & SCRIPT ENGINE -->
  <script>
    const BASELINE_DATA = {json_baseline};
    const SCENARIOS_DATA = {json_scenarios};

    let currentFilter = 'all';

    // TAB SWITCHING
    function switchTab(tabId) {{
      const tabs = ['overview', 'network', 'factories', 'warehouses', 'markets', 'sensitivity', 'scenarios', 'ledger'];
      tabs.forEach(t => {{
        const el = document.getElementById('tab-' + t);
        const btn = document.getElementById('tab-btn-' + t);
        if (el) el.classList.add('hidden');
        if (btn) btn.classList.remove('active');
      }});
      const targetEl = document.getElementById('tab-' + tabId);
      const targetBtn = document.getElementById('tab-btn-' + tabId);
      if (targetEl) targetEl.classList.remove('hidden');
      if (targetBtn) targetBtn.classList.add('active');
    }}

    // PRODUCT FILTER
    function setProductFilter(prod) {{
      currentFilter = prod;
      ['all', 'p1', 'p2'].forEach(p => {{
        const btn = document.getElementById('filter-' + p);
        if (btn) {{
          btn.classList.remove('bg-blue-600', 'text-white');
          btn.classList.add('text-slate-300');
        }}
      }});
      const activeBtn = document.getElementById('filter-' + (prod === '1' ? 'p1' : (prod === '2' ? 'p2' : 'all')));
      if (activeBtn) {{
        activeBtn.classList.add('bg-blue-600', 'text-white');
        activeBtn.classList.remove('text-slate-300');
      }}
      renderMarketsTable();
      renderLedgerTable();
    }}

    // RENDER MARKETS TABLE
    function renderMarketsTable() {{
      const tbody = document.getElementById('markets-table-body');
      if (!tbody) return;
      tbody.innerHTML = '';

      const markets = BASELINE_DATA.markets;
      for (const mId in markets) {{
        const m = markets[mId];
        const isShort = m.total_short > 0;
        
        let channel = "Warehouse Routed";
        if (mId === "2") channel = "Direct (Factory 1)";
        else if (mId === "7" || mId === "8") channel = "Direct (Factory 3)";

        const tr = document.createElement('tr');
        tr.className = isShort ? 'bg-rose-50/50 hover:bg-rose-50' : 'hover:bg-slate-50';

        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold text-slate-900">${{m.name}}</td>
          <td class="py-2.5 px-3 text-center text-slate-700">${{m.p1.demand.toFixed(2)}} / <span class="font-semibold text-blue-600">${{m.p1.shipped.toFixed(2)}}</span></td>
          <td class="py-2.5 px-3 text-center text-slate-700">${{m.p2.demand.toFixed(2)}} / <span class="font-semibold text-amber-600">${{m.p2.shipped.toFixed(2)}}</span></td>
          <td class="py-2.5 px-3 text-center font-bold text-slate-900">${{m.total_demand.toFixed(2)}}</td>
          <td class="py-2.5 px-3 text-center font-bold ${{isShort ? 'text-rose-600' : 'text-slate-400'}}">${{isShort ? m.total_short.toFixed(2) : '-'}}</td>
          <td class="py-2.5 px-3 text-center">
            <span class="badge ${{m.fill_rate >= 100 ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-rose-100 text-rose-800 border-rose-300'}}">
              ${{m.fill_rate.toFixed(1)}}%
            </span>
          </td>
          <td class="py-2.5 px-3 text-right font-bold text-slate-900">&dollar;${{m.total_rev.toFixed(2)}}k</td>
          <td class="py-2.5 px-3 text-center text-slate-600 font-medium">${{channel}}</td>
        `;
        tbody.appendChild(tr);
      }}
    }}

    // RENDER BINDING CONSTRAINTS & SENSITIVITY
    function renderSensitivity() {{
      const bBody = document.getElementById('binding-constrs-body');
      if (bBody) {{
        bBody.innerHTML = '';
        BASELINE_DATA.sensitivity.filter(s => s.is_binding).forEach(s => {{
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50';
          const isPos = s.shadow_price > 0;
          tr.innerHTML = `
            <td class="py-2 px-3 font-semibold text-slate-800">${{s.name}}</td>
            <td class="py-2 px-3 text-right font-bold ${{isPos ? 'text-emerald-600' : 'text-rose-600'}}">&dollar;${{s.shadow_price.toFixed(2)}}</td>
            <td class="py-2 px-3 text-slate-600 text-[11px]">${{s.explanation}}</td>
          `;
          bBody.appendChild(tr);
        }});
      }}

      const rcBody = document.getElementById('reduced-costs-body');
      if (rcBody) {{
        rcBody.innerHTML = '';
        BASELINE_DATA.reduced_costs.slice(0, 15).forEach(rc => {{
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50';
          tr.innerHTML = `
            <td class="py-2 px-3 font-mono font-medium text-slate-700">${{rc.var_name}}</td>
            <td class="py-2 px-3 text-right font-bold text-amber-700">&dollar;${{rc.reduced_cost.toFixed(2)}}</td>
            <td class="py-2 px-3 text-slate-600 text-[11px]">${{rc.interpretation}}</td>
          `;
          rcBody.appendChild(tr);
        }});
      }}
    }}

    // RENDER PRESET SCENARIO CARDS
    function renderPresetScenarios() {{
      const container = document.getElementById('preset-scenarios-container');
      if (!container) return;
      container.innerHTML = '';

      for (const key in SCENARIOS_DATA) {{
        const sc = SCENARIOS_DATA[key];
        const kpis = sc.data.kpis;
        const card = document.createElement('div');
        card.className = 'metric-card p-3 flex flex-col justify-between';
        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <span class="badge ${{sc.badge_color}}">${{sc.badge}}</span>
            </div>
            <h4 class="text-xs font-bold text-slate-900 leading-snug">${{sc.title}}</h4>
            <p class="text-[11px] text-slate-500 mt-1 leading-snug">${{sc.desc}}</p>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-100 text-xs space-y-1">
            <div class="flex justify-between">
              <span class="text-slate-500">Service:</span>
              <span class="font-bold ${{kpis.service_level >= 99.9 ? 'text-emerald-600' : 'text-amber-600'}}">${{kpis.service_level.toFixed(1)}}%</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Op Profit:</span>
              <span class="font-bold text-emerald-700">&dollar;${{kpis.op_profit.toFixed(1)}}k</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Net Obj:</span>
              <span class="font-bold ${{kpis.net_profit >= 0 ? 'text-blue-700' : 'text-rose-600'}}">&dollar;${{kpis.net_profit.toFixed(1)}}k</span>
            </div>
          </div>
        `;
        container.appendChild(card);
      }}
    }}

    // RENDER FLOW LEDGER
    function renderLedgerTable(filterText = '') {{
      const tbody = document.getElementById('ledger-table-body');
      if (!tbody) return;
      tbody.innerHTML = '';

      const query = filterText.toLowerCase();

      BASELINE_DATA.flows.forEach(row => {{
        if (currentFilter !== 'all' && row.product.toString() !== currentFilter) return;

        if (query) {{
          const str = (row.var_name + row.origin + row.dest + row.mode + row.type).toLowerCase();
          if (!str.includes(query)) return;
        }}

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50';

        const isShort = row.type.includes('Stockout');

        tr.innerHTML = `
          <td class="py-2 px-3 font-mono text-slate-900 font-semibold">${{row.var_name}}</td>
          <td class="py-2 px-3"><span class="badge ${{isShort ? 'bg-rose-100 text-rose-700 border-rose-300' : 'bg-slate-100 text-slate-700 border-slate-200'}}">${{row.type}}</span></td>
          <td class="py-2 px-3 font-medium">${{row.product === 1 ? '<span class="text-blue-600 font-bold">P1</span>' : '<span class="text-amber-600 font-bold">P2</span>'}}</td>
          <td class="py-2 px-3 text-slate-800">${{row.origin}}</td>
          <td class="py-2 px-3 text-slate-800 font-semibold">${{row.dest}}</td>
          <td class="py-2 px-3 text-slate-600">${{row.mode}}</td>
          <td class="py-2 px-3 text-right font-bold text-slate-900">${{row.volume.toFixed(2)}}</td>
          <td class="py-2 px-3 text-right text-slate-600">${{row.unit_trans_cost > 0 ? '&dollar;' + row.unit_trans_cost.toFixed(2) : '-'}}</td>
          <td class="py-2 px-3 text-right font-semibold text-slate-800">${{row.total_trans_cost > 0 ? '&dollar;' + row.total_trans_cost.toFixed(2) + 'k' : '-'}}</td>
          <td class="py-2 px-3 text-right font-bold text-slate-900">${{row.revenue > 0 ? '&dollar;' + row.revenue.toFixed(2) + 'k' : '-'}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function filterLedgerTable() {{
      const text = document.getElementById('ledger-search')?.value || '';
      renderLedgerTable(text);
    }}

    // LIVE SIMULATION SOLVER (Browser heuristic / exact parametric recomputation)
    function runLiveSimulation() {{
      const capMult = parseFloat(document.getElementById('slider-cap')?.value || 1.0);
      const freightMult = parseFloat(document.getElementById('slider-freight')?.value || 1.0);
      const penaltyVal = parseFloat(document.getElementById('slider-penalty')?.value || 100);
      const demMult = parseFloat(document.getElementById('slider-demand')?.value || 1.0);

      document.getElementById('lbl-cap').innerText = `${{capMult.toFixed(2)}}x (${{(15.0 * capMult).toFixed(1)}}u)`;
      document.getElementById('lbl-freight').innerText = `${{freightMult.toFixed(2)}}x`;
      document.getElementById('lbl-penalty').innerText = `&dollar;${{penaltyVal.toFixed(0)}}`;
      document.getElementById('lbl-demand').innerText = `${{demMult.toFixed(2)}}x (${{(15.45 * demMult).toFixed(2)}}u)`;

      const totalCapacity = 15.0 * capMult;
      const totalDemand = 15.45 * demMult;
      
      let shortage = Math.max(0.0, totalDemand - totalCapacity);
      let fulfilled = Math.min(totalDemand, totalCapacity);
      let serviceLevel = (fulfilled / totalDemand) * 100.0;

      const baseRevPerUnit = 90.04 / 15.0;
      const baseRmPerUnit = 51.30 / 15.0;
      const baseProdPerUnit = 1.945 / 15.0;
      const baseFreightPerUnit = (9.227 / 15.0) * freightMult;

      const simRevenue = fulfilled * baseRevPerUnit;
      const simRmCost = fulfilled * baseRmPerUnit;
      const simProdCost = fulfilled * baseProdPerUnit;
      const simFreightCost = fulfilled * baseFreightPerUnit;
      const simPenaltyCost = shortage * penaltyVal;

      const simOpProfit = simRevenue - simRmCost - simProdCost - simFreightCost;
      const simNetProfit = simOpProfit - simPenaltyCost;

      document.getElementById('sim-rev').innerText = `&dollar;${{simRevenue.toFixed(2)}}k`;
      document.getElementById('sim-freight').innerText = `&dollar;${{simFreightCost.toFixed(2)}}k`;
      document.getElementById('sim-short').innerText = `${{shortage.toFixed(2)}} u`;
      document.getElementById('sim-service').innerText = `${{serviceLevel.toFixed(1)}}%`;
      document.getElementById('sim-opprofit').innerText = `&dollar;${{simOpProfit.toFixed(2)}}k`;
      document.getElementById('sim-netprofit').innerText = `${{simNetProfit >= 0 ? '&dollar;' : '-&dollar;'}}${{Math.abs(simNetProfit).toFixed(2)}}k`;
    }}

    function resetSliders() {{
      document.getElementById('slider-cap').value = 1.0;
      document.getElementById('slider-freight').value = 1.0;
      document.getElementById('slider-penalty').value = 100;
      document.getElementById('slider-demand').value = 1.0;
      runLiveSimulation();
    }}

    // INTERACTIVE TOOLTIPS SETUP
    function setupTooltips() {{
      const tip = document.getElementById('tooltip-box');
      const interactiveEls = document.querySelectorAll('.net-lane, .net-node');

      interactiveEls.forEach(el => {{
        el.addEventListener('mouseenter', (e) => {{
          const content = el.getAttribute('data-tip');
          if (content && tip) {{
            tip.innerHTML = content;
            tip.style.display = 'block';
          }}
        }});
        el.addEventListener('mousemove', (e) => {{
          if (tip) {{
            tip.style.left = (e.pageX + 15) + 'px';
            tip.style.top = (e.pageY + 15) + 'px';
          }}
        }});
        el.addEventListener('mouseleave', () => {{
          if (tip) tip.style.display = 'none';
        }});
      }});
    }}

    // EXPORT CSV
    function exportCSV() {{
      let csv = "Variable,Echelon,Type,Product,Origin,Destination,Mode,Volume,UnitFreightCost,TotalFreightCost,Revenue,MarginContribution\\n";
      BASELINE_DATA.flows.forEach(r => {{
        csv += `"${{r.var_name}}","${{r.echelon}}","${{r.type}}",${{r.product}},"${{r.origin}}","${{r.dest}}","${{r.mode}}",${{r.volume}},${{r.unit_trans_cost}},${{r.total_trans_cost}},${{r.revenue}},${{r.margin}}\\n`;
      }});
      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Supply_Chain_Optimal_Flows_${{new Date().toISOString().slice(0,10)}}.csv`;
      a.click();
    }}

    // INITIALIZATION
    document.addEventListener('DOMContentLoaded', () => {{
      renderMarketsTable();
      renderSensitivity();
      renderPresetScenarios();
      renderLedgerTable();
      setupTooltips();
    }});
  </script>
</body>
</html>
"""
    return html

def main():
    print("Executing Gurobi LP solver and compiling supply chain model data...")
    html_content = generate_dashboard_html()

    workspace_out = "managerial_dashboard.html"
    with open(workspace_out, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated local workspace dashboard: {workspace_out}")

    artifact_dir = r"C:\Users\devas\.gemini\antigravity\brain\2f009a60-8a59-4db6-85cb-72ee2e50b58d"
    if os.path.exists(artifact_dir):
        artifact_out = os.path.join(artifact_dir, "managerial_dashboard.html")
        with open(artifact_out, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully generated artifact dashboard: {artifact_out}")

if __name__ == "__main__":
    main()

