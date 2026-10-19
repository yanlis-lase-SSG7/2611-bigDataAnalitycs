"""Extend the existing Assignment I Word report with measured Assignment II evidence.

The source manuscript is preserved. The Assignment II declaration uses the
student-specified title, date, and contribution estimate; the student must
review and sign the generated form.
"""

from __future__ import annotations

import json
import itertools
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Big Data Analytics - Laporan 2702751284.docx"
TARGET = ROOT / "Big Data Analytics - Laporan Assignment II 2702751284.docx"
OUT = ROOT / "outputs_assignment2"
FIG = ROOT / "figures"
BOOKMARK_IDS = itertools.count(9000)


def para(doc, anchor, text, style="Normal"):
    p = doc.add_paragraph(text, style=style)
    anchor.addprevious(p._p)
    return p


def table(doc, anchor, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, head in enumerate(headers):
        t.rows[0].cells[i].text = str(head)
    for values in rows:
        cells = t.add_row().cells
        for i, value in enumerate(values):
            cells[i].text = str(value)
    if widths:
        for row in t.rows:
            for cell, width in zip(row.cells, widths):
                cell.width = Cm(width)
    for row in t.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    run.font.size = Pt(8)
    for cell in t.rows[0].cells:
        for p in cell.paragraphs:
            for run in p.runs:
                run.bold = True
    anchor.addprevious(t._tbl)
    return t


def caption(doc, anchor, value):
    p = para(doc, anchor, value, "Caption")
    p.paragraph_format.keep_with_next = True
    # The retained manuscript's lists of figures/tables use hidden TC fields.
    kind = "G" if value.startswith("Gambar ") else "T"
    bookmark_id = next(BOOKMARK_IDS)
    for field_type, field_text in (("begin", None), (None, 'TC "')):
        run = OxmlElement("w:r")
        properties = OxmlElement("w:rPr")
        hidden = OxmlElement("w:vanish")
        properties.append(hidden)
        run.append(properties)
        item = OxmlElement("w:fldChar" if field_type else "w:instrText")
        if field_type:
            item.set(qn("w:fldCharType"), field_type)
        else:
            item.text = field_text
        run.append(item)
        p._p.append(run)
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), f"_TocAssignment2{bookmark_id}")
    p._p.append(start)
    for field_text in (value, f'" \\f {kind}'):
        run = OxmlElement("w:r")
        item = OxmlElement("w:instrText")
        item.text = field_text
        run.append(item)
        p._p.append(run)
        if field_text == value:
            end = OxmlElement("w:bookmarkEnd")
            end.set(qn("w:id"), str(bookmark_id))
            p._p.append(end)
    run = OxmlElement("w:r")
    item = OxmlElement("w:fldChar")
    item.set(qn("w:fldCharType"), "end")
    run.append(item)
    p._p.append(run)
    return p


def picture(doc, anchor, path, width=15.5):
    p = para(doc, anchor, "")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Cm(width))
    return p


