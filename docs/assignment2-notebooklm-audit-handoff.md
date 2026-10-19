# Tanggapan untuk NotebookLM — audit laporan Assignment II

Tanggal: 19 Oktober 2026
Proyek: Big Data Analytics / Olist / Assignment II

Saya telah memperbarui laporan Word Assignment II hingga Bab 6 dan memperbarui formulir **BINUS AI Use Declaration** pada halaman terakhir. Mohon audit naskah terbaru ini terhadap **panduan resmi Assignment II** dan berkas hasil eksperimen yang dilampirkan. Ini adalah permintaan audit, bukan pernyataan bahwa laporan sudah final atau siap dikumpulkan.

## Perubahan yang sudah diterapkan

1. Laporan memuat eksperimen prediksi keterlambatan Olist dengan 10 fitur, tiga model (PySpark MLlib Random Forest, scikit-learn Random Forest, dan Logistic Regression), dua skema pemisahan (hash dan kronologis), evaluasi validation/test, serta analisis graf asal–tujuan state. Salinan Word dan PDF hasil ekspor Microsoft Word terukur **31 halaman**, di bawah batas 40 halaman panduan.
2. Bab 5 memuat enam kombinasi model–split dan skenario ilustratif anggaran pemeriksaan 1%, 5%, dan 10% pada validation. Belum ada ambang operasional final karena kapasitas pemeriksaan dan batas precision yang dapat diterima belum ditetapkan mahasiswa.
3. Bab 6 membahas graf berarah **27 state / 409 relasi OD** dari **96.470 order berlabel**. Edge adalah state penjual ke state pelanggan; data tidak merekam transit fisik atau lokasi hub. Gambar topologi hanya menampilkan 35 edge bervolume terbesar agar terbaca.
4. Formulir AI pada halaman terakhir kini berjudul tepat **“Assignment II - Pengolahan Big Data Menggunakan Machine Learning dan Graph Analytics”**, bertanggal **16 Oktober 2026**, berkategori **Type 2 / Partial Use**, dan mencantumkan estimasi kontribusi AI **15%** sesuai pernyataan mahasiswa. Tabel menyebut bantuan pada sintaks/debugging PySpark MLlib dan NetworkX, skrip visualisasi 300 DPI, draf/penyuntingan teks, serta format Word. Tanda tangan lama dihapus agar mahasiswa dapat menandatangani deklarasi yang baru setelah meninjau isinya.

## Angka pembanding yang harus digunakan saat audit

Gunakan `outputs_assignment2/model_comparison.csv`, `outputs_assignment2/split_profile.csv`, dan `outputs_assignment2/alert_budget_scenarios.csv` sebagai sumber angka yang diunggah. Enam JSON metrik disimpan lokal untuk verifikasi lanjutan oleh penulis laporan. Ringkasan berikut hanya penunjuk pemeriksaan:

| Split | Model | F1 test | Precision test | Recall test |
| --- | --- | ---: | ---: | ---: |
| Hash | scikit-learn Logistic Regression | 0,2202 | 14,90% | 42,21% |
| Hash | scikit-learn Random Forest | 0,2201 | 15,32% | 39,06% |
| Hash | Spark Random Forest, run baru | 0,2224 | 14,77% | 45,03% |
| Kronologis | scikit-learn Logistic Regression | 0,1139 | 6,82% | 34,57% |
| Kronologis | scikit-learn Random Forest | 0,1785 | 10,35% | 64,64% |
| Kronologis | Spark Random Forest, run baru | 0,0867 | 5,17% | 26,93% |

Prevalensi delay test berbeda: hash **8,16%** dan kronologis **5,29%**. Model Spark RF pada split hash adalah pelatihan ulang Assignment II, bukan reproduksi identik baseline Assignment I (F1 test **0,2194**). Jangan menyatakan bahwa perbedaan hasil disebabkan satu faktor tertentu tanpa bukti. Durasi `model.fit` satu kali pada mesin lokal bukan benchmark komparatif atau bukti skalabilitas cluster.

