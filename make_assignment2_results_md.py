"""Regenerate a factual, interpretation-free Assignment II results sheet."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs_assignment2"
DOC = ROOT / "docs" / "assignment2-technical-results.md"
BASELINE = ROOT / "outputs_ml_graph" / "model_evaluation_report.json"
GRAPH = ROOT / "outputs_ml_graph" / "graph_preparation_audit.json"
STATES = ROOT / "outputs_ml_graph" / "graph_network_metrics.csv"
ROUTES = ROOT / "outputs_ml_graph" / "seller_customer_routes_report.csv"


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def main() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    models = pd.read_csv(OUT / "model_comparison.csv")
    scenarios = pd.read_csv(OUT / "alert_budget_scenarios.csv")
    splits = pd.read_csv(OUT / "split_profile.csv")
    states = pd.read_csv(STATES)
    routes = pd.read_csv(ROUTES)
    if len(models) != 6 or set(models.split) != {"hash", "temporal"}:
        raise ValueError("Expected six model evaluations across both split schemes")
    if len(scenarios) != 18:
        raise ValueError("Expected 18 alert-budget scenarios")
    lines = [
        "# Assignment II — hasil teknis terukur",
        "",
        "Lembar ini dihasilkan otomatis dari CSV/JSON proyek. Isinya hanya populasi, konfigurasi,",
        "metrik, dan batas pembacaan yang dapat diverifikasi; analisis, argumentasi, dan kesimpulan",
        "Assignment II tetap ditulis mahasiswa.",
        "",
        "## Populasi dan label",
        "",
        "- Order delivered dengan label valid: **96.470**; model-valid dengan 10 fitur lengkap: **96.455**.",
        "- Label `is_delayed=1` bila tanggal/waktu diterima pelanggan lebih lambat daripada estimasi.",
        "- Data prediksi memakai 10 fitur yang tercatat dalam `outputs_ml_graph/model_evaluation_report.json`.",
        "- Split hash memakai membership Assignment I; split waktu mengurutkan `order_purchase_timestamp`,",
        "  memakai `order_id` untuk memutus urutan saat timestamp sama, lalu membagi 64/16/20.",
        "",
        "## Profil split",
        "",
        "| Skema | Bagian | Order | Terlambat | Prevalensi | Pembelian paling awal | Pembelian paling akhir |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in splits.itertuples(index=False):
        lines.append(f"| {row.scheme} | {row.split} | {row.orders:,} | {row.delayed_orders:,} | "
                     f"{pct(row.delay_prevalence)} | {row.purchase_min} | {row.purchase_max} |")
    lines += [
        "",
        "## Perbandingan hasil test",
        "",
        "Ambang tiap model dipilih dari validation dengan F1 maksimum; test tidak dipakai memilih ambang.",
        "Semua model memakai order dan label yang sama **di dalam skema split yang sama**. Data test",
        "hash dan temporal berbeda, sehingga perbandingan lintas skema perlu memperhatikan prevalensi.",
        "",
        "| Split | Model | Test n | Precision | Recall | F1 | PR-AUC¹ | ROC-AUC | Ambang |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "spark_random_forest": "Spark RF (run baru)",
        "sklearn_random_forest": "scikit-learn RF",
        "sklearn_logistic_regression": "scikit-learn LR",
    }
    for row in models.sort_values(["split", "model"]).itertuples(index=False):
        lines.append(f"| {row.split} | {labels[row.model]} | {row.test_orders:,} | "
                     f"{row.precision:.4f} | {row.recall:.4f} | {row.f1:.4f} | "
                     f"{row.pr_auc_trapezoid:.4f} | {row.roc_auc:.4f} | {row.threshold:.4f} |")
    lines += [
        "",
        "¹ PR-AUC memakai interpolasi trapezoid yang sama dengan notebook 02; ini berbeda dari",
        "*average precision* scikit-learn. Logistic Regression memakai `StandardScaler` yang dilatih",
        "hanya pada train; kedua Random Forest memakai 10 fitur mentah. Semua run berlangsung pada",
        "satu mesin lokal. `fit_wall_seconds` adalah pengamatan satu run, bukan benchmark kecepatan",
        "yang dikontrol atau bukti skalabilitas cluster.",
        "",
        f"Baseline Assignment I yang tersimpan memiliki test F1 **{baseline['delay_f1']:.4f}** dan "
        f"PR-AUC **{baseline['pr_auc']:.4f}** pada split hash. Spark RF yang dilatih ulang di sini "
        "memakai order test dan konfigurasi utama yang sama, tetapi hasilnya tidak identik; jangan",
        "mengganti angka baseline lama dengan angka run baru tanpa label yang jelas.",
        "",
        "## Skenario kapasitas pemeriksaan",
        "",
        "Mahasiswa memprioritaskan precision. Tabel berikut **bukan** keputusan ambang akhir:",
        "1%, 5%, dan 10% adalah contoh batas jumlah peringatan pada validation.",
        "Untuk setiap batas, ambang dipilih dari skor validation dengan seluruh skor seri",
        "diperlakukan sebagai satu kelompok; metrik test dihitung setelah ambang terkunci.",
        "Jumlah peringatan test dapat berbeda dari persentase anggaran validation.",
        "Skor model belum dikalibrasi sebagai probabilitas; pilihan ambang memerlukan",
        "kapasitas pemeriksaan dan konsekuensi bisnis yang ditetapkan mahasiswa.",
        "",
        "| Split | Model | Anggaran validasi | Precision validasi | Peringatan test | TP test | FP test | Precision test | Recall test |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in scenarios.sort_values(
        ["split", "model", "validation_alert_budget_fraction"]
    ).itertuples(index=False):
        lines.append(
            f"| {row.split} | {labels[row.model]} | "
            f"{pct(row.validation_alert_budget_fraction)} | "
            f"{pct(row.validation_precision)} | {row.test_alerts:,} | "
            f"{row.test_tp:,} | {row.test_fp:,} | "
            f"{pct(row.test_precision)} | {pct(row.test_recall)} |"
        )
    lines += [
        "",
        "## Graf asal–tujuan state",
        "",
        f"- Graf `networkx.DiGraph`: **{graph['nodes']} node**, **{graph['routes']} edge** "
        f"dari **{graph['graph_orders']:,} order** berlabel.",
        "- Edge menyatakan state penjual → state pelanggan; tidak mencatat transit, jalur kendaraan,",
        "  atau lokasi gudang fisik.",
    ]
    for name, column in [("PageRank", "PageRank_Score"),
                         ("Betweenness topologis", "Topological_Betweenness"),
                         ("Volume order asal", "Out_Strength_Orders")]:
        top = states.nlargest(3, column)
        items = ", ".join(f"{r.State} ({getattr(r, column):.4f})" if column != "Out_Strength_Orders"
                          else f"{r.State} ({getattr(r, column):,} order)"
                          for r in top.itertuples(index=False))
        lines.append(f"- {name}, tiga nilai teratas: {items}.")
    lines += [
        "",
        "| Relasi OD | Order | Order terlambat | Delay rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for origin, destination in [("SP", "RJ"), ("SP", "MA"), ("SP", "AL")]:
        row = routes[(routes.seller_state == origin) &
                     (routes.customer_state == destination)].iloc[0]
        lines.append(f"| {origin}→{destination} | {row.transaction_volume:,} | "
                     f"{row.delayed_orders:,} | {row.route_delay_rate_pct:.2f}% |")
    lines += [
        "",
        "## Figur yang dibuat dari hasil terukur",
        "",
        "- [Gambar 5 — Confusion matrix](../figures/fig5_ml_confusion_matrix.png): enam kombinasi model/split.",
        "- [Gambar 6 — Feature importance baseline](../figures/fig6_feature_importance.png):",
        "  model Assignment I tersimpan, tidak mewakili seluruh model baru.",
        "- [Gambar 7 — Kurva ROC/PR](../figures/fig7_pr_roc_curves.png): dari skor dan label",
        "  per-order test yang disimpan lokal di `outputs_assignment2/predictions/`.",
        "- [Gambar 8 — Topologi OD](../figures/fig8_graph_network_topology.png): posisi node skematis;",
        "  hanya 35 edge dengan volume tertinggi ditampilkan agar terbaca.",
        "- [Gambar 9 — PageRank dan volume asal](../figures/fig9_state_pagerank_centrality.png).",
        "- [Gambar 10 — Volume dan delay rate relasi OD](../figures/fig10_route_volume_delay.png):",
        "  titik bervolume kecil perlu dibaca bersama denominator.",
        "",
        "## Bagian yang ditulis mahasiswa untuk laporan",
        "",
        "- **Bab 5.3–5.4:** alasan memilih kedua pembanding non-Spark dan batas keadilan perbandingan.",
        "- **Bab 5.6:** interpretasi perbedaan model dan split, trade-off precision/recall, serta batas",
        "  penggunaan hasil untuk keputusan operasional.",
        "- **Bab 6.2:** pertanyaan tentang prioritas relasi OD dan konektivitas state, interpretasi",
        "  metrik graf, batas klaim, dan insight yang menurut mahasiswa didukung data.",
        "- **Kesimpulan:** jawaban mahasiswa atas masalah yang dipilih, keterbatasan, dan langkah lanjut.",
        "",
        "Jangan menyimpulkan bahwa sebuah fitur adalah penyebab delay, bahwa sebuah state adalah",
        "hub transit, atau bahwa sebuah rute merupakan kemacetan fisik hanya dari output ini.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote", DOC)


if __name__ == "__main__":
    main()
