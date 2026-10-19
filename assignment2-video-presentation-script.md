# Naskah video Assignment II — Olist

Target durasi: **10 menit** untuk 12 slide. Ini draf tutur yang dapat dibaca sambil menampilkan PowerPoint; latihan sekali dengan stopwatch dan sesuaikan jeda atau tempo. Mahasiswa perlu memeriksa kembali alasan, interpretasi, dan kesimpulan sebagai pendapat akademiknya sendiri sebelum merekam. Tanda tangan deklarasi AI pada laporan masih harus diisi oleh mahasiswa.

## 00:00–00:25 — Slide 1: pembukaan

“Halo, saya Yanlis Alim Sang Putra Lase. Di Assignment II Big Data Analytics ini, saya melanjutkan proyek Olist dari tugas sebelumnya. Fokus saya adalah membaca risiko keterlambatan pesanan dengan machine learning, lalu melihat pola asal dan tujuan pengiriman pada tingkat state melalui graph analytics. Saya akan tunjukkan apa yang benar-benar terukur, dan batas dari hasil tersebut.”

## 00:25–01:30 — Slide 2: masalah bisnis

“Masalahnya sederhana: ketika pesanan sampai melewati estimasi, pengalaman pelanggan bisa memburuk. Dari 96.470 pesanan delivered yang memiliki label valid, 7.826 tercatat terlambat. Itu sekitar 8,11 persen. Pada order yang memiliki ulasan, rata-rata review untuk yang tepat waktu sekitar 4,29, sedangkan yang terlambat sekitar 2,57. Perbedaannya cukup besar untuk menjadi perhatian operasional, tetapi saya tidak menganggap angka ini sebagai bukti bahwa keterlambatan adalah satu-satunya penyebab skor ulasan turun. Ada faktor lain yang mungkin berperan. Pertanyaan utama saya: apakah informasi yang tersedia dari order bisa memberi sinyal risiko lebih awal, supaya tim logistik punya dasar untuk menentukan pesanan mana yang perlu diperiksa? Saya juga ingin tahu apakah ada hubungan antar-state yang volumenya besar sekaligus sering terlambat.”

## 01:30–02:30 — Slide 3: pipeline data

“Data berawal dari sembilan tabel CSV Olist. Pada tahap sebelumnya, tabel dibaca dan dicek menggunakan PySpark, lalu disimpan dalam format Parquet dengan kompresi Snappy. Untuk analisis ini saya mulai dari 96.478 pesanan berstatus delivered. Delapan order tidak punya tanggal yang lengkap untuk menentukan terlambat atau tidak, sehingga tersisa 96.470 order berlabel. Setelah fitur model diperiksa, lima belas order lain memiliki nilai prediktor kosong atau tidak valid. Jadi populasi yang masuk pemodelan adalah 96.455 order. Angka-angka itu penting karena denominator untuk analisis bisnis, model, dan graf tidak selalu sama. Semua percobaan Spark di sini berjalan di satu komputer dengan empat thread. Struktur pengolahannya relevan untuk Spark, tetapi hasil lokal ini belum membuktikan performa cluster atau kesiapan produksi.”

## 02:30–03:30 — Slide 4: sepuluh fitur

“Saya mempertahankan sepuluh fitur agar hasilnya bisa dibandingkan dengan baseline Assignment I. Ada informasi nilai dan isi pesanan, seperti jumlah item, total harga, ongkos kirim, rasio ongkos kirim, dan cicilan maksimum. Ada juga estimasi lama pengiriman, apakah seller dan customer berada di state yang sama, hari serta jam pembelian, dan berat produk. Fitur-fitur itu digabung pada tingkat order, jadi satu order menjadi satu baris model. Saya menghindari penggunaan tanggal barang benar-benar diterima sebagai prediktor, karena tanggal itu baru diketahui setelah kejadian yang ingin diprediksi. Beberapa fitur bisa berkorelasi dengan keterlambatan, tetapi korelasi atau feature importance tidak otomatis berarti hubungan sebab-akibat.”

## 03:30–04:20 — Slide 5: strategi model

“Saya memakai Random Forest di PySpark MLlib, lalu membandingkannya dengan Random Forest dan Logistic Regression dari scikit-learn. Random Forest non-Spark membantu saya melihat hasil dari keluarga algoritma yang sama di implementasi berbeda. Logistic Regression memberi pembanding yang lebih sederhana, jadi perbedaan dengannya tidak boleh disebut murni efek framework. Dua cara membagi data digunakan: hash berdasarkan keanggotaan order yang tersimpan dari Assignment I, dan urutan waktu pembelian. Untuk split waktu, sekitar 64 persen dipakai untuk train, 16 persen validation, dan 20 persen test. Ambang skor model dipilih dari validation menggunakan F1 maksimum; test baru dipakai setelah pilihan itu terkunci.”

## 04:20–05:30 — Slide 6: hasil evaluasi

“Tabel ini adalah hasil test enam kombinasi model dan split. Pada split hash, F1 ketiganya berdekatan, sekitar 0,22. Spark Random Forest dari pelatihan ulang ini mencapai 0,2224. Itu bukan salinan identik model Assignment I, yang F1-nya 0,2194. Pada split kronologis, hasil berubah cukup banyak: Logistic Regression 0,1139, Spark Random Forest 0,0867, dan scikit-learn Random Forest 0,1785. Model terakhir memberi F1 paling tinggi di antara tiga kandidat pada test waktu, dengan precision 10,35 persen dan recall 64,64 persen. Saya sengaja menampilkan precision dan recall bersama F1, karena F1 saja bisa menyembunyikan banyak false positive. Prevalensi keterlambatan pada test waktu 5,29 persen, lebih rendah daripada test hash 8,16 persen. Perubahan komposisi data ini perlu diperhatikan saat membaca precision. Saya belum punya bukti bahwa penurunan performa disebabkan concept drift tertentu; itu masih pertanyaan untuk analisis lanjutan.”

