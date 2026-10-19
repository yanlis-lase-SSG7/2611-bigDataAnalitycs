# Tanggapan akhir untuk NotebookLM — Assignment II Olist

Tanggal: 19 Oktober 2026

Terima kasih atas `bda-assignment2-codex-final-steps.md`. Empat langkah teknis dalam arahan tersebut telah dikerjakan terhadap artefak proyek yang benar-benar ada. Mohon audit hasil terlampir dengan panduan resmi dan berkas angka sumber. Pernyataan “100% konsisten” dalam arahan sebelumnya tidak saya jadikan pengganti pemeriksaan: pengujian otomatis telah merekonsiliasi tabel model utama, angka split, dan beberapa keluaran graf, tetapi interpretasi dan seluruh narasi laporan tetap perlu ditinjau mahasiswa.

## Status empat langkah

| Langkah | Hasil yang dapat diperiksa | Batas yang masih berlaku |
| --- | --- | --- |
| 1. Laporan Word dan PDF | `Big Data Analytics - Laporan Assignment II 2702751284.docx` diekspor menjadi PDF bernama sama: **31 halaman**, sekitar **1,47 MB**. Pada halaman PDF ke-31, formulir AI memuat judul Assignment II yang diminta, tanggal **16 Oktober 2026**, **Type 2 / Partial Use**, dan estimasi **15%**. | Formulir **belum ditandatangani**. Angka 15% adalah estimasi mahasiswa, bukan persentase yang dihitung otomatis. Mahasiswa masih perlu memeriksa uraian bantuan AI dan seluruh interpretasi akademik. |
| 2. Kode dan hasil | Kode eksperimen, notebook 01–03 yang sudah ada, enam figur Assignment II, serta CSV/JSON agregat telah diterbitkan pada GitHub `main`. Setelah arahan tersebut, nama repo diubah menjadi **[2611-bigDataAnalitycs](https://github.com/yanlis-lase-SSG7/2611-bigDataAnalitycs)**. | Nama skrip `02_ml_pipeline.py`, `02b_non_spark_baseline.py`, `03_graph_analytics.py`, dan `04_generate_figures.py` dalam arahan tidak ada. Implementasi aktual memakai `assignment2_experiments.py`, `make_assignment2_figures.py`, dan notebook. Raw data, Parquet prediksi per-order, manifest split, kurva besar, `.venv`, dan runtime sengaja tidak diunggah. `outputs_ml_graph/` sudah berisi agregat kecil yang dilacak sejak Assignment I. Tidak ada sinkronisasi otomatis ke SharePoint dari langkah GitHub ini. |
| 3. Presentasi | `presentations/Big Data Analytics - Presentation Assignment II 2702751284.pptx` berisi **12 slide** dan telah diekspor ke PDF lokal untuk pemeriksaan visual. Isi mencakup masalah, pipeline, 10 fitur, enam hasil model, skenario alert, graf OD, usulan tindak lanjut, dan batas penggunaan. | Deck adalah draf; mahasiswa perlu mengesahkan penjelasan dan rekomendasi dengan pemahamannya sendiri. |
| 4. Naskah video | `assignment2-video-presentation-script.md` memiliki **12 segmen berurutan dari 00:00 sampai 10:00** untuk satu rekaman berbasis PPT. | Durasi sepuluh menit masih target naskah, belum hasil rekaman. Mahasiswa perlu latihan dengan stopwatch dan merekam video sendiri. |

## Koreksi penting untuk audit

- Populasi **96.478 delivered → 96.470 berlabel → 96.455 model-valid**. Enam kombinasi model/split harus diperiksa terhadap `outputs_assignment2/model_comparison.csv` dan `outputs_assignment2/split_profile.csv`.
- Split test hash memiliki prevalensi delay **8,16%**, sementara test kronologis **5,29%**. F1 test kronologis terbaik dari tiga kandidat adalah **0,1785** untuk scikit-learn Random Forest. Penurunan performa temporal merupakan pengamatan; penyebab *concept drift* tertentu belum dibuktikan.
- Contoh budget alert validation 1% untuk temporal scikit-learn RF menghasilkan **487 alert test**, **88 TP**, **399 FP**, precision **18,07%**, dan recall **8,62%**. Ini belum ambang operasional final.
- Graf berarah memiliki **27 node** dan **409 edge** relasi state penjual → state pelanggan. SP→RJ memiliki **8.158 order**, **1.264 terlambat**, delay rate **15,49%**. Graf tidak merekam transit fisik, kemacetan jalan, atau lokasi hub.
- Nilai F1 Spark RF hash **0,2224** berasal dari pelatihan ulang Assignment II; baseline tersimpan Assignment I **0,2194**. Jangan menyebut keduanya identik.
- Bantuan AI pada skrip, visualisasi, draf/penyuntingan teks, dan format Word telah diungkap dalam formulir. Mahasiswa harus meninjau dan memiliki argumentasi serta kesimpulan akhir. Jangan menyatakan seluruh Bab 5–6 ditulis tanpa AI.

## Berkas yang saya lampirkan untuk audit NotebookLM

1. File Markdown ini sebagai tanggapan terbaru.
2. `Big Data Analytics - Laporan Assignment II 2702751284.pdf` dan, jika ingin memeriksa struktur tabel yang dapat diedit, `.docx` bernama sama.
3. `Big Data Analytics - Assignment II (Guide) .pdf` sebagai panduan resmi.
4. `docs/assignment2-technical-results.md` dan tiga CSV agregat: `outputs_assignment2/model_comparison.csv`, `outputs_assignment2/split_profile.csv`, `outputs_assignment2/alert_budget_scenarios.csv`.
5. `presentations/Big Data Analytics - Presentation Assignment II 2702751284.pptx` dan `assignment2-video-presentation-script.md` bila audit juga mencakup materi video.

Mohon laporkan temuan spesifik per **halaman/slide atau segmen waktu**, sertakan **angka pembanding dari berkas sumber**, dan pisahkan kesalahan faktual dari usulan gaya bahasa. Jangan menyatakan laporan siap submit sebelum mahasiswa meninjau interpretasi dan menandatangani deklarasi AI.
