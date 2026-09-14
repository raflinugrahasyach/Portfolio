<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class DataPendudukCsv extends CI_Controller
{
    public function __construct()
    {
        parent::__construct();
        // Tidak perlu load model atau database apapun
        $this->load->library('session');
    }

    public function index()
    {
        $data['title'] = "Data Penduduk dari File CSV";
        $data['penduduk_csv'] = []; // Siapkan array kosong

        $csv_file_path = FCPATH . "dummy_penduduk_desa_taraju.csv";

        if (file_exists($csv_file_path)) {
            $handle = fopen($csv_file_path, "r");
            if ($handle !== FALSE) {
                // Lewati baris pertama (header)
                fgetcsv($handle);

                $row_count = 0;
                // Baca baris per baris, maksimal 1500 baris data
                while (($row = fgetcsv($handle, 2000, ",")) !== FALSE && $row_count < 1500) {
                    // Cek jika baris tidak kosong
                    if (isset($row[0]) && !empty($row[0])) {
                        $data['penduduk_csv'][] = $row;
                    }
                    $row_count++;
                }
                fclose($handle);
            }
        } else {
            $this->session->set_flashdata('pesan', '<div class="alert alert-danger">File dummy_penduduk_desa_taraju.csv tidak ditemukan!</div>');
        }
        
        // Muat tampilan
        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar');
        $this->load->view('penduduk/v_data_csv', $data); // Menggunakan view baru
        $this->load->view('templates_administrator/footer');
    }
}

