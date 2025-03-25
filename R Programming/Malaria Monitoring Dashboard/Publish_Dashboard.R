# Load necessary libraries
library(shiny)
library(shinydashboard)
library(leaflet)
library(readxl)
library(DT)
library(ggplot2)
library(pheatmap)
library(RColorBrewer)
library(DCluster)
library(VGAM)
library(gamlss)
library(lmtest)
library(nortest)
library(AER)
library(dplyr)
library(openxlsx)


# Load data
data <- read_excel("./datates.xlsx")

# Define UI

custom_css <- "

  .sidebar-menu .fa {
    margin-right: 10px; /* Jarak antara ikon dan teks */
    
  }  

  body, .content-wrapper, .right-side, .skin-blue .main-content {
    background-color: #ffffff !important;
    font-family: 'Helvetica', sans-serif; /* Menggunakan font Helvetica */
  }
  
  .content-wrapper {
    padding-left: 40px; /* Jarak dari sisi kiri */
    padding-right: 40px; /* Jarak dari sisi kanan */
  }

  .skin-blue .main-header .navbar {
    background-color: #0c1414; /* Earth tone header */
  }

  .skin-blue .main-header .logo {
    background-color: #0c1414; /* Logo area */
    color: white;
  }

  .skin-blue .main-sidebar {
    background-color: #2d3f3f; /* Sidebar background */
    color: white;
  }

  .skin-blue .sidebar-menu > li > a {
    color: #ffffff; /* Sidebar menu text */
    font-size: 16px;
  }

  .skin-blue .sidebar-menu > li.active > a {
    background-color: #0c1414;
    color: white;
  }

  .value-box {
    background-color: transparent !important;
    color: #6b8e23;
    border: none !important;
    padding: 15px;
    font-size: 18px;
    text-align: center;
  }

  .value-box .icon {
    font-size: 30px;
    margin-bottom: 10px;
  }

  h2, h3 {
    color: #hhhhhh;
  }

  .btn-primary {
    background-color: #8fbc8f;
    border-color: #556b2f;
  }

  .btn-primary:hover {
    background-color: #556b2f;
    border-color: #6b8e23;
  }

  .leaflet-container {
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
  }

  .box {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
  }
  
  .value-box-custom {
    background-color: #2c3e3f !important; /* Warna latar belakang sesuai gambar */
    color: white !important; /* Warna teks */
    border-radius: 12px; /* Membuat sudut membulat */
    flex-basis: 10%; /* Kotak mengambil 30% dari lebar kontainer flex */
    padding: 10px 24px; /* Padding atas-bawah (20px) dan kiri-kanan (14px) */
    display: flex; /* Membuat layout fleksibel */
    justify-content: space-between; /* Pemisahan teks kiri dan kanan */
    align-items: center; /* Rata tengah secara vertikal */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Efek bayangan */
    font-family: 'Helvetica', sans-serif; /* Font Helvetica */
    margin-bottom: 20px; /* Jarak antar kotak */
  }

  .value-box-custom .value {
    font-size: 42px; /* Ukuran teks utama */
    font-weight: bold;
    margin: 6;
    color: #ffffff;
  }

  .value-box-custom .description {
    font-size: 22px; /* Ukuran teks keterangan */
    margin: 10;
    padding: 14;
    color: #ffffff;
    text-align: right; /* Rata kanan */
  }

  .value-box-title {
    font-size: 18px; /* Ukuran font judul */
    font-weight: bold;
    margin-bottom: 4px;
    color: #0c1414; /* Warna teks judul */
  }
  
  .custom-paragraph {
  font-size: 18px; /* Ukuran font untuk paragraf */
  font-family: 'Helvetica', sans-serif; /* Font Helvetica untuk paragraf */
  text-align: justify; /* Rata kiri-kanan */
  line-height: 1.6; /* Jarak antar-baris */
  }
  
  .title-malaria {
  font-size: 30px;
  font-family: 'Helvetica', sans-serif;
  font-weight: bold;
  text-align: left;
  margin-bottom: 15px;
  }
  
  .map-container {
  margin: 0 15px; /* Margin kiri dan kanan */
}