def update_ai_declaration(doc):
    """Apply the student's stated Assignment II form details to the copied form."""
    header, activity = doc.tables[-2:]
    if header.cell(4, 0).text != "Assignment Title" or activity.cell(0, 0).text != "ASSIGNMENT PART":
        raise ValueError("Expected BINUS AI declaration form was not found at the document end")
    header.cell(4, 1).text = (
        ": Assignment II - Pengolahan Big Data Menggunakan Machine Learning dan Graph Analytics"
    )
    header.cell(5, 1).text = "Type 2 / Partial Use"

    updates = {
        1: (
            "Yes", "OpenAI Codex; Gemini Notebook",
            "AI membahas opsi kasus, model, split, dan graf. Mahasiswa memilih kasus Olist "
            "dan prioritas precision; kesimpulan akhir ditinjau mahasiswa."
        ),
        2: (
            "Yes", "OpenAI Codex",
            "Bantuan sintaks PySpark MLlib, scikit-learn, debugging NetworkX, pengujian "
            "dan draf Bab 5–6. Mahasiswa meninjau interpretasi akhir sebelum pengumpulan."
        ),
        3: (
            "Yes", "OpenAI Codex; Matplotlib/Seaborn",
            "Skrip visualisasi fig1–fig10 sekitar 300 DPI, termasuk evaluasi ML dan graf OD."
        ),
        4: (
            "Yes", "Gemini Notebook; OpenAI Codex",
            "Pemeriksaan bahasa dan konsistensi istilah laporan."
        ),
        5: (
            "Yes", "OpenAI Codex; python-docx; Microsoft Word",
            "Format tabel hasil ML, caption, daftar isi/gambar/tabel, dan tata letak Word."
        ),
    }
    for index, (used, tool, description) in updates.items():
        activity.cell(index, 1).text = used
        activity.cell(index, 2).text = tool
        activity.cell(index, 3).text = description
    activity.cell(6, 0).text = "Approximate contribution of AI in the final submission of assignment is 15%"
    for row in activity.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.0
                for run in paragraph.runs:
                    run.font.size = Pt(9)

    dates = [p for p in doc.paragraphs if p.text.strip().startswith("Jakarta, ")]
    if len(dates) != 1:
        raise ValueError("Expected one declaration date in the BINUS form")
    dates[0].text = "Jakarta, 16 Oktober 2026"

    # The source form contains a floating signature from Assignment I. A new
    # declaration date needs the student's new signature, so leave its line blank.
    form_heading = next(i for i, p in enumerate(doc.paragraphs)
                        if "ARTIFICIAL INTELLIGENCE USE DECLARATION FORM" in p.text)
    for paragraph in doc.paragraphs[form_heading + 1:]:
        for run in list(paragraph._p.xpath("./w:r")):
            if run.xpath(".//w:drawing"):
                paragraph._p.remove(run)


