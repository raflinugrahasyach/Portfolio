<?php
// FILE: application/views/v_dashboard.php
// FUNGSI: Tampilan halaman dashboard utama, meniru Gambar 4.9 dari PDF.
?>

<h1 class="h3 mb-4 text-gray-800"><?= $judul; ?></h1>

<div class="row">

    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Total Penduduk Terdata</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800"><?= $total_penduduk; ?></div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-users fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-danger shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-danger text-uppercase mb-1">Penduduk Miskin</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800"><?= $total_miskin; ?></div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-exclamation-circle fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Penduduk Tidak Miskin</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800"><?= $total_tidak_miskin; ?></div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-check-circle fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-info shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Akurasi Model (Contoh)</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800">74.4%</div>
                    </div>
                    <div class="col-auto">
                        <i class="fas fa-percentage fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="card shadow mb-4">
    <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-primary">Selamat Datang!</h6>
    </div>
    <div class="card-body">
        <p>Anda berhasil login sebagai <strong>admin</strong>. Sistem ini, Anda dapat mengelola data penduduk dan melakukan klasifikasi status ekonomi menggunakan metode Support Vector Machine (SVM) untuk menentukan kelayakan penerimaan bantuan sosial.</p>
        <p class="mb-0">Silakan gunakan menu di sebelah kiri untuk menavigasi halaman.</p>
    </div>
</div>
