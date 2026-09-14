<?php
defined('BASEPATH') or exit('No direct script access allowed');

class Dashboard extends CI_Controller
{
    public function __construct()
    {
        parent::__construct();
        $this->load->model('Penduduk_model');
    }

    public function index()
    {
        // Menggunakan nama variabel yang benar untuk view
        $data['title'] = 'Dashboard';
        $data['jumlah_penduduk'] = $this->Penduduk_model->count_all_penduduk();
        $data['jumlah_miskin'] = $this->Penduduk_model->count_by_status('Miskin');
        $data['jumlah_tidak_miskin'] = $this->Penduduk_model->count_by_status('Tidak Miskin');

        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar');
        $this->load->view('dashboard/index', $data);
        $this->load->view('templates_administrator/footer');
    }
}
