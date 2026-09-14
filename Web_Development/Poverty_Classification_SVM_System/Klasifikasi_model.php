<?php
defined('BASEPATH') or exit('No direct script access allowed');

class Klasifikasi_model extends CI_Model
{
    // ... (method get_unclassified_penduduk dan get_riwayat_klasifikasi tidak berubah) ...
    public function get_unclassified_penduduk()
    {
        $subquery = $this->db->select('nik')->from('tb_klasifikasi')->get_compiled_select();
        return $this->db->where("nik NOT IN ($subquery)", NULL, FALSE)->get('tb_penduduk')->result_array();
    }
    
    public function get_riwayat_klasifikasi()
    {
        $this->db->select('p.nama, p.nik, h.kelas, h.tanggal_klasifikasi');
        $this->db->from('tb_hasil as h');
        $this->db->join('tb_klasifikasi as k', 'h.id_klasifikasi = k.id_klasifikasi');
        $this->db->join('tb_penduduk as p', 'k.nik = p.nik');
        $this->db->order_by('h.tanggal_klasifikasi', 'DESC');
        return $this->db->get()->result_array();
    }

    public function save_klasifikasi_data($input, $prediction)
    {
        // Menggunakan nama kolom yang sudah distandardisasi
        $data_klasifikasi = [
            'nik' => $input['nik'],
            'jenis_kelamin' => $input['jenis_kelamin'],
            'pendidikan' => $input['pendidikan'],
            'pekerjaan' => $input['pekerjaan'],
            'status_perkawinan' => $input['status_perkawinan'],
            'anak_sekolah' => $input['anak_sekolah'],
            'lantai_rumah' => $input['lantai_rumah'],
            'dinding_rumah' => $input['dinding_rumah'],
            'daya_listrik' => $input['daya_listrik'],
            'sumber_air' => $input['sumber_air'],
        ];
        $this->db->insert('tb_klasifikasi', $data_klasifikasi);
        $id_klasifikasi = $this->db->insert_id();

        $data_hasil = [
            'id_klasifikasi' => $id_klasifikasi,
            'nik' => $input['nik'],
            'kelas' => $prediction,
            'akurasi' => null,
        ];
        $this->db->insert('tb_hasil', $data_hasil);

        return $id_klasifikasi;
    }
}
