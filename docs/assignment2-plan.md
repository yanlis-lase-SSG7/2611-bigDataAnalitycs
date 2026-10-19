# Rencana kerja Assignment II — Olist

Sumber utama: `Big Data Analytics - Assignment II (Guide) .pdf` (4 halaman). Assignment II adalah kelanjutan individual Assignment I. Fokusnya pengolahan Big Data menggunakan machine learning hingga evaluasi dan analisis, ditambah graph analytics. Panduan tidak mencantumkan tenggat. Mahasiswa telah memilih tetap memprediksi keterlambatan order Olist dengan 10 fitur lama; pembanding scikit-learn Random Forest dan Logistic Regression; split hash dan waktu; serta analisis volume/delay relasi OD dan konektivitas state.

## Ketentuan penyerahan

- Laporan lanjutan Bab 1–6, maksimal **40 halaman**, mencakup daftar isi/gambar/tabel. Bab 5 memuat preprocessing, feature engineering, algoritma, proses pengembangan model dengan dan tanpa Spark MLlib (atau library relevan), evaluasi, dan analisis. Bab 6 memuat pengembangan graph serta analisis/insight.
- Tautan dataset dan tautan source code **yang sudah dieksekusi**.
- Slide Assignment II dan video presentasi maksimal **10 menit**.
- Porsi bantuan AI maksimal 50% dan deklarasi AI wajib. Panduan secara eksplisit menempatkan pemilihan data, perancangan pipeline/feature engineering, pemilihan algoritma/strategi model, interpretasi/perbandingan evaluasi, analisis graf, argumentasi, dan kesimpulan pada mahasiswa. AI dapat membantu sintaks Python, debugging, penjelasan error/contoh library, tata bahasa, serta tabel/grafik/visualisasi. Mahasiswa mengisi deklarasinya sendiri.

## Peta kebutuhan terhadap proyek saat ini

| Kebutuhan panduan | Yang sudah tersedia | Pekerjaan tersisa |
| --- | --- | --- |
| Pilih data dan jelaskan masalah | Mahasiswa memilih dataset Olist dan kasus keterlambatan order; Assignment I menyediakan baseline | Mahasiswa menuliskan alasan dan rumusan masalah dalam kata-kata sendiri |
| Preprocessing dan feature engineering | Notebook 01–02, Parquet, audit kualitas/label, dan 10 fitur per order digunakan kembali | Mahasiswa menjelaskan alasan mempertahankan fitur dan titik waktu prediksi |
| Algoritma dan pengembangan **dengan dan tanpa Spark MLlib** | Spark Random Forest serta scikit-learn Random Forest dan Logistic Regression sudah dijalankan pada kedua split; output terpisah di `outputs_assignment2/` | Mahasiswa menulis justifikasi model dan batas perbandingan; kode/hasil diuji sebelum laporan |
| Evaluasi dan analisis ML | Enam JSON metrik, skor per-order, kurva, confusion matrix, profil split, 18 skenario anggaran peringatan validation, dan ringkasan teknis sudah dibuat | Mahasiswa menginterpretasikan hasil hash versus waktu, trade-off metrik, serta menetapkan kapasitas pemeriksaan atau kriteria precision yang nyata |
| Graph analytics | Notebook 03 menyimpan graf OD NetworkX; figur konektivitas serta volume/delay relasi sudah dibuat | Mahasiswa merumuskan insight sendiri; klaim transit/hub fisik tidak didukung data |
| Laporan Bab 1–6, ≤40 halaman | Salinan Word Assignment II lokal sudah memuat Bab 1–6, daftar isi/gambar/tabel diperbarui, formulir AI diperbarui sesuai angka/uraian yang ditentukan mahasiswa, dan ekspor Word terukur 31 halaman | Mahasiswa meninjau substansi Bab 5–6 dan deklarasi AI, lalu menandatangani formulir baru; tambahkan tautan source code setelah hasil diterbitkan serta cek akses tautan dataset sebelum pengumpulan |
| Tautan data/kode; slide; video | Repositori GitHub, PPT dan video Assignment I | Sediakan tautan dataset yang dapat diakses dosen, pastikan kode Assignment II dieksekusi/tersimpan, lalu buat slide dan video baru sesuai hasil Assignment II |

## Urutan pelaksanaan

1. **Keputusan mahasiswa sudah dicatat.** Kasus, fitur, dua pembanding non-Spark, kedua split, dan dua pertanyaan graf dipilih langsung oleh mahasiswa. Alasan lengkap dan interpretasi hasil tetap perlu ditulis dalam kata-kata mereka sendiri.
2. **Eksperimen teknis telah dijalankan.** Baca `docs/assignment2-technical-results.md` dan output JSON/CSV sumbernya. Pertahankan hasil Assignment I sebagai baseline dan jangan menyatukan angka model lama dengan hasil pelatihan ulang.
3. **Mahasiswa menulis analisisnya.** Mahasiswa membandingkan hasil model, menjelaskan keterbatasan, menafsirkan graph, dan menyusun kesimpulan. Setelah itu AI boleh membantu tata bahasa, konsistensi angka, tabel, dan tata letak tanpa mengubah substansi argumentasi.
4. **Bangun paket penyerahan.** Bab 4.3–6 sudah ditambahkan pada salinan Word 31 halaman untuk ditinjau mahasiswa. Setelah tinjauan dan deklarasi AI, terbitkan kode/hasil, tambahkan tautan yang dapat diakses, lalu perbarui PPT dan video ≤10 menit dan cocokkan angka pada seluruh artefak.

## Bahan pertimbangan untuk keputusan mahasiswa

Ini contoh opsi untuk dipelajari, bukan keputusan atau rekomendasi proyek. Pilihan akhirnya beserta alasannya harus ditulis mahasiswa sendiri sesuai panduan.

