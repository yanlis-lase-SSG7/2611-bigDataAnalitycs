"""Create measured Assignment II figures from saved predictions and reports."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import networkx as nx
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs_assignment2"
FIGURES = ROOT / "figures"
SAVED = ROOT / "outputs_ml_graph"
MODELS = [
    ("spark_random_forest", "Spark RF", "#0b7285"),
    ("sklearn_random_forest", "sklearn RF", "#e09f3e"),
    ("sklearn_logistic_regression", "sklearn LR", "#7c4d8e"),
]


def save(name: str) -> None:
    FIGURES.mkdir(exist_ok=True)
    plt.savefig(FIGURES / name, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()


def confusion_matrix() -> None:
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    fig.suptitle("Test confusion matrices (threshold selected on validation)", fontsize=14)
    for row, split in enumerate(("hash", "temporal")):
        for col, (key, label, _) in enumerate(MODELS):
            m = json.loads((OUT / f"{split}_{key}_metrics.json").read_text(encoding="utf-8"))
            c = m["confusion_matrix"]
            values = np.array([[c["tn"], c["fp"]], [c["fn"], c["tp"]]])
            ax = axes[row, col]
            ax.imshow(values, cmap="Blues", vmin=0, vmax=values.max())
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, f"{values[i, j]:,}", ha="center", va="center",
                            color="white" if values[i, j] > values.max() / 2 else "#17243a",
                            fontsize=11, fontweight="bold")
            ax.set_xticks([0, 1], ["On time", "Delayed"])
            ax.set_yticks([0, 1], ["On time", "Delayed"])
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            ax.set_title(f"{split.title()} · {label}\nF1 {m['f1']:.3f}")
    save("fig5_ml_confusion_matrix.png")


def importance() -> None:
    data = pd.read_csv(SAVED / "feature_importance_report.csv").sort_values("Importance")
    fig, ax = plt.subplots(figsize=(8.5, 5.1))
    ax.barh(data.Feature, data.Importance, color="#0b7285")
    ax.set_xlabel("Relative feature importance")
    ax.set_title("Assignment I Spark Random Forest · saved baseline")
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save("fig6_feature_importance.png")


def pr_roc_curves() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    for row, split in enumerate(("hash", "temporal")):
        for key, label, color in MODELS:
            data = pd.read_csv(OUT / "curves" / f"{split}_{key}.csv")
            m = json.loads((OUT / f"{split}_{key}_metrics.json").read_text(encoding="utf-8"))
            roc = data[data.curve == "roc"]
            pr = data[data.curve == "pr"]
            axes[row, 0].plot(roc.x, roc.y, label=f"{label} ({m['roc_auc']:.3f})",
                              color=color, linewidth=1.7)
            axes[row, 1].plot(pr.x, pr.y, label=f"{label} ({m['pr_auc_trapezoid']:.3f})",
                              color=color, linewidth=1.7)
        axes[row, 0].plot([0, 1], [0, 1], linestyle="--", color="#9aa5ae", linewidth=1)
        prevalence = m["test_prevalence"]
        axes[row, 1].axhline(prevalence, linestyle="--", color="#9aa5ae", linewidth=1,
                             label=f"Prevalence {prevalence:.3f}")
        for col, title, xlabel, ylabel in [
            (0, "ROC", "False positive rate", "True positive rate"),
            (1, "Precision–recall", "Recall", "Precision"),
        ]:
            ax = axes[row, col]
            ax.set_title(f"{split.title()} test · {title}")
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.grid(alpha=0.2)
            ax.legend(fontsize=8, loc="best")
    fig.suptitle("Curves calculated from saved per-order test scores", fontsize=14)
    save("fig7_pr_roc_curves.png")


def graph_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    routes = pd.read_csv(SAVED / "seller_customer_routes_report.csv")
    states = pd.read_csv(SAVED / "graph_network_metrics.csv")
    if len(states) != 27 or len(routes) != 409 or routes.transaction_volume.sum() != 96470:
        raise ValueError("Graph inputs differ from saved preparation audit")
    return routes, states


def graph_topology(routes: pd.DataFrame, states: pd.DataFrame) -> None:
    graph = nx.DiGraph()
    for row in routes.itertuples(index=False):
        graph.add_edge(row.seller_state, row.customer_state,
                       weight=row.transaction_volume, delay=row.route_delay_rate_pct)
    if graph.number_of_nodes() != 27 or graph.number_of_edges() != 409:
        raise ValueError("Unexpected graph topology")
    # Draw a legible display subset; statistics and analysis use all 409 edges.
    top = routes.nlargest(35, "transaction_volume")
    display = nx.DiGraph()
    display.add_nodes_from(graph.nodes)
    for row in top.itertuples(index=False):
        display.add_edge(row.seller_state, row.customer_state, weight=row.transaction_volume,
                         delay=row.route_delay_rate_pct)
    # A fixed shell keeps every state legible; positions are schematic, not geography.
    pos = nx.shell_layout(display, nlist=[["SP"], sorted(n for n in display if n != "SP")])
    out_strength = dict(zip(states.State, states.Out_Strength_Orders))
    sizes = [180 + 720 * np.sqrt(out_strength.get(node, 0) / max(out_strength.values()))
             for node in display.nodes]
    edges = list(display.edges(data=True))
    widths = [0.5 + 3.0 * np.sqrt(e[2]["weight"] / max(top.transaction_volume)) for e in edges]
    colors = [e[2]["delay"] for e in edges]
    fig, ax = plt.subplots(figsize=(10, 10))
    nx.draw_networkx_nodes(display, pos, node_size=sizes, node_color="#0b7285",
                           edgecolors="white", linewidths=0.8, ax=ax)
    label_positions = {
        node: (point[0] * (1.09 if node != "SP" else 1),
               point[1] * (1.09 if node != "SP" else 1))
        for node, point in pos.items()
    }
    nx.draw_networkx_labels(display, label_positions, font_color="#17243a", font_size=8,
                            font_weight="bold", ax=ax)
    nx.draw_networkx_edges(
        display, pos, edgelist=[(u, v) for u, v, _ in edges], width=widths,
        edge_color=colors, edge_cmap=plt.cm.YlOrRd, edge_vmin=0,
        edge_vmax=max(colors), alpha=0.55, arrows=True, arrowsize=8, ax=ax
    )
    color_scale = plt.cm.ScalarMappable(norm=Normalize(vmin=0, vmax=max(colors)), cmap="YlOrRd")
    plt.colorbar(color_scale, ax=ax, label="Delay rate (%)", shrink=0.65)
    ax.set_title("Olist seller-state → customer-state network\nSchematic layout; 35 highest-volume edges shown of 409")
    ax.set_xlim(-1.24, 1.24)
    ax.set_ylim(-1.24, 1.24)
    ax.axis("off")
    fig.tight_layout()
    save("fig8_graph_network_topology.png")


def state_centrality(states: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True)
    for ax, column, title, color in [
        (axes[0], "PageRank_Score", "Top 10 PageRank", "#0b7285"),
        (axes[1], "Out_Strength_Orders", "Top 10 origin order volume", "#e09f3e"),
    ]:
        top = states.nlargest(10, column).sort_values(column)
        ax.barh(top.State, top[column], color=color)
        ax.set_title(title)
        ax.grid(axis="x", alpha=0.2)
        ax.set_axisbelow(True)
    fig.suptitle("State-level graph metrics · directed origin–destination network")
    save("fig9_state_pagerank_centrality.png")


def route_volume_delay(routes: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 5.5))
    ax.scatter(routes.transaction_volume, routes.route_delay_rate_pct,
               s=16, alpha=0.5, color="#0b7285")
    ax.set_xscale("log")
    ax.set_xlabel("Orders on origin–destination relation (log scale)")
    ax.set_ylabel("Delayed orders / all orders on relation (%)")
    ax.set_title("Route volume and observed delay rate · 409 relations")
    ax.grid(alpha=0.2)
    for origin, dest in [("SP", "MA"), ("SP", "AL"), ("SP", "RJ")]:
        row = routes[(routes.seller_state == origin) & (routes.customer_state == dest)].iloc[0]
        ax.annotate(f"{origin}→{dest} (n={row.transaction_volume})",
                    (row.transaction_volume, row.route_delay_rate_pct),
                    xytext=(6, 5), textcoords="offset points", fontsize=8)
    fig.tight_layout()
    save("fig10_route_volume_delay.png")


def main() -> None:
    confusion_matrix()
    importance()
    pr_roc_curves()
    routes, states = graph_data()
    graph_topology(routes, states)
    state_centrality(states)
    route_volume_delay(routes)
    print("Saved six 300-DPI figures to", FIGURES)


if __name__ == "__main__":
    main()
