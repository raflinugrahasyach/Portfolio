<?php
defined('BASEPATH') or exit('No direct script access allowed');

class Penduduk_model extends CI_Model
{
    private $table_penduduk = 'tb_penduduk';
    private $table_klasifikasi = 'tb_klasifikasi';
    private $table_hasil = 'tb_hasil';

    public function getAllPenduduk()
    {
        $this->db->select('p.nik, p.nama, p.alamat, p.rt_rw, h.kelas as status_kemiskinan, k.jenis_kelamin');
        $this->db->from($this->table_penduduk . ' as p');
        $this->db->join($this->table_klasifikasi . ' as k', 'p.nik = k.nik', 'left');
        $this->db->join($this->table_hasil . ' as h', 'k.id_klasifikasi = h.id_klasifikasi', 'left');
        $this->db->order_by('p.nama', 'ASC');
        return $this->db->get()->result_array();
    }

    public function getPendudukById($nik)
    {
        $this->db->select('p.*, k.*, h.kelas, h.tanggal_klasifikasi');
        $this->db->from($this->table_penduduk . ' as p');
        $this->db->join($this->table_klasifikasi . ' as k', 'p.nik = k.nik', 'left');
        $this->db->join($this->table_hasil . ' as h', 'k.id_klasifikasi = h.id_klasifikasi', 'left');
        $this->db->where('p.nik', $nik);
        return $this->db->get()->row_array();
    }
    
    public function simpan_penduduk_dan_klasifikasi($input_data, $hasil_prediksi)
    {
        $this->db->trans_start();
        $data_penduduk = [
            'nik'       => $input_data['nik'], 
            'nama'      => $input_data['nama'],
            'tgl_lahir' => $input_data['tgl_lahir'], 
            'alamat'    => $input_data['alamat'],
            'rt_rw'     => $input_data['rt_rw'],
        ];
        $this->db->insert($this->table_penduduk, $data_penduduk);

        $data_klasifikasi = [
            'nik'               => $input_data['nik'], 
            'jenis_kelamin'     => $input_data['jenis_kelamin'],
            'pendidikan'        => $input_data['pendidikan'], 
            'pekerjaan'         => $input_data['pekerjaan'],
            'status_perkawinan' => $input_data['status_perkawinan'], 
            'tanggungan_anak'   => $input_data['tanggungan_anak'],
            'lantai_rumah'      => $input_data['lantai_rumah'], 
            'dinding_rumah'     => $input_data['dinding_rumah'],
            'daya_listrik'      => $input_data['daya_listrik'], 
            'sumber_air'        => $input_data['sumber_air'],
            'status'            => $hasil_prediksi
        ];
        $this->db->insert($this->table_klasifikasi, $data_klasifikasi);
        $id_klasifikasi = $this->db->insert_id();

        $data_hasil = [
            'id_klasifikasi' => $id_klasifikasi, 
            'nik'            => $input_data['nik'],
            'kelas'          => $hasil_prediksi, 
            'akurasi'        => null,
        ];
        $this->db->insert($this->table_hasil, $data_hasil);

        $this->db->trans_complete();
        return $this->db->trans_status();
    }

    /**
     * Mengubah data penduduk dan kriteria terkait.
     */
    public function ubahDataPenduduk($nik, $data_post)
    {
        // ======================= FUNGSI YANG DIPERBAIKI TOTAL =======================
        // Memulai transaksi database agar aman
        $this->db->trans_start();

        // 1. Siapkan dan Update data pokok di tb_penduduk
        $data_penduduk = [
            "nama"      => $data_post['nama'],
            "tgl_lahir" => $data_post['tgl_lahir'],
            "alamat"    => $data_post['alamat'],
            "rt_rw"     => $data_post['rt_rw'],
        ];
        $this->db->where('nik', $nik);
        $this->db->update($this->table_penduduk, $data_penduduk);

        // 2. Siapkan dan Update data kriteria di tb_klasifikasi
        $data_klasifikasi = [
            'jenis_kelamin'     => $data_post['jenis_kelamin'],
            'pendidikan'        => $data_post['pendidikan'], 
            'pekerjaan'         => $data_post['pekerjaan'],
            'status_perkawinan' => $data_post['status_perkawinan'], 
            'tanggungan_anak'   => $data_post['tanggungan_anak'],
            'lantai_rumah'      => $data_post['lantai_rumah'], 
            'dinding_rumah'     => $data_post['dinding_rumah'],
            'daya_listrik'      => $data_post['daya_listrik'], 
            'sumber_air'        => $data_post['sumber_air'],
        ];
        $this->db->where('nik', $nik);
        $this->db->update($this->table_klasifikasi, $data_klasifikasi);

        // Menyelesaikan transaksi
        $this->db->trans_complete();
        // Mengembalikan status transaksi (true jika berhasil, false jika gagal)
        return $this->db->trans_status();
        // =========================================================================
    }

    public function hapusDataPenduduk($nik)
    {
        $this->db->where('nik', $nik);
        $this->db->delete($this->table_penduduk);
        return $this->db->affected_rows();
    }
    
    public function get_by_nik($nik)
    {
        $this->db->where('nik', $nik);
        return $this->db->get($this->table_penduduk)->row();
    }

    public function count_all_penduduk()
    {
        return $this->db->count_all($this->table_penduduk);
    }

    public function count_by_status($status)
    {
        $this->db->where('kelas', $status);
        return $this->db->count_all_results($this->table_hasil);
    }
}