"

dashboard_ui <- dashboardPage(
  
  # Menambahkan kelas 'custom-header' ke dashboardHeader
  dashboardHeader(
    title = tags$div(
      class = "custom-header",
      "Dashboard Informasi dan Analisis Malaria Indonesia"
    ),
    tags$li(class = "dropdown", 
            tags$style("
              /* Agar header lebih fleksibel untuk teks panjang */
              .main-header { 
                height: auto; /* Biarkan header menyesuaikan tinggi berdasarkan teks */
                text-align: center;
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap; /* Membolehkan elemen di dalam header untuk membungkus */
              }
              .main-header .logo {
                flex: 1 1 auto; /* Mengatur logo agar memiliki ruang sendiri */
              }
              .custom-header {
                flex: 1 1 0%; /* Memberikan lebih banyak ruang untuk teks judul */
                word-wrap: break-word;
                word-break: break-word;
                font-size: 20px;
                font-weight: bold;
                text-align: left;
              }
            "))
  ),
  
  dashboardSidebar(
    sidebarMenu(
      menuItem("Beranda", tabName = "beranda", icon = icon("home")),
      menuItem("Analisis", tabName = "analisis", icon = icon("table"),
               menuSubItem("Tabel", tabName = "tabel", icon = icon("table")),
               menuSubItem("Visualisasi", tabName = "visualisasi", icon = icon("chart-line")),
               menuSubItem("Variabel", tabName = "variabel", icon = icon("sliders")),
               menuSubItem("Input Data", tabName = "input_data", icon = icon("chart-pie"))
      ),
      menuItem("Sumber", tabName = "sumber", icon = icon("info"))
    ),
    tags$style(HTML(custom_css)
    )
  ),
  
  dashboardBody(
    tags$head(
      tags$style(HTML(custom_css))
    ),
    tabItems(
      # Halaman Beranda
      tabItem(tabName = "beranda",
              # Title "Apa itu Malaria?" dan Penjelasan
              fluidRow(
                column(
                  width = 12,
                  tags$div(
                    tags$h3("Apa itu Malaria?", class = "title-malaria"),  # Judul
                    tags$p("Malaria merupakan masalah kesehatan masyarakat signifikan di Indonesia, terutama di daerah endemis, karena fluktuasi prevalensinya meskipun berbagai program pengendalian telah diterapkan. Contohnya, Kabupaten Purworejo di Jawa Tengah kembali melaporkan kasus malaria pada 2021 setelah sempat berhasil ditekan pada 2004, mengindikasikan kendala dalam pengendalian vektor, perilaku masyarakat, dan keberlanjutan program kesehatan (Shinta & Manalu, 2022). Pemerintah menargetkan eliminasi malaria pada 2030 sesuai Keputusan Menteri Kesehatan RI Nomor 293/Menkes/SK/IV/2009, namun API nasional meningkat dari kurang dari 1 per 1.000 penduduk pada 2015–2020 menjadi 1,5 pada 2023, dengan 418.546 kasus positif dari 3,46 juta pemeriksaan. Upaya eliminasi membutuhkan pendekatan holistik, termasuk penggunaan kelambu berinsektisida, larvasida, dan intervensi berbasis bukti yang mempertimbangkan faktor lingkungan, sosial, budaya, dan bionomik Anopheles spp. (Shinta & Manalu, 2022).",
                           class = "custom-paragraph")
                  )
                )
              ),
              
              fluidRow(
                tags$div(
                  class = "map-container", # Tambahkan class untuk margin
                  tags$h3("Peta Penyebaran Malaria", class = "title-malaria"), # Judul peta
                  leafletOutput("map", height = 500) # Output peta
                )
              ),
              
              # Heatmap dan Informasi Tambahan
              fluidRow(
                column(width = 6, 
                       box(width = 12, plotOutput("heatmap"))
                ),
                column(width = 6, 
                       box(width = 12,
                           valueBoxOutput("total_malaria", width = 12),
                           valueBoxOutput("highest_province", width = 12),
                           valueBoxOutput("lowest_province", width = 12)
                       )
                )
              )
      ),
      
      # Subhalaman Tabel
      tabItem(tabName = "tabel",
              fluidRow(
                box(title = "Tabel Data Penyebaran Malaria", width = 12,
                    DTOutput("data_table"))
              )
      ),
      
      # Subhalaman Visualisasi
      tabItem(tabName = "visualisasi",
              fluidRow(
                h2("Visualisasi Data dan Statistik Deskriptif", 
                   style = "margin-bottom: 50px; font-size: 24px; font-weight: bold;")
              ),
              
              # Iterasi Variabel
              tagList(
                lapply(c("JP", "SD", "UNPK", "LSL", "IKK", "TBJ"), function(var) {
                  tagList(
                    fluidRow(
                      column(4, uiOutput(paste0(var, "_highest"))), # Menggunakan uiOutput
                      column(4, uiOutput(paste0(var, "_lowest"))), # Menggunakan uiOutput
                      column(4, uiOutput(paste0(var, "_mean"))) # Menggunakan uiOutput
                    ),
                    fluidRow(
                      box(
                        title = paste("Distribusi", var, "per Provinsi"),
                        width = 12,
                        plotOutput(paste0(var, "_barchart"))
                      )
                    ))
                })
              )
      ),
      
      # Subhalaman Variabel
      tabItem(
        tabName = "variabel",
        fluidRow(
          # Subjudul
          h2(
            "Penjelasan Variabel", 
            style = "margin-bottom: 30px; font-size: 32px; font-weight: bold; text-align: left;"
          ),
          box(
            width = 12, 
            tags$ul(
              tags$li(
                tags$b("1. Jumlah Penduduk Indonesia yang Memiliki KTP (JP)"), 
                style = "font-size: 24px;",
                tags$p("Jumlah penduduk yang memiliki Kartu Tanda Penduduk (KTP) di Indonesia mencerminkan tingkat pendaftaran penduduk dan akses mereka terhadap layanan publik, termasuk kesehatan. KTP berfungsi sebagai identitas resmi yang memungkinkan individu untuk mendapatkan layanan kesehatan yang lebih baik, yang pada gilirannya berkontribusi pada peningkatan Indeks Pembangunan Manusia (IPM) (Arisman, 2018).", style = "font-size: 16px;")
              ),
              tags$li(
                tags$b("2. Tingkat Penyelesaian Pendidikan Jenjang Sekolah Dasar (SD)"), 
                style = "font-size: 24px;",
                tags$p("Tingkat penyelesaian pendidikan pada jenjang sekolah dasar sangat penting untuk pengembangan sumber daya manusia. Pendidikan dasar yang baik berkontribusi pada kesehatan yang lebih baik dan produktivitas yang lebih tinggi di masa depan. Penelitian menunjukkan bahwa akses pendidikan yang baik dapat meningkatkan kualitas hidup dan kesehatan masyarakat (Hasanah & Oktafia, 2024).", style = "font-size: 16px;")
              ),
              tags$li(
                tags$b("3. Persentase Unmet Need Pelayanan Kesehatan (UNPK)"), 
                style = "font-size: 24px;",
                tags$p("Unmet need dalam pelayanan kesehatan menunjukkan proporsi individu yang membutuhkan layanan kesehatan tetapi tidak mendapatkannya, sering kali karena faktor biaya. Hal ini berdampak negatif pada kesehatan masyarakat, dan mengatasi unmet need sangat penting untuk meningkatkan kualitas hidup dan kesehatan masyarakat (Tehupeiory, et al., 2023).", style = "font-size: 16px;")
              ),
              tags$li(
                tags$b("4. Proporsi Rumah Tangga yang Memiliki Akses Terhadap Layanan Sanitasi Layak (LSL)"), 
                style = "font-size: 24px;",
                tags$p("Akses terhadap layanan sanitasi yang layak berhubungan erat dengan kesehatan masyarakat. Sanitasi yang baik dapat mengurangi risiko penyakit menular dan meningkatkan kesehatan secara keseluruhan. Data menunjukkan bahwa proporsi rumah tangga yang memiliki akses terhadap sanitasi layak di Indonesia masih perlu ditingkatkan untuk mencapai tujuan pembangunan berkelanjutan (Mongan, 2019).", style = "font-size: 16px;")
              ),
              tags$li(
                tags$b("5. Indeks Kedalaman Kemiskinan (P1) (IKK)"), 
                style = "font-size: 24px;",
                tags$p("Indeks kedalaman kemiskinan (P1) mengukur seberapa dalam kondisi kemiskinan yang dialami oleh penduduk miskin. Tingkat kemiskinan yang tinggi sering kali berkorelasi dengan akses yang buruk terhadap layanan kesehatan, yang dapat memperburuk kondisi kesehatan masyarakat. Oleh karena itu, pengurangan kedalaman kemiskinan sangat penting untuk meningkatkan kesehatan dan kesejahteraan masyarakat (Putri & Muljaningsih, 2022).", style = "font-size: 16px;")
              ),
              tags$li(
                tags$b("6. Persentase Penduduk yang Mempunyai Keluhan Kesehatan Selama Sebulan Terakhir dan Tidak Berobat Jalan Menurut Alasan Utama Tidak Berobat Jalan - Tidak Punya Biaya Berobat (TBJ)"), 
                style = "font-size: 24px;",
                tags$p("Persentase penduduk yang mengalami keluhan kesehatan tetapi tidak berobat karena alasan biaya menunjukkan adanya hambatan finansial dalam akses layanan kesehatan. Hal ini dapat memperburuk kondisi kesehatan individu dan populasi secara keseluruhan. Oleh karena itu, penting untuk mengembangkan kebijakan yang mengurangi hambatan biaya untuk meningkatkan akses terhadap layanan kesehatan (Swiyono, Nur, & Apriliani, 2023).", style = "font-size: 16px;")
              )
            )
          )
        )
      ),
      tabItem(
        tabName = "input_data",
        fluidRow(
          # Kolom untuk mengunggah data
          column(
            6,
            fileInput(
              "file_upload", 
              tags$h4("Pilih data (Excel):"), 
              accept = c(".xlsx")  # Hanya menerima file Excel
            ),
            numericInput(
              "n_rows", 
              tags$h4("Tampilkan"), 
              value = 2, 
              min = 1
            ),
            tableOutput("uploaded_preview")  # Tabel untuk preview data yang diunggah
          ),
          
          # Kolom untuk template tabel
          column(
            6,
            tags$h4("Template Excel"),  # Title di atas tombol unduh
            downloadButton(
              "download_template", 
              "Unduh data"
            )  
          )
        ),
        
        # Hasil perhitungan analisis
        fluidRow(
          column(
            12,
            h4("Hasil Perhitungan"),
            tableOutput("calculation_result")  # Tabel untuk hasil analisis
          )
        ),
        
        # Tombol Hitung
        fluidRow(
          column(
            12,
            div(
              style = "text-align: left; margin-top: 20px;",
              actionButton("calculate_data", "Hitung", class = "btn-primary")
            )
          )
        )
      ),
      tabItem(
        tabName = "sumber",
        fluidPage(
          # Judul halaman
          titlePanel("Tabel Sumber Data"),
          
          # Tempat untuk menampilkan tabel
          DTOutput("data_sources_table"),
          
          # Referensi tambahan
          fluidRow(
            column(
              12,
              h3("Referensi"),
              htmlOutput("references")  # Output referensi dalam format HTML
            )
          )
        )
      )
    )
  ))

# Define server logic
dashboard_server <- function(input, output, session) {
  # Subhalaman Tabel - Tabel data dengan fitur pencarian
  output$data_table <- renderDT({
    datatable(
      data, 
      filter = "top", # Fitur filter pencarian
      options = list(pageLength = 10, autoWidth = TRUE),
      rownames = FALSE
    )
  })
  
  # Subhalaman Visualisasi - Contoh plot
  output$visualisasi_plot <- renderPlot({
    ggplot(data, aes(x = Provinsi, y = Malaria)) +
      geom_bar(stat = "identity", fill = "steelblue") +
      theme_minimal() +
      labs(title = "Kasus Malaria per Provinsi", x = "Provinsi", y = "Jumlah Kasus")
  })
  
  # Subhalaman Variabel - Informasi variabel
  output$variable_info <- renderPrint({
    str(data)
  })
  
  # Render leaflet map
  output$map <- renderLeaflet({
    data$color <- with(data, ifelse(Malaria < quantile(Malaria, 0.25), "red",
                                    ifelse(Malaria > quantile(Malaria, 0.75), "green", "yellow")))
    
    leaflet(data) %>%
      addTiles() %>%
      addCircleMarkers(
        lng = ~Longitude, lat = ~Latitude,
        popup = ~paste("Provinsi:", Provinsi, "<br>Jumlah Malaria:", Malaria),
        radius = 8, color = ~color, fillOpacity = 0.7
      ) %>%
      addLegend(
        colors = c("red", "yellow", "green"), 
        labels = c("Rendah", "Sedang", "Tinggi"), 
        title = "Kategori Malaria", 
        opacity = 0.7,
        position = "bottomright"
      )
  })
  
  # Render value boxes
  # Render Total Malaria
  output$total_malaria <- renderUI({
    tags$div(
      class = "value-box-container",
      tags$div(
        class = "value-box-title", # Judul di atas kotak indikator
        "Jumlah Malaria di Indonesia"
      ),
      tags$div(
        class = "value-box-custom",
        tags$div(class = "value", formatC(sum(data$Malaria, na.rm = TRUE), format = "d", big.mark = ",")), # Angka utama
        tags$div(class = "description", "dari total 38 Provinsi") # Keterangan di kanan
      )
    )
  })
  
  
  # Render Provinsi dengan Kasus Tertinggi
  output$highest_province <- renderUI({
    max_prov <- data[which.max(data$Malaria), ]
    tags$div(
      class = "value-box-container",
      tags$div(
        class = "value-box-title", # Judul di atas kotak indikator
        "Jumlah Malaria Tertinggi"
      ),
      tags$div(
        class = "value-box-custom",
        tags$div(class = "value", formatC(max_prov$Malaria, format = "d", big.mark = ",")), # Angka utama
        tags$div(class = "description", max_prov$Provinsi) # Keterangan di kanan
      )
    )
  })
  
  
  # Render Provinsi dengan Kasus Terendah
  output$lowest_province <- renderUI({
    min_prov <- data[which.min(data$Malaria), ]
    tags$div(
      class = "value-box-container",
      tags$div(
        class = "value-box-title", # Judul di atas kotak indikator
        "Jumlah Malaria Terendah"
      ),
      tags$div(
        class = "value-box-custom",
        tags$div(class = "value", formatC(min_prov$Malaria, format = "d", big.mark = ",")), # Angka utama
        tags$div(class = "description", min_prov$Provinsi) # Keterangan di kanan
      )
    )
  })
  
  
  # Render heatmap
  output$heatmap <- renderPlot({
    matrix_data <- as.matrix(data [, 2:8])
    rownames(matrix_data) <- data$Provinsi
    
    # Menampilkan matriks
    print(matrix_data)
    
    cor_matrix <- cor(matrix_data)
    library(pheatmap)
    
    # Membuat heatmap
    library(RColorBrewer)
    pheatmap(cor_matrix, 
             color = colorRampPalette(brewer.pal(9, "BrBG"))(50) , 
             main = "Korelasi Antar Variabel",
             fontsize = 14,
             cluster_rows = TRUE,   # Menyusun baris berdasarkan kesamaan korelasi
             cluster_cols = TRUE) 
  })
  # Loop untuk semua variabel (X1, X2, X3, JP, SD, dll.)
  all_vars <- c("X1", "X2", "X3", "JP", "SD", "UNPK", "LSL", "IKK", "TBJ")
  
  lapply(all_vars, function(var) {
    
    # Provinsi dengan Nilai Tertinggi
    output[[paste0(var, "_highest")]] <- renderUI({
      max_prov <- data[which.max(data[[var]]), ]
      
      tags$div(
        class = "value-box-container",
        
        # Judul di atas kotak
        tags$div(
          class = "value-box-title", # Kelas CSS untuk judul
          paste("Provinsi dengan Nilai Tertinggi (", var, ")", sep = "") # Isi judul
        ),
        
        # Kotak indikator
        tags$div(
          class = "value-box-custom",
          tags$div(class = "value", max_prov[[var]]), # Nilai utama
          tags$div(
            class = "description", 
            max_prov$Provinsi # Deskripsi di kanan
          )
        )
      )
    })
    
    
    # Provinsi dengan Nilai Terendah
    output[[paste0(var, "_lowest")]] <- renderUI({
      min_prov <- data[which.min(data[[var]]), ]
      
      tags$div(
        class = "value-box-container",
        
        # Judul di atas kotak
        tags$div(
          class = "value-box-title", # Kelas CSS untuk judul
          paste("Provinsi dengan Nilai Terendah (", var, ")", sep = "") # Isi judul
        ),
        
        # Kotak indikator
        tags$div(
          class = "value-box-custom",
          tags$div(class = "value", min_prov[[var]]), # Nilai utama
          tags$div(
            class = "description", 
            min_prov$Provinsi # Deskripsi di kanan
          )
        )
      )
    })
    
    # Rata-rata Nilai
    output[[paste0(var, "_mean")]] <- renderUI({
      mean_value <- round(mean(data[[var]], na.rm = TRUE), 2)
      
      tags$div(
        class = "value-box-container",
        
        # Judul di atas kotak
        tags$div(
          class = "value-box-title", # Kelas CSS untuk judul
          paste("Rata-rata Nilai (", var, ")", sep = "") # Isi judul
        ),
        
        # Kotak indikator
        tags$div(
          class = "value-box-custom",
          tags$div(class = "value", mean_value), # Nilai rata-rata
          tags$div(
            class = "description",
            "Rata-rata" # Deskripsi tambahan di kanan
          )
        )
      )
    })
    
    
    # Plot Distribusi
    output[[paste0(var, "_barchart")]] <- renderPlot({
      data$category <- ifelse(data[[var]] == max(data[[var]]), "Highest", "Others")
      
      ggplot(data, aes(x = reorder(Provinsi, -data[[var]]), y = data[[var]], fill = category)) +
        geom_bar(stat = "identity", fill = "limegreen") +
        labs(
          title = "Karakteristik Jumlah Penduduk yang Memiliki KTP", 
          x = "Provinsi", 
          y = var
        ) +
        theme_minimal() +
        theme(
          axis.text.x = element_text(angle = 45, hjust = 1), # Rotasi label
          axis.text.y = element_text(size = 10),             # Ukuran label sumbu Y
          axis.title.x = element_text(size = 12),            # Ukuran teks sumbu X
          axis.title.y = element_text(size = 12),            # Ukuran teks sumbu Y
          plot.title = element_text(size = 14, hjust = 0.5)  # Ukuran dan posisi judul
        )
    })
    
    # Reactive untuk menyimpan data yang diunggah
    uploaded_data <- reactiveVal()
    
    # Proses unggah data
    observeEvent(input$file_upload, {
      req(input$file_upload)
      data <- read.xlsx(input$file_upload$datapath)
      uploaded_data(data)
      
      # Tampilkan preview data yang diunggah
      output$uploaded_preview <- renderUI({
        tags$div(
          style = "overflow-x: auto;", # Scroll horizontal jika tabel terlalu lebar
          tableOutput("uploaded_table") # Output tabel
        )
      })
      
      output$uploaded_table <- renderTable({
        head(data, n = input$n_rows) # Menampilkan n baris pertama
      })
    })
    
    
    # Tombol "Hitung" untuk melakukan prediksi
    observeEvent(input$calculate_data, {
      req(uploaded_data())  # Pastikan data telah diunggah
      
      data_upload <- uploaded_data()
      
      # Latih model GPR
      model_gpr <- vglm(Malaria~JP+SD+UNPK+LSL+IKK, family = genpoisson1, data = data)
      
      # Ambil koefisien model secara otomatis
      coef_gpr <- coef(model_gpr)
      
      # Prediksi jumlah malaria menggunakan koefisien yang sudah disimpan
      gpr_pred <- exp(
        coef_gpr["(Intercept):1"] +
          coef_gpr["JP"] * data_upload$JP +
          coef_gpr["SD"] * data_upload$SD +
          coef_gpr["UNPK"] * data_upload$UNPK +
          coef_gpr["LSL"] * data_upload$LSL +
          coef_gpr["IKK"] * data_upload$IKK
      )
      
      # Tambahkan hasil prediksi ke data
      result_data <- data_upload %>%
        mutate(Malaria_Prediction = gpr_pred)
      
      # Tampilkan hasil prediksi
      output$calculation_result <- renderUI({
        tags$div(
          style = "overflow-x: auto;", # Scroll horizontal jika tabel terlalu lebar
          tableOutput("calculation_table"), # Output tabel
          tags$p(
            "Hasil prediksi jumlah kasus malaria menggunakan model Generalized Poisson Regression.",
            style = "font-size: 18px; margin-top: 20px;" # Menambahkan gaya teks dan jarak atas
          )
        )
      })
      
      # Output tabel hasil prediksi
      output$calculation_table <- renderTable({
        result_data
      })
    })
    
    
    
    # Tombol untuk mengunduh template tabel dalam format Excel
    output$download_template <- downloadHandler(
      filename = function() { "template_data.xlsx" },
      content = function(file) {
        # Membuat data template
        template_data <- data.frame(
          Provinsi = c(
            "KEP. BANGKA BELITUNG", "DKI JAKARTA", "ACEH", "KALIMANTAN UTARA", 
            "SULAWESI BARAT", "BALI", "KEP. RIAU", "DI YOGYAKARTA", 
            "KALIMANTAN TIMUR", "SULAWESI SELATAN", "JAWA TENGAH", "GORONTALO", 
            "JAWA TIMUR", "NUSA TENGGARA TIMUR", "SULAWESI UTARA", "LAMPUNG", 
            "PAPUA", "SUMATERA BARAT", "KALIMANTAN SELATAN", "SULAWESI TENGAH", 
            "PAPUA BARAT", "RIAU", "SULAWESI TENGGARA", "SUMATERA UTARA", 
            "MALUKU", "NUSA TENGGARA BARAT", "BENGKULU", "SUMATERA SELATAN", 
            "JAMBI", "JAWA BARAT", "BANTEN", "KALIMANTAN BARAT", 
            "KALIMANTAN TENGAH", "MALUKU UTARA"
          ),
          JP = rep(0, 34),
          SD = rep(0, 34),
          UNPK = rep(0, 34),
          LSL = rep(0, 34),
          IKK = rep(0, 34),
          TBJ = rep(0, 34)
        )
        # Menulis file Excel dengan openxlsx
        write.xlsx(template_data, file)
      })
    data_sources <- data.frame(
      label = c("Y", "X1", "X2", "X3", "X4", "X5"),
      keterangan = c(
        "Jumlah kasus malaria berdasarkan provinsi pada tahun 2023",
        "Jumlah penduduk Indonesia yang memiliki KTP tahun 2023",
        "Tingkat Penyelesaian Pendidikan Jenjang Sekolah Dasar Menurut Provinsi",
        "Persentase Unmet Need Pelayanan Kesehatan Menurut Provinsi (Persen)",
        "Proporsi Rumah Tangga Yang Memiliki Akses Terhadap Layanan Sanitasi Layak (Persen)",
        "Indeks Kedalaman Kemiskinan (P1) Menurut Provinsi dan Daerah (Persen)"
      ),
      sumber = c(
        "<a href='https://www.kemkes.go.id/id/profil-kesehatan-indonesia-2023' target='_blank'>Kemkes</a>",
        "<a href='https://www.kemkes.go.id/id/profil-kesehatan-indonesia-2023' target='_blank'>Kemkes</a>",
        "<a href='https://www.bps.go.id/id/statistics-table/2/MTk4MCMy/tingkat-penyelesaian-pendidikan-menurut-jenjang-pendidikan-dan-provinsi.html' target='_blank'>BPS</a>",
        "<a href='https://www.bps.go.id/id/statistics-table/2/MTQwMiMy/unmet-need-pelayanan-kesehatan-menurut-provinsi.html' target='_blank'>BPS</a>",
        "<a href='https://www.bps.go.id/id/statistics-table/2/MTI2NyMy/proporsi-rumah-tangga-yang-memiliki-akses-terhadap-layanan-sanitasi-layak.html' target='_blank'>BPS</a>",
        "<a href='https://www.bps.go.id/id/statistics-table/2/NTAzIzI=/indeks-kedalaman-kemiskinan--p1--menurut-provinsi-dan-daerah.html' target='_blank'>BPS</a>"
      ),
      stringsAsFactors = FALSE
    )
    
    # Render data sources table
    output$data_sources_table <- renderDT({
      datatable(data_sources, escape = FALSE)  # escape = FALSE untuk menampilkan HTML (hyperlink)
    })
    
    # Referensi tambahan
    references <- "
    <ul>
      <li>Arisman, A. (2018). Determinant of Human Development Index in ASEAN Countries. <i>Signifikan: Jurnal Ilmu Ekonomi</i>.</li>
      <li>Hasanah, L., & Oktafia, R. (2024). Program penyuluhan kandungan gizi pada makanan dalam rangka peningkatan kualitas sumber daya manusia. <i>BEMAS Jurnal Bermasyarakat</i>.</li>
      <li>Mongan, J. J. (2019). Pengaruh pengeluaran pemerintah bidang pendidikan dan kesehatan terhadap indeks pembangunan manusia di Indonesia. <i>Indonesian Treasury Review: Jurnal Perbendaharaan, Keuangan Negara, dan Kebijakan Publik</i>.</li>
      <li>Putri, N. M., & Muljaningsih, S. (2022). Analisis Pengaruh Indeks Pengangguran, Indeks Pelayanan Kesehatan dan Indeks Pendidikan Terhadap Indeks Pembangunan Manusia (Ipm) di Kabupaten Bojonegoro. <i>Equity: Jurnal Ekonomi</i>.</li>
      <li>Swiyono, D., Nur, L. L., & Apriliani, A. P. (2023). Kinerja Indeks Pembangunan Manusia (IPM) (Studi Kasus di Indonesia dan Malaysia 1992 – 2021). <i>Jurnal Ekonomi Pembangunan STIE Muhammadiyah Palopo</i>.</li>
      <li>Tehupeiory, A., Sianipar, I. M., Sari, M. M., Septiariva, I. Y., Suhardono, S., & Suryawan, I. W. (2023). Estimasi Karakteristik Sosial-Ekonomi Wilayah dalam Capaian Pembangunan Berkelanjutan untuk 100% Akses Sanitasi di Provinsi Kepulauan Riau. <i>Jurnal Ilmu Lingkungan</i>.</li>
      <li>Shinta, & Manalu, H. S. (2022). Konflik Sosial dan Pengendalian Malaria Pada Masa Pandemi Covid-19 di Kabupaten Purworejo, Jawa Tengah Tahun 2021. <i>Jurnal Kesehatan Lingkungan Indonesia</i>.</li>
    </ul>
  "
    
    # Output referensi
    output$references <- renderUI({
      HTML(references)
    })
  })
}

# Run the application
shinyApp(ui = dashboard_ui, server = dashboard_server)
