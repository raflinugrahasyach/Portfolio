<?php
defined('BASEPATH') or exit('No direct script access allowed');

require_once(APPPATH . 'third_party/dompdf/autoload.inc.php');
use Dompdf\Dompdf;
use Dompdf\Options;

class Pdf
{
    public $filename;
    public $paper_size;
    public $orientation;

    public function __construct()
    {
        // Set default values
        $this->filename = 'laporan.pdf';
        $this->paper_size = 'A4';
        $this->orientation = 'portrait';
    }

    protected function ci()
    {
        return get_instance();
    }

    public function load_view($view, $data = array())
    {
        $options = new Options();
        $options->set('isRemoteEnabled', true); // Allow remote images
        
        $dompdf = new Dompdf($options);
        $html = $this->ci()->load->view($view, $data, TRUE);

        $dompdf->loadHtml($html);
        $dompdf->setPaper($this->paper_size, $this->orientation);
        $dompdf->render();
        
        // Output the generated PDF to Browser
        // Attachment => 0 (false) = preview in browser
        // Attachment => 1 (true) = force download
        $dompdf->stream($this->filename, array('Attachment' => 0));
    }
}