def main():
    doc = Document(SOURCE)
    anchor = next(p._p for p in doc.paragraphs if p.text.strip() == "DAFTAR PUSTAKA")
    metrics = pd.read_csv(OUT / "model_comparison.csv")
    splits = pd.read_csv(OUT / "split_profile.csv")
    scenarios = pd.read_csv(OUT / "alert_budget_scenarios.csv")
    graph = json.loads((ROOT / "outputs_ml_graph" / "graph_preparation_audit.json").read_text(encoding="utf-8"))
    expected_pairs = {(split, model) for split in ("hash", "temporal") for model in (
        "spark_random_forest", "sklearn_random_forest", "sklearn_logistic_regression")}
    actual_pairs = set(zip(metrics["split"], metrics["model"]))
    if len(metrics) != 6 or actual_pairs != expected_pairs:
        raise ValueError("Model comparison must contain exactly the six expected split/model pairs")
    validation_f1 = {}
    for split, model in expected_pairs:
        result = json.loads((OUT / f"{split}_{model}_metrics.json").read_text(encoding="utf-8"))
        if abs(result["f1"] - float(metrics.loc[
                (metrics.split == split) & (metrics.model == model), "f1"].iloc[0])) > 1e-12:
            raise ValueError(f"JSON/CSV test F1 mismatch for {split}/{model}")
        validation_f1[(split, model)] = result["validation_selection"]["f1"]

    doc.paragraphs[0].text = "ASSIGNMENT II"
    doc.paragraphs[3].text = (
        "PENGEMBANGAN MODEL MACHINE LEARNING DAN ANALISIS GRAF UNTUK RISIKO "
        "KETERLAMBATAN PENGIRIMAN PADA OLIST STORE BRAZIL"
    )

    chapter5 = para(doc, anchor, "BAB 5\nPENGEMBANGAN DAN EVALUASI MODEL MACHINE LEARNING", "Heading 1")
    chapter5.paragraph_format.page_break_before = True
    para(doc, anchor, "5.1 Data Preprocessing", "Heading 2")
    para(doc, anchor,
         "Tahap Assignment II melanjutkan masalah yang sama dari Assignment I: memperkirakan risiko "
         "pesanan diterima melewati waktu estimasi yang tercatat. Label is_delayed bernilai satu bila "
         "waktu penerimaan aktual lebih lambat daripada estimasi. Dari 99.441 order sumber, 96.470 "
         "order delivered memiliki tanggal pembentuk label yang lengkap. Sebanyak 15 order lain "
         "tidak mempunyai seluruh prediktor, sehingga populasi pemodelan berjumlah 96.455 order. "
         "Label aktual hanya tersedia setelah pengiriman selesai; prediksi dimaksudkan sebagai "
         "sinyal risiko setelah informasi order dan estimasi pengiriman tercatat, bukan kepastian "
         "bahwa sebuah pengiriman akan terlambat.")
    para(doc, anchor, "5.2 Feature Engineering", "Heading 2")
    para(doc, anchor,
         "Sepuluh prediktor yang dipertahankan dari notebook 02 ialah total_items, total_price, "
         "total_freight, freight_ratio, max_installments, estimated_delivery_days, is_same_state, "
         "purchase_dayofweek, purchase_hour, dan product_weight_g. Agregasi item dan pembayaran "
         "dilakukan sebelum join ke grain satu order. Primary seller ditentukan dari item dengan "
         "order_item_id terkecil; penyederhanaan ini mengabaikan kontribusi penjual lain pada order "
         "multi-seller. Nilai product_weight_g yang hilang mengikuti aturan imputasi konstanta "
         "500 gram dari Assignment I. Seluruh sepuluh nilai harus lengkap dan finite untuk masuk model.")

    para(doc, anchor, "5.2.1 Pemisahan data untuk evaluasi", "Heading 3")
    para(doc, anchor,
         "Dua skema evaluasi dipakai. Skema hash mempertahankan keanggotaan train, validation, dan "
         "test dari Assignment I, sehingga perbandingan terhadap baseline lama menggunakan order uji "
         "yang sama. Skema temporal mengurutkan waktu pembelian, dengan order_id sebagai pemutus "
         "urutan saat timestamp sama, lalu membagi sekitar 64% train, 16% validation, dan 20% test. "
         "Seluruh model dalam satu skema memakai populasi dan label yang sama. Skema temporal menguji "
         "periode pembelian berikutnya, tetapi bukan validasi produksi pada data Olist masa kini.")
    caption(doc, anchor, "Tabel 5.1 Profil populasi dan prevalensi keterlambatan setiap split")
    table(doc, anchor,
          ["Skema", "Bagian", "Order", "Terlambat", "Prevalensi"],
          [[r.scheme, r.split, f"{r.orders:,}", f"{r.delayed_orders:,}",
            f"{r.delay_prevalence * 100:.2f}%"] for r in splits.itertuples(index=False)],
          [2.5, 3.5, 3, 3, 3])
    para(doc, anchor,
         "Prevalensi pada test hash adalah 8,16%, sedangkan test temporal 5,29%. Karena komposisi "
         "dan periode test berbeda, angka antar-skema tidak ditafsirkan sebagai pengaruh tunggal "
         "pergantian algoritma. Perbandingan tiga model paling langsung dilakukan di dalam skema "
         "split yang sama.")

    para(doc, anchor, "5.3 Algoritma Machine Learning", "Heading 2")
    para(doc, anchor,
         "Model dengan Spark MLlib adalah Random Forest Classifier 100 pohon, kedalaman maksimum "
         "delapan, seed 42, dan bobot kelas satu untuk kedua kelas. Dua pembanding tanpa MLlib ialah "
         "Random Forest scikit-learn dengan 100 pohon dan kedalaman maksimum delapan, serta "
         "Logistic Regression sebagai model linier pembanding. Logistic Regression memakai "
         "StandardScaler yang di-fit hanya pada train. Implementasi Spark dijalankan dengan local[4] "
         "pada satu komputer; hasil ini tidak membuktikan efisiensi cluster terdistribusi.")
    para(doc, anchor, "5.4 Proses Pengembangan Model dengan dan tanpa Spark MLlib", "Heading 2")
    para(doc, anchor,
         "Untuk setiap skema split, ketiga model di-fit hanya pada bagian train. Spark MLlib "
         "menyatukan sepuluh kolom melalui VectorAssembler sebelum melatih Random Forest; "
         "scikit-learn membaca matriks fitur yang sama dan melatih Random Forest serta pipeline "
         "StandardScaler–Logistic Regression. Skor validation dipakai untuk memilih ambang, "
         "kemudian skor test dievaluasi dengan ambang yang sudah terkunci. Tidak ada record "
         "test yang digunakan pada fit atau pemilihan ambang.")
    para(doc, anchor,
         "Setiap model menghasilkan skor kelas terlambat. Untuk metrik utama, ambang dipilih hanya "
         "pada validation dengan F1 maksimum; jika seri, precision lalu ambang yang lebih tinggi "
         "diprioritaskan. Test tidak digunakan untuk melatih model atau memilih ambang. Setelah "
         "mahasiswa menyatakan precision sebagai perhatian operasional utama, dibuat pula tiga "
         "skenario sensitivitas yang membatasi jumlah peringatan validation pada 1%, 5%, dan 10%. "
         "Batas ini bersifat ilustratif, sebab kapasitas pemeriksaan aktual belum diketahui. Skor "
         "model juga belum dikalibrasi sebagai probabilitas keterlambatan.")

    para(doc, anchor, "5.5 Evaluasi Model", "Heading 2")
    caption(doc, anchor, "Tabel 5.2 F1 validasi dan metrik test pada ambang terpilih")
    labels = {"spark_random_forest": "Spark RF", "sklearn_random_forest": "sklearn RF",
              "sklearn_logistic_regression": "sklearn LR"}
    table(doc, anchor,
          ["Split", "Model", "F1 validasi", "Precision", "Recall", "F1 test", "PR-AUC", "ROC-AUC"],
          [[r.split, labels[r.model], f"{validation_f1[(r.split, r.model)]:.4f}",
            f"{r.precision:.4f}", f"{r.recall:.4f}",
            f"{r.f1:.4f}", f"{r.pr_auc_trapezoid:.4f}", f"{r.roc_auc:.4f}"]
           for r in metrics.sort_values(["split", "model"]).itertuples(index=False)],
          [1.6, 2.5, 1.9, 1.9, 1.9, 1.6, 2.1, 2.1])
    para(doc, anchor,
         "PR-AUC pada Tabel 5.2 memakai luas trapezoid di bawah kurva precision–recall, sama "
         "dengan notebook 02; nilainya tidak identik dengan average precision scikit-learn. "
         "Pelatihan ulang Spark RF pada split hash menghasilkan F1 0,2224, sedangkan baseline "
         "Assignment I yang tersimpan F1 0,2194. Keduanya merupakan run berbeda, bukan hasil "
         "yang dapat saling menggantikan tanpa penanda.")
    caption(doc, anchor, "Gambar 5.1 Matriks kesalahan enam kombinasi model dan split")
    picture(doc, anchor, FIG / "fig5_ml_confusion_matrix.png", 14.8)
    caption(doc, anchor, "Gambar 5.2 Kurva ROC dan precision–recall pada data test")
    picture(doc, anchor, FIG / "fig7_pr_roc_curves.png", 13.5)

    para(doc, anchor, "5.5.1 Sensitivitas terhadap beban pemeriksaan", "Heading 3")
    para(doc, anchor,
         "False positive adalah order tepat waktu yang diperingatkan sebagai berisiko. Prediksi "
         "tersebut tidak mengubah label aktual apabila keduanya disimpan terpisah, tetapi dapat "
         "menambah pekerjaan pemeriksaan dan menurunkan kepercayaan terhadap peringatan. False "
         "negative tetap penting karena order terlambat yang terlewat tidak memperoleh tindak lanjut "
         "dini. Oleh sebab itu, precision dan recall dibaca bersama jumlah order yang ditandai.")
    selected = scenarios[(scenarios.split == "temporal") &
                         (scenarios.model == "sklearn_random_forest")].sort_values(
                             "validation_alert_budget_fraction")
    caption(doc, anchor, "Tabel 5.3 Skenario kapasitas validation untuk scikit-learn RF pada split temporal")
    table(doc, anchor,
          ["Anggaran validasi", "Peringatan test", "TP", "FP", "Precision", "Recall"],
          [[f"{r.validation_alert_budget_fraction * 100:.0f}%", f"{r.test_alerts:,}",
            f"{r.test_tp:,}", f"{r.test_fp:,}", f"{r.test_precision * 100:.2f}%",
            f"{r.test_recall * 100:.2f}%"] for r in selected.itertuples(index=False)],
          [3.1, 3.1, 2, 2, 3, 3])
    para(doc, anchor,
         "Sebagai pembanding, pada ambang F1 maksimum model yang sama menandai 6.374 order "
         "test, terdiri atas 660 terlambat dan 5.714 tepat waktu (precision 10,35%; recall 64,64%). "
         "Skenario anggaran 1% validation memberi precision test 18,07%, tetapi recall tinggal "
         "8,62%: 88 terlambat terdeteksi dan 933 terlewat. Ambang tetap yang diperoleh dari "
         "validation menghasilkan 487 peringatan pada test, bukan 1% dari jumlah order test. "
         "Perubahan distribusi skor antarperiode harus diperhatikan bila kapasitas pemeriksaan "
         "merupakan batas operasional yang keras.")

    para(doc, anchor, "5.6 Analisis", "Heading 2")
    para(doc, anchor,
         "Pada split hash, F1 tiga model berada dekat 0,22. Pada split temporal, hasilnya "
         "berbeda: Spark RF 0,0867, scikit-learn RF 0,1785, dan Logistic Regression 0,1139. "
         "Perbedaan ini menunjukkan bahwa ringkasan pada split hash saja belum cukup untuk "
         "menilai kinerja pada periode pembelian berikutnya. Penurunan prevalensi label test "
         "dari 8,16% ke 5,29% turut perlu ditampilkan, tetapi data ini belum mengisolasi sebab "
         "seluruh perubahan metrik. ROC-AUC temporal Spark RF sekitar 0,492; sumber "
         "perilaku tersebut belum dibuktikan.")
    para(doc, anchor,
         "Pada anggaran 1% validation, precision test scikit-learn RF 18,07% (399 false "
         "positive dari 487 peringatan). Karena kapasitas pemeriksaan belum diketahui, "
         "ambang produksi belum ditetapkan.")

    chapter6 = para(doc, anchor, "BAB 6\nPENGEMBANGAN DAN ANALISIS GRAF", "Heading 1")
    chapter6.paragraph_format.page_break_before = True
    para(doc, anchor, "6.1 Pengembangan Graph", "Heading 2")
    para(doc, anchor,
         "Notebook 03 membangun NetworkX DiGraph dari 96.470 order delivered berlabel. Node "
         "adalah state Brazil; sisi berarah menghubungkan state primary seller menuju state "
         "pelanggan. Agregasi menghitung volume dan jumlah order terlambat per pasangan state. "
         f"Graf terukur memuat {graph['nodes']} node dan {graph['routes']} sisi. Volume order "
         "menjadi bobot untuk out-strength, in-strength, dan PageRank; betweenness yang dilaporkan "
         "bersifat topologis tanpa bobot volume. Graf ini merupakan relasi asal–tujuan, bukan "
         "catatan perpindahan paket di titik transit atau implementasi graph database fisik.")
    caption(doc, anchor, "Gambar 6.1 Skema relasi state asal–tujuan bervolume tertinggi")
    picture(doc, anchor, FIG / "fig8_graph_network_topology.png", 15.2)
    para(doc, anchor,
         "Gambar 6.1 hanya menggambar 35 dari 409 sisi dengan volume tertinggi agar keterbacaan "
         "terjaga. Posisi node bersifat skematis, bukan koordinat lokasi atau jalur transportasi.")

    para(doc, anchor, "6.2 Analisis dan Insight yang Diperoleh", "Heading 2")
    caption(doc, anchor, "Tabel 6.1 Contoh relasi asal–tujuan dengan volume dan tingkat keterlambatan")
    table(doc, anchor, ["Relasi", "Order", "Terlambat", "Delay rate"],
          [["SP → RJ", "8.158", "1.264", "15,49%"],
           ["SP → MA", "491", "104", "21,18%"],
           ["SP → AL", "255", "67", "26,27%"]],
          [3.5, 3.5, 3.5, 3.5])
    para(doc, anchor,
         "Tingkat keterlambatan nasional untuk populasi graf adalah 7.826 dari 96.470 order "
         "(8,11%). SP → RJ menggabungkan volume 8.158 order dengan delay rate 15,49%, sehingga "
         "layak diperiksa lebih lanjut. SP → MA dan SP → AL memiliki persentase lebih tinggi, "
         "tetapi denominator masing-masing 491 dan 255 order. Persentase tanpa volume dapat "
         "memberi urutan prioritas yang menyesatkan.")
    caption(doc, anchor, "Gambar 6.2 Volume dan delay rate relasi asal–tujuan")
    picture(doc, anchor, FIG / "fig10_route_volume_delay.png", 15.2)
    caption(doc, anchor, "Gambar 6.3 PageRank dan volume order asal per state")
    picture(doc, anchor, FIG / "fig9_state_pagerank_centrality.png", 15.2)
    para(doc, anchor,
         "SP mempunyai out-strength 68.415 order dan PageRank 0,2997, sedangkan betweenness "
         "topologis tertinggi dimiliki MG (0,0506), diikuti SP (0,0438). Kedua ukuran menjawab "
         "pertanyaan berbeda: konsentrasi hubungan berbobot dan posisi dalam jalur graf abstrak. "
         "Nilai tersebut tidak menunjukkan bahwa sebuah state merupakan gudang transit fisik.")

    para(doc, anchor, "6.3 Batas inferensi dan tindak lanjut", "Heading 2")
    para(doc, anchor,
         "Graf membantu memilih relasi yang perlu diteliti bersama tim logistik, terutama ketika "
         "volume dan delay rate sama-sama tinggi. Namun data Olist tidak memuat urutan transit, "
         "rute kendaraan, kapasitas hub, atau penyebab keterlambatan. Karena itu, SP → RJ "
         "merupakan prioritas penyelidikan, bukan bukti bottleneck fisik atau dasar langsung "
         "memindahkan gudang. Pengembangan berikutnya memerlukan data operasional pengiriman "
         "dan pengujian apakah tindakan pada relasi tersebut benar-benar menurunkan keterlambatan.")
    para(doc, anchor,
         "Secara keseluruhan, prototipe ini menunjukkan alur pemrosesan data, perbandingan "
         "model, evaluasi menurut waktu, dan analisis graf yang dapat direproduksi pada satu "
         "mesin. Hasil prediksi masih terbatas terutama pada precision dan perubahan kinerja "
         "antarperiode. Sebelum digunakan dalam operasi, perlu ditentukan kapasitas pemeriksaan, "
         "pengukuran biaya false positive dan false negative, pengujian periode baru, serta "
         "kalibrasi dan pemantauan model."
         )

    # Update two stale Assignment I statements in the copied manuscript.
    for p in doc.paragraphs:
        if p.text.strip() == "Gambar 2.2 Lima feature importance terbesar pada model terpilih":
            p.text = "Gambar 2.2 Lima feature importance terbesar pada baseline Spark RF Assignment I"
        elif p.text.startswith("Feature importance menggambarkan kontribusi fitur pada model terpilih"):
            p.text = p.text.replace(
                "Feature importance menggambarkan kontribusi fitur pada model terpilih",
                "Feature importance pada baseline Spark RF Assignment I menggambarkan kontribusi relatif fitur dalam model tersebut")
        elif "Laporan Assignment I ini membahas masalah keterlambatan pengiriman" in p.text:
            p.text = p.text.replace(
                "Laporan Assignment I ini membahas masalah keterlambatan pengiriman, persiapan data, dan rancangan solusi.",
                "Bab 1–4 merangkum masalah keterlambatan pengiriman, persiapan data, dan rancangan solusi dari Assignment I; Bab 5–6 melanjutkan evaluasi model dan analisis graf untuk Assignment II.")
        elif "generalisasi ke periode berikutnya belum diuji" in p.text:
            p.text = p.text.replace(
                "skor belum dikalibrasi dan generalisasi ke periode berikutnya belum diuji.",
                "skor belum dikalibrasi. Pada tahap Assignment I, generalisasi ke periode berikutnya belum diuji; pengujian temporal Assignment II dilaporkan pada Bab 5.")
        elif "pengembangan model merupakan pekerjaan Assignment II" in p.text:
            p.text = p.text.replace(
                "pengujian temporal, kalibrasi, biaya false alarm, dan pengembangan model merupakan pekerjaan Assignment II.",
                "pengembangan model dan pengujian temporal dibahas pada Bab 5, sedangkan kalibrasi dan biaya false alarm masih memerlukan pengujian lanjut.")
        elif "belum menjadi graph database atau analisis logistik final Assignment II" in p.text:
            p.text = p.text.replace(
                "Eksplorasi ini belum menjadi graph database atau analisis logistik final Assignment II",
                "Analisis graf Assignment II dijelaskan pada Bab 6, tetapi ini belum menjadi graph database atau analisis logistik operasional")
        elif p.text.startswith("Kode lengkap yang dapat dijalankan tersedia pada tiga notebook"):
            p.text = ("Kode Assignment I tersedia pada tiga notebook dalam folder notebooks. "
                      "Eksperimen Assignment II terdapat pada assignment2_experiments.py, "
                      "pembuatan figur pada make_assignment2_figures.py, dan keluaran ringkas "
                      "pada outputs_assignment2. Output per-order tersimpan lokal dan tidak "
                      "disertakan di repositori karena ukurannya.")
        elif p.text.startswith("Buka notebook dengan interpreter"):
            p.text = ("Gunakan Python 3.11 dan lingkungan proyek sesuai README. Jalankan notebook "
                      "01 → 02 → 03 untuk menyiapkan data dan hasil Assignment I, kemudian "
                      "jalankan assignment2_experiments.py --engine all, "
                      "make_assignment2_figures.py, dan make_assignment2_results_md.py. "
                      "Java 17 dan PySpark 4.0.4 digunakan secara lokal dengan Spark local[4]. "
                      "Input besar, runtime, dan prediksi per-order tetap berada dalam folder lokal.")
        elif p.text.startswith("Data historis 2016–2018 dan volume sekitar 120 MiB"):
            p.text = ("Data historis 2016–2018 dan volume sekitar 120 MiB tidak membuktikan "
                      "kapasitas enterprise. Label timestamp berbeda dari SLA tanggal kalender. "
                      "Primary seller menyederhanakan multi-seller orders; imputasi bobot memakai "
                      "konstanta. Model sudah diuji dengan split temporal, tetapi precision masih "
                      "rendah, skor belum dikalibrasi, dan validasi tersebut belum mewakili "
                      "deployment masa kini. Graf agregat tidak merekam pergerakan paket atau "
                      "transit. Biaya keputusan, kinerja kueri terdistribusi, dan kepatuhan "
                      "operasional belum diuji.")
        elif p.text.startswith("4.3 Pembersihan organisasi dan operasi data"):
            p.text = "4.3 Dataset untuk Diolah Menggunakan Machine Learning"

    update_ai_declaration(doc)
    doc.save(TARGET)
    print(TARGET)


if __name__ == "__main__":
    main()
