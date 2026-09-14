<?php
defined('BASEPATH') or exit('No direct script access allowed');

class Klasifikasi extends CI_Controller
{
    public function __construct()
    {
        parent::__construct();
        $this->load->model('Klasifikasi_model');
        $this->load->model('Penduduk_model');
        $this->load->library('form_validation');
    }

    public function index()
    {
        $data['judul'] = 'Klasifikasi Kemiskinan';
        $data['penduduk'] = $this->Klasifikasi_model->get_unclassified_penduduk();
        $data['riwayat'] = $this->Klasifikasi_model->get_riwayat_klasifikasi();

        $this->load->view('templates_administrator/header', $data);
        $this->load->view('templates_administrator/sidebar');
        $this->load->view('klasifikasi/index', $data);
        $this->load->view('templates_administrator/footer');
    }

    public function proses()
    {
        $this->form_validation->set_rules('nik', 'NIK Penduduk', 'required');
        
        if ($this->form_validation->run() == FALSE) {
            $this->index();
        } else {
            $input_data = $this->input->post(NULL, TRUE);
            
            $api_url = 'http://127.0.0.1:5000/predict';
            
            // PERBAIKAN: Menggunakan nama field yang benar dari form (sesuai view)
            $features = [
                'jenis_kelamin' => (int)$input_data['jenis_kelamin'],
                'pendidikan' => (int)$input_data['pendidikan'],
                'pekerjaan' => (int)$input_data['pekerjaan'],
                'status_perkawinan' => (int)$input_data['status_perkawinan'],
                'anak_sekolah' => (int)$input_data['anak_sekolah'],
                'lantai_rumah' => (int)$input_data['lantai_rumah'],
                'dinding_rumah' => (int)$input_data['dinding_rumah'],
                'daya_listrik' => (int)$input_data['daya_listrik'],
                'sumber_air' => (int)$input_data['sumber_air']
            ];

            $payload = json_encode(['data' => $features]);
            
            $ch = curl_init($api_url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
            curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
            
            $response = curl_exec($ch);
            $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            $curl_error = curl_error($ch);
            curl_close($ch);
            
            if ($http_code == 200 && $response) {
                $result = json_decode($response, true);
                $prediction = $result['prediction'];
                $this->Klasifikasi_model->save_klasifikasi_data($input_data, $prediction);
                $this->session->set_flashdata('flash', 'Klasifikasi Berhasil');
                redirect('klasifikasi');
            } else {
                $error_message = "Gagal memproses klasifikasi (HTTP Code: {$http_code}).";
                if ($curl_error) { $error_message .= " cURL Error: " . $curl_error; }
                elseif ($response) {
                    $api_error = json_decode($response, true);
                    $error_message .= isset($api_error['error']) ? ' Pesan API: ' . $api_error['error'] : ' Respons API tidak valid.';
                } else { $error_message .= ' Tidak ada respons dari server API.'; }
                $this->session->set_flashdata('flash-error', $error_message);
                redirect('klasifikasi');
            }
        }
    }
}