Graf OD: relasi SP→RJ berisi **8.158 order**, **1.264 terlambat**, delay rate **15,49%**. PageRank tiga state teratas adalah SP **0,2997**, RJ **0,1182**, MG **0,1059**; betweenness topologis teratas MG **0,0506**, SP **0,0438**, PR **0,0412**. Nilai ini bersifat deskriptif untuk graf state asal–tujuan, bukan bukti bottleneck fisik.

## Yang perlu NotebookLM periksa

1. Cocokkan semua tabel, angka, caption, rujukan figur, daftar isi/gambar/tabel, dan kesimpulan laporan dengan panduan serta CSV/JSON sumber. Berikan lokasi halaman/subbab untuk setiap temuan.
2. Periksa apakah Bab 5 memenuhi kebutuhan pengembangan dan evaluasi model **dengan dan tanpa Spark MLlib**, serta Bab 6 memenuhi kebutuhan graph analytics dan insight, tanpa klaim kausal atau kesiapan produksi yang berlebihan.
3. Periksa apakah penjelasan perbedaan hash versus kronologis, trade-off precision/recall, skenario anggaran peringatan, dan batas graf OD akurat. Bedakan **fakta terukur**, **interpretasi**, dan **usulan lanjutan**.
4. Periksa konsistensi deklarasi AI dengan bantuan yang diungkapkan. **Angka 15% adalah estimasi yang ditetapkan mahasiswa, bukan hasil pengukuran otomatis.** Mohon tandai kalimat yang menyatakan analisis atau seluruh narasi Bab 5–6 ditulis 100% tanpa AI bila masih ada; bantuan draf/penyuntingan teks memang terjadi. Penilaian dan keputusan akademik akhir harus ditinjau dan dimiliki mahasiswa.
5. Identifikasi kekurangan yang menghalangi penyerahan: tanda tangan deklarasi baru, alasan/interpretasi pribadi mahasiswa, akses tautan dataset dan kode yang sudah dieksekusi, serta kelengkapan lain menurut panduan. Slide dan video belum disiapkan karena audit laporan didahulukan.

Mohon keluarkan temuan dalam tabel: **prioritas**, **halaman/subbab**, **kutipan/klaim yang dipersoalkan**, **bukti pembanding yang dilampirkan**, dan **saran revisi spesifik**. Jangan mengisi kekosongan dengan angka rekaan atau memperlakukan arahan NotebookLM terdahulu sebagai hasil eksperimen.

## Lampiran audit yang disarankan

**Wajib:**

1. `Big Data Analytics - Laporan Assignment II 2702751284.docx` **dan** PDF hasil ekspor terbarunya (`.report_review/assignment2_report.pdf`). PDF memudahkan pemeriksaan halaman; Word memudahkan pemeriksaan isi tabel/formulir. Keduanya adalah versi yang sama.
2. `Big Data Analytics - Assignment II (Guide) .pdf` — instruksi dan rubrik resmi.
3. `docs/assignment2-technical-results.md` — peta hasil dan batas interpretasi.
4. `outputs_assignment2/model_comparison.csv`, `outputs_assignment2/split_profile.csv`, dan `outputs_assignment2/alert_budget_scenarios.csv` — angka agregat sumber.
5. File tanggapan ini, `docs/assignment2-notebooklm-audit-handoff.md`, sebagai ruang lingkup dan daftar klaim untuk diuji.

**Opsional:** figur 5–10 sebagai PNG terpisah jika gambar tertanam di laporan tidak terbaca. Enam JSON metrik, skrip Python, dan notebook tetap tersedia lokal untuk pemeriksaan kode terpisah; daftar format unggah NotebookLM resmi mencakup DOCX, PDF, Markdown, dan CSV, tetapi tidak mencantumkan JSON, `.py`, atau `.ipynb` sebagai sumber langsung. Jika audit kode diperlukan, konversi skrip relevan ke `.txt` atau gunakan tautan repositori setelah kode diterbitkan.

Jangan unggah dataset mentah, lingkungan `.venv`, runtime Java, Parquet prediksi per-order, cache, atau arahan/audit NotebookLM lama sebagai pengganti bukti sumber. Jangan sertakan formulir bertanda tangan sebelum mahasiswa meninjaunya.
