<?php
defined('BASEPATH') OR exit('No direct script access allowed');

$route['default_controller'] = 'auth';

// KOMENTAR: Rute untuk halaman baru yang hanya menampilkan CSV.
$route['data-penduduk-csv'] = 'DataPendudukCsv';

$route['404_override'] = '';
$route['translate_uri_dashes'] = FALSE;