## 05:30–06:00 — Slide 7: ambang dan kapasitas

“Karena saya lebih memprioritaskan agar pesanan tepat waktu tidak terlalu banyak salah ditandai, saya juga melihat skenario jumlah alert. Contohnya untuk scikit-learn Random Forest pada split waktu, ambang dari budget satu persen di validation menghasilkan 487 alert pada test: 88 benar terlambat, 399 false positive. Precision-nya 18,07 persen, tetapi recall hanya 8,62 persen. Budget lima dan sepuluh persen menangkap lebih banyak keterlambatan, dengan jauh lebih banyak alert. Ini simulasi sensitivitas, belum keputusan ambang final. Saya perlu mengetahui kapasitas pemeriksaan nyata sebelum memilihnya.”

## 06:00–07:00 — Slide 8: definisi graf

“Bagian kedua memakai graf berarah NetworkX. Setiap node adalah state di Brasil, dan edge menghubungkan state seller ke state customer yang muncul pada order. Ada 27 node dan 409 relasi asal–tujuan dari 96.470 order berlabel. Volume order menjadi salah satu bobot edge. Gambar ini hanya memperlihatkan 35 edge dengan volume tertinggi agar pola umumnya terbaca; analisis metrik tetap memakai graf lengkap. Posisi node pada gambar adalah tata letak visual, bukan koordinat geografis. Data ini tidak merekam gudang, transit paket, perjalanan kendaraan, atau kemacetan jalan. Karena itu saya membaca graf sebagai jaringan hubungan transaksi antar-state, bukan peta jalur fisik pengiriman.”

## 07:00–08:00 — Slide 9: temuan graf

“Salah satu relasi yang menonjol adalah SP ke RJ. Ada 8.158 order, dengan 1.264 terlambat, sehingga delay rate sekitar 15,49 persen. Kombinasi volume tinggi dan delay yang cukup besar membuat relasi ini layak diperiksa lebih dulu. SP ke MA dan SP ke AL memiliki delay rate lebih tinggi, tetapi masing-masing hanya 491 dan 255 order. Jadi saya tidak akan mengurutkan prioritas hanya dari persentase; jumlah kasus juga perlu terlihat. Pada graf ini, PageRank tertinggi ada di SP, sekitar 0,2997. Betweenness topologis tertinggi ada di MG, sekitar 0,0506. Metrik tersebut menggambarkan struktur graf transaksi yang dibangun. Saya tidak menyimpulkan SP atau MG adalah hub transit fisik dari angka centrality ini.”

## 08:00–09:00 — Slide 10: usulan operasional

“Dari dua analisis ini, usulan saya bersifat uji coba. Pertama, mulai dengan daftar order berisiko yang kecil dan ditinjau manusia. Tim perlu mencatat berapa banyak alert yang berguna dan berapa biaya untuk memeriksa yang ternyata tepat waktu. Kedua, lihat relasi asal–tujuan seperti SP ke RJ bersama volume, jumlah terlambat, dan delay rate, lalu bandingkan dengan relasi lain. Kalau ditemukan masalah berulang, penyebabnya harus ditelusuri dengan data operasional tambahan. Ketiga, evaluasi model pada periode baru dan pantau precision, recall, prevalensi, serta kalibrasi skor. Saya tidak menyarankan tindakan otomatis ataupun perubahan lokasi hub sekarang, karena eksperimen ini belum mengukur dampak intervensi atau memetakan perjalanan fisik paket.”

## 09:00–09:30 — Slide 11: tata kelola dan AI

“Ada dua batas tata kelola yang perlu saya sampaikan. Dataset mentah dan prediksi per-order tetap disimpan lokal; yang saya bagikan ke repositori adalah kode serta hasil agregat kecil. Lalu, formulir AI pada laporan menyatakan Type 2 atau Partial Use dengan estimasi kontribusi 15 persen yang saya tetapkan. Bantuan yang dicatat mencakup sintaks dan debugging, visualisasi, draf atau penyuntingan teks, serta format Word. Sebelum pengumpulan, saya akan memeriksa lagi interpretasi akhir dan menandatangani formulir tersebut.”

## 09:30–10:00 — Slide 12: penutup

“Kesimpulan sementara saya: model bisa memberi sinyal, tetapi hasil test waktu, terutama precision-nya, belum cukup untuk keputusan otomatis. Graf OD membantu menunjukkan hubungan transaksi yang patut ditinjau, bukan lokasi hambatan fisik. Langkah berikutnya adalah menentukan kapasitas pemeriksaan yang realistis, memvalidasi hasil pada periode baru, dan baru kemudian menguji apakah intervensi benar-benar membantu. Terima kasih, saya siap menerima pertanyaan.”

## Pemeriksaan sebelum rekaman

- Buka PPT dalam mode Slide Show dan gunakan naskah ini pada layar kedua atau Presenter View. Tidak perlu berpindah ke VS Code.
- Latih sekali dengan stopwatch. Percepat atau potong kalimat pada slide 5–6 bila total melebihi 10 menit; jangan menghapus batas penting tentang prevalensi, false positive, dan arti graf OD.
- Pastikan slide dan laporan memakai angka yang sama. Jangan tampilkan tanda tangan atau menyatakan laporan sudah disetujui bila belum ditandatangani dan diperiksa.
