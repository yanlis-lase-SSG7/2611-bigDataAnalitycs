# Assignment II — hasil teknis terukur

Lembar ini dihasilkan otomatis dari CSV/JSON proyek. Isinya hanya populasi, konfigurasi,
metrik, dan batas pembacaan yang dapat diverifikasi; analisis, argumentasi, dan kesimpulan
Assignment II tetap ditulis mahasiswa.

## Populasi dan label

- Order delivered dengan label valid: **96.470**; model-valid dengan 10 fitur lengkap: **96.455**.
- Label `is_delayed=1` bila tanggal/waktu diterima pelanggan lebih lambat daripada estimasi.
- Data prediksi memakai 10 fitur yang tercatat dalam `outputs_ml_graph/model_evaluation_report.json`.
- Split hash memakai membership Assignment I; split waktu mengurutkan `order_purchase_timestamp`,
  memakai `order_id` untuk memutus urutan saat timestamp sama, lalu membagi 64/16/20.

## Profil split

| Skema | Bagian | Order | Terlambat | Prevalensi | Pembelian paling awal | Pembelian paling akhir |
| --- | --- | ---: | ---: | ---: | --- | --- |
| hash | train | 61,826 | 4,994 | 8.08% | 2016-10-03 12:44:50 | 2018-08-29 18:00:37 |
| hash | validation | 15,513 | 1,272 | 8.20% | 2016-10-04 12:16:33 | 2018-08-29 00:56:12 |
| hash | test | 19,116 | 1,559 | 8.16% | 2016-10-03 19:56:50 | 2018-08-29 12:48:09 |
| temporal | train | 61,731 | 5,553 | 9.00% | 2016-10-03 12:44:50 | 2018-03-20 12:23:27 |
| temporal | validation | 15,433 | 1,251 | 8.11% | 2018-03-20 12:24:44 | 2018-05-26 21:41:31 |
| temporal | test | 19,291 | 1,021 | 5.29% | 2018-05-26 21:50:39 | 2018-08-29 18:00:37 |

## Perbandingan hasil test

Ambang tiap model dipilih dari validation dengan F1 maksimum; test tidak dipakai memilih ambang.
Semua model memakai order dan label yang sama **di dalam skema split yang sama**. Data test
hash dan temporal berbeda, sehingga perbandingan lintas skema perlu memperhatikan prevalensi.

| Split | Model | Test n | Precision | Recall | F1 | PR-AUC¹ | ROC-AUC | Ambang |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hash | scikit-learn LR | 19,116 | 0.1490 | 0.4221 | 0.2202 | 0.1358 | 0.6567 | 0.1046 |
| hash | scikit-learn RF | 19,116 | 0.1532 | 0.3906 | 0.2201 | 0.1591 | 0.6683 | 0.1063 |
| hash | Spark RF (run baru) | 19,116 | 0.1477 | 0.4503 | 0.2224 | 0.1432 | 0.6634 | 0.0997 |
| temporal | scikit-learn LR | 19,291 | 0.0682 | 0.3457 | 0.1139 | 0.0860 | 0.6621 | 0.1361 |
| temporal | scikit-learn RF | 19,291 | 0.1035 | 0.6464 | 0.1785 | 0.1248 | 0.7147 | 0.1481 |
| temporal | Spark RF (run baru) | 19,291 | 0.0517 | 0.2693 | 0.0867 | 0.0532 | 0.4919 | 0.1285 |

¹ PR-AUC memakai interpolasi trapezoid yang sama dengan notebook 02; ini berbeda dari
*average precision* scikit-learn. Logistic Regression memakai `StandardScaler` yang dilatih
hanya pada train; kedua Random Forest memakai 10 fitur mentah. Semua run berlangsung pada
satu mesin lokal. `fit_wall_seconds` adalah pengamatan satu run, bukan benchmark kecepatan
yang dikontrol atau bukti skalabilitas cluster.

Baseline Assignment I yang tersimpan memiliki test F1 **0.2194** dan PR-AUC **0.1409** pada split hash. Spark RF yang dilatih ulang di sini memakai order test dan konfigurasi utama yang sama, tetapi hasilnya tidak identik; jangan
mengganti angka baseline lama dengan angka run baru tanpa label yang jelas.

## Skenario kapasitas pemeriksaan

Mahasiswa memprioritaskan precision. Tabel berikut **bukan** keputusan ambang akhir:
1%, 5%, dan 10% adalah contoh batas jumlah peringatan pada validation.
Untuk setiap batas, ambang dipilih dari skor validation dengan seluruh skor seri
diperlakukan sebagai satu kelompok; metrik test dihitung setelah ambang terkunci.
Jumlah peringatan test dapat berbeda dari persentase anggaran validation.
Skor model belum dikalibrasi sebagai probabilitas; pilihan ambang memerlukan
kapasitas pemeriksaan dan konsekuensi bisnis yang ditetapkan mahasiswa.

