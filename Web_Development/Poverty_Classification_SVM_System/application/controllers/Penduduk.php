<?php
defined('BASEPATH') or exit('No direct script access allowed');

class Penduduk extends CI_Controller
{
    public function __construct()
    {
        parent::__construct();
        $this->load->model('Penduduk_model');
        $this->load->library('form_validation');
        $this->load->library('session');
        $this->load->library('pdf');
    }

    public function index()
    {
        $data['judul'] = 'Daftar Penduduk';
        $data['penduduk'] = $this->Penduduk_model->getAllPenduduk();
        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar');
        $this->load->view('penduduk/index', $data);
        $this->load->view('templates_administrator/footer');
    }

    public function tambah()
    {
        $data['judul'] = 'Form Tambah Data & Klasifikasi Penduduk';
        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar');
        $this->load->view('penduduk/tambah');
        $this->load->view('templates_administrator/footer');
    }

    public function proses_tambah()
    {
        $this->form_validation->set_rules('nik', 'NIK', 'required|numeric|exact_length[16]|is_unique[tb_penduduk.nik]');
        $this->form_validation->set_rules('nama', 'Nama', 'required');

        if ($this->form_validation->run() == FALSE) {
            $this->tambah();
        } else {
            $input_data = $this->input->post(null, true);

            $data_to_predict = [
                'jenis_kelamin'     => (int)$input_data['jenis_kelamin'],
                'pendidikan'        => (int)$input_data['pendidikan'],
                'pekerjaan'         => (int)$input_data['pekerjaan'],
                'status_perkawinan' => (int)$input_data['status_perkawinan'],
                'tanggungan_anak'   => (int)$input_data['tanggungan_anak'],
                'lantai_rumah'      => (int)$input_data['lantai_rumah'],
                'dinding_rumah'     => (int)$input_data['dinding_rumah'],
                'daya_listrik'      => (int)$input_data['daya_listrik'],
                'sumber_air'        => (int)$input_data['sumber_air'],
            ];

            $url = 'http://127.0.0.1:5000/predict';
            $ch = curl_init($url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data_to_predict));
            curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
            curl_setopt($ch, CURLOPT_TIMEOUT, 10);

            $response_json = curl_exec($ch);
            $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);

            if ($response_json && $httpcode == 200) {
                $result = json_decode($response_json, true);
                $prediksi = $result['prediction'] ?? 'Tidak Miskin';
            } else {
                $prediksi = 'Tidak Miskin'; 
            }
            
            $this->Penduduk_model->simpan_penduduk_dan_klasifikasi($input_data, $prediksi);
            
            $this->session->set_flashdata('pesan', '<div class="alert alert-success">Data penduduk berhasil ditambahkan dengan hasil klasifikasi: <strong>' . $prediksi . '</strong>.</div>');
            redirect('penduduk');
        }
    }

    public function detail($nik)
    {
        $data['judul'] = 'Detail Data Penduduk';
        $data['penduduk'] = $this->Penduduk_model->getPendudukById($nik);
        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar');
        $this->load->view('penduduk/detail', $data);
        $this->load->view('templates_administrator/footer');
    }
    
    public function ubah($nik)
    {
        $data['judul'] = 'Form Ubah Data Penduduk';
        $data['penduduk'] = $this->Penduduk_model->getPendudukById($nik);
        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar', $data);
        $this->load->view('penduduk/ubah', $data);
        $this->load->view('templates_administrator/footer');
    }
    
    public function ubah_aksi()
    {
        $nik = $this->input->post('nik');
        $data_post = $this->input->post(null, true);

        if ($this->Penduduk_model->ubahDataPenduduk($nik, $data_post)) {
            $this->session->set_flashdata('pesan', '<div class="alert alert-success">Data penduduk berhasil diubah!</div>');
        } else {
            $this->session->set_flashdata('pesan', '<div class="alert alert-danger">Gagal mengubah data!</div>');
        }
        redirect('penduduk');
    }

    public function hapus($nik)
    {
        $this->Penduduk_model->hapusDataPenduduk($nik);
        $this->session->set_flashdata('pesan', '<div class="alert alert-danger">Data berhasil dihapus!</div>');
        redirect('penduduk');
    }
    
    public function laporan()
    {
        $data['judul'] = 'Laporan Hasil Klasifikasi';
        $data['penduduk'] = $this->Penduduk_model->getAllPenduduk();
        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar');
        $this->load->view('penduduk/laporan_hasil', $data);
        $this->load->view('templates_administrator/footer');
    }
    
    public function laporan_pdf()
    {
        // ======================= PERBAIKAN TOTAL DI SINI =======================
        // Menggunakan library Pdf.php sesuai dengan cara kerjanya yang benar
        
        // 1. Ambil data yang diperlukan untuk laporan
        $data['penduduk'] = $this->Penduduk_model->getAllPenduduk();
        
        // 2. Set properti yang ada di library sebelum memanggil fungsinya
        $this->pdf->filename = "laporan-hasil-klasifikasi.pdf";
        $this->pdf->paper_size = 'A4';
        $this->pdf->orientation = 'landscape';

        // 3. Panggil fungsi load_view dari library, yang akan melakukan semua proses
        $this->pdf->load_view('penduduk/lap_hasil_pdf', $data);
        // ======================================================================
    }
}
