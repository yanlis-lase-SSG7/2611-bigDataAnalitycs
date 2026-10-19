# Build the Assignment II presentation from verified aggregate results.
# Requires desktop Microsoft PowerPoint on Windows; source figures remain editable
# in the project while all slide text is native PowerPoint text.
param(
    [string]$Output = (Join-Path $PSScriptRoot 'presentations/Big Data Analytics - Presentation Assignment II 2702751284.pptx')
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$navy = '10253D'; $deep = '0B1B2E'; $teal = '087E85'; $mint = 'CDEAE6'
$paper = 'F6F8F7'; $ink = '173049'; $muted = '54707D'; $orange = 'D78340'

function RGB([string]$hex) {
    $r = [Convert]::ToInt32($hex.Substring(0, 2), 16)
    $g = [Convert]::ToInt32($hex.Substring(2, 2), 16)
    $b = [Convert]::ToInt32($hex.Substring(4, 2), 16)
    return [int]($r + 256 * $g + 65536 * $b)
}
function Rect($s, [double]$x, [double]$y, [double]$w, [double]$h, [string]$fill, [double]$radius=0) {
    $kind = if ($radius -gt 0) { 5 } else { 1 }
    $q = $s.Shapes.AddShape($kind, $x, $y, $w, $h)
    $q.Fill.ForeColor.RGB = RGB $fill
    $q.Line.Visible = 0
    return $q
}
function Txt($s, [string]$value, [double]$x, [double]$y, [double]$w, [double]$h,
             [double]$size=18, [string]$color='173049', [bool]$bold=$false,
             [int]$align=1) {
    $q = $s.Shapes.AddTextbox(1, $x, $y, $w, $h)
    $q.TextFrame.MarginLeft = 0; $q.TextFrame.MarginRight = 0
    $q.TextFrame.MarginTop = 0; $q.TextFrame.MarginBottom = 0
    $q.TextFrame.WordWrap = -1
    $q.TextFrame.TextRange.Text = $value
    $q.TextFrame.TextRange.Font.Name = 'Aptos'
    $q.TextFrame.TextRange.Font.Size = $size
    $q.TextFrame.TextRange.Font.Bold = [int]$bold
    $q.TextFrame.TextRange.Font.Color.RGB = RGB $color
    $q.TextFrame.TextRange.ParagraphFormat.Alignment = $align
    return $q
}
function Pic($s, [string]$file, [double]$x, [double]$y, [double]$w, [double]$h) {
    $image = [System.Drawing.Image]::FromFile($file)
    try { $ratio = $image.Width / $image.Height } finally { $image.Dispose() }
    if ($w / $h -gt $ratio) { $pw = $h * $ratio; $ph = $h }
    else { $pw = $w; $ph = $w / $ratio }
    $px = $x + ($w - $pw) / 2; $py = $y + ($h - $ph) / 2
    return $s.Shapes.AddPicture($file, 0, -1, $px, $py, $pw, $ph)
}
function Base($p, [int]$num, [string]$title, [string]$tag='ASSIGNMENT II', [string]$source='Sumber: hasil eksperimen Olist, 2026') {
    $s = $p.Slides.Add($num, 12)
    Rect $s 0 0 960 540 $paper | Out-Null
    Rect $s 0 0 960 9 $teal | Out-Null
    Txt $s $tag 42 28 620 22 11 $teal $true | Out-Null
    Txt $s $title 42 55 865 66 30 $navy $true | Out-Null
    Rect $s 42 493 876 1 'C7D3D2' | Out-Null
    Txt $s $source 42 503 805 22 9 $muted | Out-Null
    Txt $s ('{0:00} / 12' -f $num) 847 503 70 22 9 $muted $false 3 | Out-Null
    return $s
}
function Card($s, [double]$x, [double]$y, [double]$w, [double]$h,
              [string]$label, [string]$value, [string]$detail, [string]$accent='087E85') {
    Rect $s $x $y $w $h 'FFFFFF' 1 | Out-Null
    Rect $s $x $y 6 $h $accent | Out-Null
    Txt $s $label ($x+19) ($y+18) ($w-38) 25 12 $muted $true | Out-Null
    Txt $s $value ($x+19) ($y+48) ($w-38) 54 34 $navy $true | Out-Null
    Txt $s $detail ($x+19) ($y+108) ($w-38) ($h-120) 13 $ink | Out-Null
}
function Note($s, [string]$value) {
    try { $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $value } catch {}
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Add()
try {
    $pres.PageSetup.SlideWidth = 960
    $pres.PageSetup.SlideHeight = 540

    # 1 Cover
    $s = $pres.Slides.Add(1, 12)
    Rect $s 0 0 960 540 $deep | Out-Null
    Rect $s 0 0 13 540 $teal | Out-Null
    Rect $s 685 73 180 180 $teal 1 | Out-Null
    Txt $s 'BDA / ASSIGNMENT II' 58 58 460 27 13 $mint $true | Out-Null
    Txt $s "Membaca risiko`nketerlambatan`npesanan Olist" 58 128 610 215 42 'FFFFFF' $true | Out-Null
    Txt $s 'Machine learning dan graf asal–tujuan state' 58 370 650 34 20 $mint | Out-Null
    Txt $s 'Yanlis Alim Sang Putra Lase  |  2702751284  |  M.TI BINUS' 58 475 800 30 13 'FFFFFF' | Out-Null
    Note $s 'Pembukaan. Jelaskan masalah dan cakupan, bukan klaim kesiapan produksi.'

    # 2 Business question
    $s = Base $pres 2 'Mengapa keterlambatan perlu dipantau?' 'MASALAH BISNIS' 'Sumber: keluaran notebook 02 dan laporan Assignment I'
    Card $s 42 145 270 260 'ORDER BERLABEL' '96.470' 'Pesanan delivered dengan tanggal penerimaan dan estimasi yang valid.' | Out-Null
    Card $s 327 145 270 260 'TERLAMBAT' '8,11%' '7.826 order diterima setelah tanggal estimasi.' $orange | Out-Null
    Card $s 612 145 306 260 'SKOR ULASAN' '4,29 → 2,57' 'Rata-rata review order tepat waktu dibanding order terlambat; ini asosiasi, bukan bukti sebab-akibat.' | Out-Null
    Txt $s 'Pertanyaan: dapatkah risiko diperkirakan sebelum hasil pengiriman diketahui?' 45 431 865 42 19 $navy $true | Out-Null
    Note $s 'Tekankan dampak layanan dan perbedaan review sebagai asosiasi.'

    # 3 Data pipeline
    $s = Base $pres 3 'Dari pesanan terkirim ke data model' 'DATA PIPELINE' 'Sumber: audit data notebook 01–02 dan output Assignment II'
    Card $s 42 146 269 246 'DELIVERED' '96.478' 'Seluruh order dengan status delivered.' | Out-Null
    Card $s 332 146 269 246 'LABEL VALID' '96.470' 'Delapan order tanpa tanggal yang diperlukan untuk label dikeluarkan.' | Out-Null
    Card $s 622 146 296 246 'MODEL VALID' '96.455' 'Lima belas order dengan prediktor kosong atau tidak finite dikeluarkan.' | Out-Null
    Txt $s 'CSV asli → Parquet Snappy → fitur tingkat order → train / validation / test' 53 428 850 43 19 $navy $true 2 | Out-Null
    Note $s 'Jelaskan validasi dan bahwa Spark berjalan lokal pada satu mesin.'

    # 4 Features
    $s = Base $pres 4 'Sepuluh fitur yang dipertahankan' 'FEATURE ENGINEERING' 'Sumber: assignment2_experiments.py; outputs_ml_graph/model_evaluation_report.json'
    Rect $s 42 138 425 315 'FFFFFF' 1 | Out-Null
    Rect $s 485 138 433 315 'FFFFFF' 1 | Out-Null
    Txt $s 'Nilai dan pengiriman' 61 158 370 30 18 $teal $true | Out-Null
    Txt $s "total_items`ntotal_price`ntotal_freight`nfreight_ratio`nmax_installments" 61 207 375 225 19 $ink | Out-Null
    Txt $s 'Estimasi dan konteks order' 504 158 383 30 18 $teal $true | Out-Null
    Txt $s "estimated_delivery_days`nis_same_state`npurchase_dayofweek`npurchase_hour`nproduct_weight_g" 504 207 370 225 19 $ink | Out-Null
    Note $s 'Jangan menyebut feature importance sebagai bukti kausal.'

    # 5 Modeling protocol
    $s = Base $pres 5 'Tiga model, dua cara memisahkan waktu' 'MODEL & EVALUASI' 'Sumber: assignment2_experiments.py dan outputs_assignment2/split_profile.csv'
    Card $s 42 142 270 241 'DENGAN SPARK MLLIB' 'RF' 'Random Forest pada PySpark, berjalan di local[4].' | Out-Null
    Card $s 327 142 270 241 'TANPA SPARK MLLIB' 'RF' 'Random Forest scikit-learn pada data/split yang sepadan.' | Out-Null
    Card $s 612 142 306 241 'PEMBANDING SEDERHANA' 'LR' 'Logistic Regression dengan StandardScaler yang fit hanya pada train.' | Out-Null
    Txt $s 'Hash: membership Assignment I   •   Kronologis: 64% train / 16% validation / 20% test' 46 410 875 32 16 $navy $true | Out-Null
    Txt $s 'Ambang dipilih dari validation; test hanya dipakai untuk evaluasi akhir.' 46 447 875 25 14 $muted | Out-Null
    Note $s 'Perbedaan model bukan perbandingan murni framework; algoritma LR juga berbeda.'

    # 6 Six test results
    $s = Base $pres 6 'Hasil test berubah pada split kronologis' 'EVALUASI ML' 'Sumber: outputs_assignment2/model_comparison.csv; ambang dipilih pada validation'
    $x = @(44, 207, 515, 626, 742)
    $head = @('Split','Model','Precision','Recall','F1')
    for ($j=0; $j -lt 5; $j++) { Txt $s $head[$j] $x[$j] 139 170 25 12 $teal $true | Out-Null }
    $rows = @(
        @('Hash','sklearn LR','14,90%','42,21%','0,2202'),
        @('Hash','sklearn RF','15,32%','39,06%','0,2201'),
        @('Hash','Spark RF','14,77%','45,03%','0,2224'),
        @('Waktu','sklearn LR','6,82%','34,57%','0,1139'),
        @('Waktu','sklearn RF','10,35%','64,64%','0,1785'),
        @('Waktu','Spark RF','5,17%','26,93%','0,0867')
    )
    for ($i=0; $i -lt 6; $i++) {
        $y = 170 + 44*$i
        Rect $s 42 $y 876 40 $(if ($i%2 -eq 0) {'FFFFFF'} else {'EAF0EF'}) 1 | Out-Null
        for ($j=0; $j -lt 5; $j++) { Txt $s $rows[$i][$j] $x[$j] ($y+7) 185 26 15 $(if ($i -eq 4) {$teal} else {$ink}) ($i -eq 4) | Out-Null }
    }
    Txt $s 'Prevalensi test: hash 8,16%; waktu 5,29%. Perbedaan ini memengaruhi pembacaan precision.' 46 449 867 34 13 $muted | Out-Null
    Note $s 'Sampaikan penurunan F1 temporal sebagai observasi. Penyebabnya belum dibuktikan.'

    # 7 Alert budget
    $s = Base $pres 7 'Berapa banyak order yang perlu ditinjau?' 'AMBANG PREDIKSI' 'Sumber: outputs_assignment2/alert_budget_scenarios.csv; temporal sklearn RF'
    Card $s 42 143 270 263 'BUDGET VALIDATION 1%' '487 alert' 'Test: 88 benar terlambat, 399 false positive; precision 18,07%, recall 8,62%.' | Out-Null
    Card $s 327 143 270 263 'BUDGET VALIDATION 5%' '2.539 alert' 'Test: precision 12,68%, recall 31,54%.' $orange | Out-Null
    Card $s 612 143 306 263 'BUDGET VALIDATION 10%' '4.208 alert' 'Test: precision 11,50%, recall 47,40%.' | Out-Null
    Txt $s 'Anggaran pada validation tidak menjamin jumlah alert test. Belum ada ambang operasional final.' 45 432 870 48 16 $navy $true | Out-Null
    Note $s 'Prioritas mahasiswa adalah mengurangi false positive; tetap perlu kapasitas dan kriteria bisnis nyata.'

    # 8 Graph topology
    $s = Base $pres 8 'Graf asal–tujuan antar-state' 'GRAPH ANALYTICS' 'Sumber: notebook 03 dan figures/fig8_graph_network_topology.png'
    Rect $s 42 132 470 335 'FFFFFF' 1 | Out-Null
    Pic $s (Join-Path $root 'figures/fig8_graph_network_topology.png') 57 144 440 310 | Out-Null
    Card $s 533 143 385 143 'GRAF BERARAH' '27 state' '409 edge seller-state → customer-state.' | Out-Null
    Rect $s 533 302 385 154 'E4EFEC' 1 | Out-Null
    Txt $s 'Cara membaca' 553 317 330 29 19 $teal $true | Out-Null
    Txt $s 'Node = state. Edge = pasangan asal–tujuan order. Posisi gambar skematis; hanya 35 edge dengan volume tertinggi ditampilkan.' 553 354 330 89 16 $ink | Out-Null
    Note $s 'Jangan menyebut edge sebagai jalur transit atau lokasi hub fisik.'

    # 9 Graph insights
    $s = Base $pres 9 'Relasi OD yang layak diperiksa lebih dulu' 'TEMUAN GRAF' 'Sumber: outputs_ml_graph/graph_network_metrics.csv; docs/assignment2-technical-results.md'
    Rect $s 42 139 470 316 'FFFFFF' 1 | Out-Null
    Pic $s (Join-Path $root 'figures/fig10_route_volume_delay.png') 51 151 452 285 | Out-Null
    Txt $s 'SP → RJ' 536 151 300 34 25 $navy $true | Out-Null
    Txt $s '8.158 order  •  1.264 terlambat  •  15,49%' 536 190 370 49 17 $teal $true | Out-Null
    Txt $s 'PageRank tertinggi: SP 0,2997. Betweenness topologis tertinggi: MG 0,0506.' 536 260 370 81 17 $ink | Out-Null
    Txt $s 'SP→MA dan SP→AL memiliki rate lebih tinggi, tetapi volume lebih kecil; selalu tampilkan pembilang dan penyebut.' 536 360 370 91 15 $muted | Out-Null
    Note $s 'Ini prioritas pemeriksaan OD, bukan bukti kemacetan fisik.'

    # 10 Recommendations
    $s = Base $pres 10 'Usulan tindak lanjut yang bisa diuji' 'IMPLIKASI BISNIS' 'Dasar: metrik test, skenario alert, dan graf OD; belum diuji sebagai intervensi'
    Card $s 42 144 270 265 '1 / PILOT' 'Tinjau manual' 'Uji daftar risiko kecil dengan tim operasional; catat biaya review dan false positive.' | Out-Null
    Card $s 327 144 270 265 '2 / PRIORITAS' 'Pantau OD' 'Periksa volume dan delay SP→RJ; bandingkan dengan rute lain memakai denominator.' $orange | Out-Null
    Card $s 612 144 306 265 '3 / EVALUASI' 'Uji periode baru' 'Pantau precision, recall, prevalensi, kalibrasi, dan perubahan komposisi data.' | Out-Null
    Txt $s 'Keputusan otomatis atau perubahan jaringan fisik memerlukan bukti tambahan.' 47 437 870 40 16 $navy $true | Out-Null
    Note $s 'Rekomendasi ini hipotesis langkah kerja, bukan hasil uji dampak.'

    # 11 Governance and disclosure
    $s = Base $pres 11 'Batas penggunaan dan deklarasi AI' 'TATA KELOLA' 'Sumber: laporan Assignment II, halaman 31; formulir menunggu tanda tangan mahasiswa'
    Rect $s 42 139 418 311 'FFFFFF' 1 | Out-Null
    Txt $s 'Data & model' 61 158 365 32 20 $teal $true | Out-Null
    Txt $s "• Hasil agregat dipublikasikan; prediksi per-order dan raw data tetap lokal.`n• Spark diuji pada satu mesin, bukan cluster produksi.`n• Ambang skor belum disahkan untuk tindakan otomatis." 61 205 365 216 16 $ink | Out-Null
    Rect $s 481 139 437 311 'E4EFEC' 1 | Out-Null
    Txt $s 'AI Use Declaration' 501 158 382 32 20 $teal $true | Out-Null
    Txt $s 'Type 2 / Partial Use' 501 210 380 37 27 $navy $true | Out-Null
    Txt $s 'Estimasi mahasiswa: 15%' 501 258 380 34 20 $navy $true | Out-Null
    Txt $s 'Bantuan kode, visualisasi, draf teks, dan format dokumen diungkapkan. Mahasiswa harus memeriksa interpretasi akhir dan menandatangani formulir.' 501 315 380 111 16 $ink | Out-Null
    Note $s 'Jangan menyatakan persentase ini terukur otomatis atau bahwa seluruh teks bebas bantuan AI.'

    # 12 Close
    $s = $pres.Slides.Add(12, 12)
    Rect $s 0 0 960 540 $deep | Out-Null
    Rect $s 0 0 13 540 $teal | Out-Null
    Txt $s 'KESIMPULAN' 59 62 600 30 13 $mint $true | Out-Null
    Txt $s "Model memberi sinyal;`nkeputusan perlu validasi" 59 130 820 153 42 'FFFFFF' $true | Out-Null
    Txt $s 'F1 temporal terbaik dari tiga kandidat: 0,1785. Graf OD menunjukkan konsentrasi order, bukan jalur fisik.' 61 319 830 95 21 $mint | Out-Null
    Txt $s 'Terima kasih  •  Tanya jawab' 61 467 790 34 19 'FFFFFF' | Out-Null
    Note $s 'Tutup dengan keterbatasan, rencana uji berikutnya, lalu buka tanya jawab.'

    $pres.SaveAs($Output, 24)
    $qaDir = Join-Path $root '.report_review'
    New-Item -ItemType Directory -Force -Path $qaDir | Out-Null
    $pdf = Join-Path $qaDir 'assignment2_presentation.pdf'
    $pres.SaveAs($pdf, 32)
    Write-Output "PPTX=$Output"
    Write-Output "PDF=$pdf"
    Write-Output "SLIDES=$($pres.Slides.Count)"
} finally {
    $pres.Close()
    $ppt.Quit()
}