| Split | Model | Anggaran validasi | Precision validasi | Peringatan test | TP test | FP test | Precision test | Recall test |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hash | scikit-learn LR | 1.00% | 12.90% | 221 | 32 | 189 | 14.48% | 2.05% |
| hash | scikit-learn LR | 5.00% | 13.94% | 985 | 150 | 835 | 15.23% | 9.62% |
| hash | scikit-learn LR | 10.00% | 15.80% | 1,972 | 327 | 1,645 | 16.58% | 20.97% |
| hash | scikit-learn RF | 1.00% | 33.55% | 211 | 74 | 137 | 35.07% | 4.75% |
| hash | scikit-learn RF | 5.00% | 22.19% | 1,048 | 221 | 827 | 21.09% | 14.18% |
| hash | scikit-learn RF | 10.00% | 18.05% | 1,961 | 351 | 1,610 | 17.90% | 22.51% |
| hash | Spark RF (run baru) | 1.00% | 22.58% | 221 | 42 | 179 | 19.00% | 2.69% |
| hash | Spark RF (run baru) | 5.00% | 19.23% | 1,004 | 193 | 811 | 19.22% | 12.38% |
| hash | Spark RF (run baru) | 10.00% | 16.70% | 1,947 | 334 | 1,613 | 17.15% | 21.42% |
| temporal | scikit-learn LR | 1.00% | 22.08% | 1,403 | 134 | 1,269 | 9.55% | 13.12% |
| temporal | scikit-learn LR | 5.00% | 21.14% | 2,864 | 203 | 2,661 | 7.09% | 19.88% |
| temporal | scikit-learn LR | 10.00% | 19.25% | 3,829 | 243 | 3,586 | 6.35% | 23.80% |
| temporal | scikit-learn RF | 1.00% | 17.53% | 487 | 88 | 399 | 18.07% | 8.62% |
| temporal | scikit-learn RF | 5.00% | 18.55% | 2,539 | 322 | 2,217 | 12.68% | 31.54% |
| temporal | scikit-learn RF | 10.00% | 18.54% | 4,208 | 484 | 3,724 | 11.50% | 47.40% |
| temporal | Spark RF (run baru) | 1.00% | 18.18% | 504 | 28 | 476 | 5.56% | 2.74% |
| temporal | Spark RF (run baru) | 5.00% | 20.75% | 2,355 | 155 | 2,200 | 6.58% | 15.18% |
| temporal | Spark RF (run baru) | 10.00% | 19.38% | 3,634 | 211 | 3,423 | 5.81% | 20.67% |

## Graf asal–tujuan state

- Graf `networkx.DiGraph`: **27 node**, **409 edge** dari **96,470 order** berlabel.
- Edge menyatakan state penjual → state pelanggan; tidak mencatat transit, jalur kendaraan,
  atau lokasi gudang fisik.
- PageRank, tiga nilai teratas: SP (0.2997), RJ (0.1182), MG (0.1059).
- Betweenness topologis, tiga nilai teratas: MG (0.0506), SP (0.0438), PR (0.0412).
- Volume order asal, tiga nilai teratas: SP (68,415 order), MG (7,647 order), PR (7,429 order).

| Relasi OD | Order | Order terlambat | Delay rate |
| --- | ---: | ---: | ---: |
| SP→RJ | 8,158 | 1,264 | 15.49% |
| SP→MA | 491 | 104 | 21.18% |
| SP→AL | 255 | 67 | 26.27% |

## Figur yang dibuat dari hasil terukur

- [Gambar 5 — Confusion matrix](../figures/fig5_ml_confusion_matrix.png): enam kombinasi model/split.
- [Gambar 6 — Feature importance baseline](../figures/fig6_feature_importance.png):
  model Assignment I tersimpan, tidak mewakili seluruh model baru.
- [Gambar 7 — Kurva ROC/PR](../figures/fig7_pr_roc_curves.png): dari skor dan label
  per-order test yang disimpan lokal di `outputs_assignment2/predictions/`.
- [Gambar 8 — Topologi OD](../figures/fig8_graph_network_topology.png): posisi node skematis;
  hanya 35 edge dengan volume tertinggi ditampilkan agar terbaca.
- [Gambar 9 — PageRank dan volume asal](../figures/fig9_state_pagerank_centrality.png).
- [Gambar 10 — Volume dan delay rate relasi OD](../figures/fig10_route_volume_delay.png):
  titik bervolume kecil perlu dibaca bersama denominator.

## Bagian yang ditulis mahasiswa untuk laporan

- **Bab 5.3–5.4:** alasan memilih kedua pembanding non-Spark dan batas keadilan perbandingan.
- **Bab 5.6:** interpretasi perbedaan model dan split, trade-off precision/recall, serta batas
  penggunaan hasil untuk keputusan operasional.
- **Bab 6.2:** pertanyaan tentang prioritas relasi OD dan konektivitas state, interpretasi
  metrik graf, batas klaim, dan insight yang menurut mahasiswa didukung data.
- **Kesimpulan:** jawaban mahasiswa atas masalah yang dipilih, keterbatasan, dan langkah lanjut.

Jangan menyimpulkan bahwa sebuah fitur adalah penyebab delay, bahwa sebuah state adalah
hub transit, atau bahwa sebuah rute merupakan kemacetan fisik hanya dari output ini.