| Keputusan | Contoh opsi | Konsekuensi yang perlu diperiksa |
| --- | --- | --- |
| Kasus analitik | Tetap memprediksi keterlambatan pengiriman; atau memilih masalah lain yang labelnya dapat dibuat dari tabel Olist | Kasus lama memiliki baseline dan laporan yang sudah tersedia. Kasus baru memerlukan definisi target, pemeriksaan waktu tersedianya fitur, dan pembaruan narasi Bab 1–4 |
| Pembanding tanpa Spark MLlib | Implementasi algoritma serupa memakai pustaka Python non-Spark; atau baseline algoritma berbeda | Algoritma serupa membantu membandingkan implementasi; algoritma berbeda sekaligus mengubah metode, sehingga perbedaan hasil tidak dapat diatribusikan hanya pada framework. Keduanya perlu populasi/split/metrik yang sebanding |
| Pertanyaan graph | Konsentrasi volume/risiko pada hubungan state asal–tujuan; atau hubungan seller–customer/product yang dapat dibangun dari tabel asli | Pilihan pertama dapat memakai graf yang sudah ada. Pilihan kedua memerlukan definisi node/edge baru. Keduanya memerlukan batas klaim yang sesuai dengan data teramati |

Catatan keputusan mahasiswa telah disampaikan dalam percakapan. Untuk laporan, mahasiswa masih perlu menuliskan alasan pilihan dan interpretasi hasil dengan kata-kata sendiri; lihat `docs/assignment2-technical-results.md` untuk angka yang dapat diperiksa.

## Telaah blueprint tambahan (2026-10-15)

Blueprint NotebookLM sudah berevolusi menjadi `docs/bda-assignment2-codex-directive.md`. Ini adalah usulan pendampingan, **bukan** hasil pengukuran, otorisasi langsung dari mahasiswa, maupun pengganti panduan resmi. Bagian yang sejalan dengan panduan resmi: melanjutkan Bab 4.3–6, implementasi dengan dan tanpa Spark MLlib, evaluasi, graph analytics, visualisasi, serta batas 40 halaman. Namun keputusan fitur, algoritma, strategi model dan interpretasi tetap harus dijustifikasi mahasiswa.

Klaim berikut perlu dikoreksi sebelum dapat dipakai dalam kode, laporan, atau presentasi:

- Output saat ini memuat **96.470** order berlabel, tetapi hanya **96.455** order memenuhi semua prediktor model. Metadata model mencatat **10** fitur, bukan 18.
- F1 test model yang tersimpan adalah **0,2194**, bukan sekitar 0,84. Waktu training 4,2 vs 1,1 detik belum diukur; jangan ditampilkan sebagai hasil benchmark. Spark saat ini berjalan pada `local[4]`, bukan cluster multi-node yang sudah diuji.
- Fitur penting teratas yang tersimpan adalah `estimated_delivery_days` (0,3384), bukan `distance_est_days`; `freight_ratio` bukan peringkat kedua. Feature importance menunjukkan asosiasi pada model, bukan bukti penyebab keterlambatan.
- PageRank SP yang tersimpan **0,2997**, bukan sekitar 0,38. Betweenness tertinggi justru MG (0,0506), lalu SP (0,0438). Graf asal–tujuan tidak mengamati jalur transit atau hub fisik, sehingga klaim kemacetan jaringan dan rekomendasi fulfillment center memerlukan bukti tambahan.
- Angka 15% tidak dipindahkan otomatis dari dokumen lama. Dalam instruksi 16 Oktober 2026, mahasiswa secara eksplisit menetapkan estimasi 15% untuk formulir Assignment II; mahasiswa tetap perlu meninjau kebenaran uraian kontribusi dan menandatangani formulir baru.

Jika mahasiswa mengadopsi suatu pilihan dari blueprint, tulis terlebih dahulu alasan dan batasannya dengan pemahaman sendiri. Kode dan narasi hasil hanya boleh menggunakan angka yang benar-benar dihasilkan oleh eksperimen yang sudah dijalankan.

Directive terbaru sudah mengoreksi urutan *feature importance*, tetapi masih salah pada confusion matrix, split 80/20 yang mengabaikan validation, dan kriteria volume rute `>500`. Telaah ringkas ada di `docs/assignment2-feedback-directive-for-notebooklm.md`.

## Batas hasil Assignment I yang perlu dijelaskan jujur

- Baseline terukur: 96.470 pesanan delivered berlabel valid, 7.826 terlambat (8,11%). Model PySpark MLlib saat ini: ROC-AUC 0,6610; PR-AUC 0,1409; precision 14,47%; recall 45,41%; F1 0,2194 pada test dan ambang terpilih 0,099536.
- Pemisahan data saat ini berbasis hash order ID, belum membuktikan generalisasi ke periode masa depan. Skor model belum terkalibrasi. Ini adalah keterbatasan yang sudah tercatat, bukan instruksi untuk memilih strategi pengembangan tertentu.
- Graf NetworkX memodelkan asal–tujuan state yang teramati, bukan transit paket, lokasi hub fisik, atau graph database terdistribusi.

## Pemeriksaan akhir

- Panduan menulis subbagian Bab 2 sebagai `4.1–4.3`; gunakan penomoran Bab 2 yang konsisten (`2.1–2.3`) pada laporan.
- Jalankan kode dari lingkungan lokal yang terdokumentasi dan simpan output tanpa error.
- Cocokkan metrik antara output, laporan, dan PPT; mahasiswa memverifikasi interpretasinya.
- Pastikan jumlah halaman PDF final dan durasi video memenuhi panduan.
- Jangan sertakan data pribadi/secrets, runtime, cache, atau output besar yang tidak perlu di Git.
