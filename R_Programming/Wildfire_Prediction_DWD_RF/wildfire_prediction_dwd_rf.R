# ============================================================
# PEATLAND FIRE PREDICTION — Sumatra
# Refactored Script: DWD RBF + ASLT + Random Forest
# Scope of Work: TASK 1-3 (Preprocessing, Modelling, Evaluasi)
# ============================================================
# Paket yang digunakan:
#   kernlab  → sigest() & rbfdot() untuk kernel RBF
#   kerndwd  → Distance-Weighted Discrimination
#   ranger   → Random Forest (memory-efficient)
# ============================================================

pacman::p_load(
  ggplot2, sf, dplyr, ggspatial, viridis, readxl, readr,
  kerndwd, kernlab,          # kernlab: sigest() & rbfdot()
  forcats, svglite, mapview, scales, data.table, summarytools,
  caret, pROC, smotefamily, ranger, plotROC,
  terra, tidyterra, tictoc, DataExplorer, tidyr
)


# ============================================================
# ██████████████████████████████████████████████████████████
#                TASK 1 — FUNGSI ASLT
# ██████████████████████████████████████████████████████████
# Automatic Shifted Log Transformation
# ----------------------------------------------------------
# Formula : y = log(x + λ)
# Heuristik λ : geometric mean dari nilai positif × 10 %
#               ⇒ λ = exp(mean(log(x[x > 0]))) × 0.1
#
# Alasan pemilihan heuristik ini:
#   • Geometric mean lebih robust terhadap outlier positif
#     dibanding arithmetic mean.
#   • Faktor 0.1 menjaga λ sangat kecil sehingga tidak
#     mendistorsi distribusi asli, tetapi cukup besar untuk
#     mencegah log(0) dan menggeser massa distribusi menjauhi
#     batas bawah nol.
#   • Nilai λ dihitung HANYA dari data TRAIN, lalu di-reuse
#     pada data TEST → mencegah data leakage.
# ============================================================

apply_aslt <- function(df,
                       target_cols = NULL,   # NULL = auto-detect
                       lambda_map  = NULL,   # NULL = fase training (hitung λ)
                       verbose     = TRUE) {

  # ── Fase TRAIN: hitung λ dari data training ────────────
  if (is.null(lambda_map)) {
    lambda_map <- list()

    # Auto-detect kolom numerik dengan minimum = 0
    if (is.null(target_cols)) {
      num_cols    <- names(df)[sapply(df, is.numeric)]
      target_cols <- num_cols[sapply(df[num_cols],
                                     function(x) min(x, na.rm = TRUE) == 0)]
    }

    for (col in target_cols) {
      x_pos  <- df[[col]][df[[col]] > 0]   # hanya nilai positif
      lambda <- if (length(x_pos) > 0)
                  exp(mean(log(x_pos))) * 0.1   # geometric mean × 10%
                else
                  1e-6                           # fallback: semua nol

      lambda_map[[col]] <- lambda

      if (verbose)
        cat(sprintf("[ASLT] Kolom '%-12s' → λ = %.6f  |  formula: y = log(x + λ)\n",
                    col, lambda))
    }
  }

  # ── Terapkan transformasi (TRAIN & TEST) ───────────────
  for (col in names(lambda_map)) {
    if (col %in% names(df)) {
      lam       <- lambda_map[[col]]
      df[[col]] <- log(df[[col]] + lam)
    }
  }

  return(list(data = df, lambda_map = lambda_map))
}


# ============================================================
#                   FUNGSI EVALUASI METRIK
# ============================================================
# Menghitung Accuracy, Sensitivity, Specificity, F1, AUC
# dari vektor aktual & prediksi (karakter "0"/"1").
# ============================================================

eval_metrics <- function(aktual, prediksi, score, label = "") {
  cm   <- table(Aktual = aktual, Prediksi = prediksi)
  cat("\nConfusion Matrix [", label, "]:\n"); print(cm)

  TP <- cm["1", "1"]; TN <- cm["0", "0"]
  FP <- cm["0", "1"]; FN <- cm["1", "0"]

  acc  <- (TP + TN) / (TP + TN + FP + FN)
  sens <- TP / (TP + FN)
  spec <- TN / (TN + FP)
  prec <- TP / (TP + FP)
  f1   <- 2 * prec * sens / (prec + sens)

  roc_o <- roc(response  = as.integer(aktual),
               predictor = score,
               quiet     = TRUE)
  auc_v <- as.numeric(auc(roc_o))

  cat(sprintf("\n[%s]\n  Accuracy    = %.4f\n  Sensitivity = %.4f\n",
              label, acc, sens))
  cat(sprintf("  Specificity = %.4f\n  F1-Score    = %.4f\n  AUC         = %.4f\n",
              spec, f1, auc_v))

  return(list(
    Accuracy    = acc,
    Sensitivity = sens,
    Specificity = spec,
    F1          = f1,
    AUC         = auc_v,
    roc         = roc_o
  ))
}


# ============================================================
#               DATA UTAMA & KONSTANTA GLOBAL
# ============================================================

data_utama <- fread("hasil_filter_tanpaprov.csv")

cat("Distribusi label awal:\n")
print(table(data_utama$fire_presence))
print(prop.table(table(data_utama$fire_presence)))

# Kolom prediktor (kolom 1-9, tidak termasuk IDUNIK & fire_presence)
PREDICTOR_COLS <- names(data_utama)[1:9]

# Kolom zero-inflated yang wajib di-ASLT (curah hujan)
# — tambahkan nama kolom lain di sini jika ada
ZERO_COLS      <- c("RR_sum")

# Ukuran chunk untuk prediksi test (hemat RAM)
CHUNK_SIZE     <- 200000L


# ============================================================
# ██████████████████████████████████████████████████████████
#     TASK 2 — MODEL DWD RBF + ASLT  (Skenario 2)
# ██████████████████████████████████████████████████████████
# Pipeline:
#   Stratified Split
#   → [ASLT]          ← TASK 1, posisi KRITIS
#   → Center & Scale
#   → ADASYN + Undersample
#   → Auto-sigma (sigest)
#   → Fit DWD RBF
#   → 5-fold Company_B λ
#   → Prediksi test per 200K-chunk
#   → Evaluasi
# ============================================================

cat("\n\n══════════════════════════════════════════════\n")
cat("  SKENARIO 2: DWD RBF + ASLT\n")
cat("══════════════════════════════════════════════\n")

## ── STEP 1: Stratified Split ─────────────────────────────
set.seed(47)
idx_kelas1_all   <- which(data_utama$fire_presence == 1)
idx_kelas0_all   <- which(data_utama$fire_presence == 0)

idx_kelas1_train <- sample(idx_kelas1_all,
                            size = floor(0.8 * length(idx_kelas1_all)))
idx_kelas1_test  <- setdiff(idx_kelas1_all, idx_kelas1_train)

n_kelas0_train   <- 500000 - length(idx_kelas1_train)
idx_kelas0_train <- sample(idx_kelas0_all, size = n_kelas0_train)

idx_kelas0_test  <- setdiff(idx_kelas0_all, idx_kelas0_train)
idx_test         <- c(idx_kelas0_test, idx_kelas1_test)
idx_train        <- c(idx_kelas0_train, idx_kelas1_train)

train_data  <- data_utama[idx_train, ] |> select(-IDUNIK)
X_train_raw <- train_data[, ..PREDICTOR_COLS]
y_train_raw <- train_data$fire_presence

cat(sprintf("  Train: %d baris | Test: %d baris\n",
            nrow(train_data), length(idx_test)))


## ── STEP 2: ASLT ─────────────────────────────────────────
# ⚠️  URUTAN KRITIS: Split → ASLT → Standardisasi → ADASYN
# λ dihitung dari data TRAIN, kemudian dipakai ulang di TEST
cat("\n--- Menerapkan ASLT pada data TRAIN (DWD) ---\n")
aslt_result_dwd <- apply_aslt(X_train_raw,
                               target_cols = ZERO_COLS,
                               verbose     = TRUE)
X_train_aslt   <- aslt_result_dwd$data
lambda_map_dwd <- aslt_result_dwd$lambda_map   # ← simpan untuk TEST


## ── STEP 3: Standardisasi (center & scale) ───────────────
preproc_dwd    <- preProcess(X_train_aslt, method = c("center", "scale"))
X_train_scaled <- predict(preproc_dwd, X_train_aslt) |> as.data.frame()

cat("\nMean setelah scaling (harus ~0):\n")
print(round(colMeans(X_train_scaled), 4))
cat("SD setelah scaling (harus ~1):\n")
print(round(apply(X_train_scaled, 2, sd), 4))


## ── STEP 4: ADASYN + Undersample ─────────────────────────
cat("\nSebelum resampling:\n"); print(table(y_train_raw))

adasyn_result <- ADAS(X = X_train_scaled, target = y_train_raw, K = 5)
train_adasyn  <- adasyn_result$data

cat("\nSetelah ADASYN:\n"); print(table(train_adasyn$class))

set.seed(48)
idx_k0     <- which(train_adasyn$class == "0")
idx_k1     <- which(train_adasyn$class == "1")
n_k1       <- length(idx_k1)
idx_k0_sub <- sample(idx_k0, size = min(n_k1 * 3, length(idx_k0)))

train_balanced <- train_adasyn[c(idx_k0_sub, idx_k1), ]
set.seed(48)
train_balanced <- train_balanced[sample(nrow(train_balanced)), ]

cat("\nSetelah ADASYN + Undersample:\n")
print(table(train_balanced$class))

X_train_final <- as.matrix(train_balanced[, 1:9])
y_train_final <- ifelse(train_balanced$class == "1", 1, -1)
X_train_ref   <- X_train_final   # referensi support-vector DWD

rm(X_train_raw, train_data, X_train_aslt, X_train_scaled,
   adasyn_result, train_adasyn)
gc()


## ── STEP 5: Auto-Sigma (Median Heuristic via sigest) ─────
# sigest() dari kernlab mengestimasi rentang σ yang masuk akal.
# Kita ambil kuantil 0.5 (nilai tengah) → "median heuristic".
# Sub-sampel ≤ 10.000 baris agar tidak OOM.
cat("\nMenghitung optimal sigma untuk kernel RBF (DWD ASLT)...\n")
set.seed(50)
n_sigma_sample <- min(10000L, nrow(X_train_final))
idx_sigma      <- sample(nrow(X_train_final), n_sigma_sample)
sigma_range    <- sigest(X_train_final[idx_sigma, ],
                         frac = 0.5, scaled = FALSE)
optimal_sigma  <- sigma_range[2]   # kuantil 0.5
cat(sprintf("[RBF-ASLT] Optimal sigma (median heuristic): %.6f\n",
            optimal_sigma))


## ── STEP 5B: Sub-sampling Khusus DWD RBF (Mencegah OOM) ──
set.seed(99)
MAX_DWD_TRAIN <- 3000L
idx_fit       <- sample(1:nrow(X_train_final), min(MAX_DWD_TRAIN, nrow(X_train_final)))

X_train_dwd_fit <- X_train_final[idx_fit, ]
y_train_dwd_fit <- y_train_final[idx_fit]
X_train_ref     <- X_train_dwd_fit  # Referensi prediksi uji

## ── STEP 6: Fit DWD RBF ──────────────────────────────────
lambda_seq <- 10^(seq(-3, 1, length.out = 20))

cat("\nTraining DWD dengan kernel RBF + ASLT (Sub-sampled 15k)...\n")
tic()
dwd_model_rbf <- kerndwd(
  x      = X_train_dwd_fit,
  y      = y_train_dwd_fit,
  kern   = rbfdot(sigma = optimal_sigma),
  lambda = lambda_seq,
  qval   = 1
)
toc()

## ── STEP 7: 5-fold CV → pilih lambda optimal ─────────────
set.seed(49)
cat("\nCross-validation DWD RBF ASLT...\n")
tic()
cv_dwd_rbf <- cv.kerndwd(
  x      = X_train_dwd_fit,
  y      = y_train_dwd_fit,
  kern   = rbfdot(sigma = optimal_sigma),
  lambda = lambda_seq,
  qval   = 1,
  nfolds = 5
)
toc()

lambda_opt_idx <- which(dwd_model_rbf$lambda == cv_dwd_rbf$lambda.min)
cat(sprintf("[DWD-RBF-ASLT] Lambda optimal: %.6f (index: %d)\n",
            cv_dwd_rbf$lambda.min, lambda_opt_idx))


## ── STEP 8: Prediksi test per chunk 200K (hemat RAM) ─────
# Data test WAJIB melalui ASLT → standardisasi yang sama
# dengan TRAIN agar distribusi konsisten.
n_test                <- length(idx_test)
hasil_pred_dwd_aslt   <- vector("character", n_test)
hasil_aktual_dwd_aslt <- vector("character", n_test)
hasil_score_dwd_aslt  <- vector("numeric",   n_test)

cat(sprintf("\nPrediksi DWD-RBF+ASLT: %d baris, %d chunk...\n",
            n_test, ceiling(n_test / CHUNK_SIZE)))
tic()
for (i in seq(1, n_test, by = CHUNK_SIZE)) {
  idx_end   <- min(i + CHUNK_SIZE - 1L, n_test)
  idx_chunk <- idx_test[i:idx_end]
  chunk     <- data_utama[idx_chunk, ]

  # 1. ASLT pada chunk TEST (gunakan lambda_map dari TRAIN)
  aslt_chunk <- apply_aslt(chunk[, ..PREDICTOR_COLS],
                            lambda_map = lambda_map_dwd,
                            verbose    = FALSE)$data

  # 2. Standardisasi menggunakan preproc_dwd dari TRAIN
  X_chunk <- predict(preproc_dwd, aslt_chunk) |> as.matrix()

  # 3. Prediksi DWD
  score_raw   <- predict(dwd_model_rbf,
                          kern = rbfdot(sigma = optimal_sigma),
                          x    = X_train_ref,
                          newx = X_chunk,
                          s    = cv_dwd_rbf$lambda.min)
  score_chunk <- as.numeric(score_raw[, lambda_opt_idx])

  hasil_score_dwd_aslt[i:idx_end]  <- score_chunk
  hasil_pred_dwd_aslt[i:idx_end]   <- ifelse(score_chunk > 0, "1", "0")
  hasil_aktual_dwd_aslt[i:idx_end] <- as.character(chunk$fire_presence)

  cat(sprintf("  Chunk %d/%d → %.1f%%\n",
              ceiling(idx_end / CHUNK_SIZE),
              ceiling(n_test / CHUNK_SIZE),
              idx_end / n_test * 100))
  gc()
}
toc()


## ── STEP 9: Evaluasi ─────────────────────────────────────
metrics_dwd_rbf_aslt <- eval_metrics(
  hasil_aktual_dwd_aslt,
  hasil_pred_dwd_aslt,
  hasil_score_dwd_aslt,
  label = "DWD RBF + ASLT"
)

fwrite(data.frame(
  index    = idx_test,
  aktual   = hasil_aktual_dwd_aslt,
  prediksi = hasil_pred_dwd_aslt,
  score    = hasil_score_dwd_aslt
), "hasil_evaluasi_dwd_rbf_aslt.csv")


# ============================================================
#     SKENARIO 1 — DWD RBF + NON-ASLT (Baseline)
# ============================================================
# Pipeline identik kecuali langkah ASLT dilewati.
# Semua variabel diberi suffix _noa (No ASLT).
# ============================================================

cat("\n\n══════════════════════════════════════════════\n")
cat("  SKENARIO 1: DWD RBF + Non-ASLT\n")
cat("══════════════════════════════════════════════\n")

## ── Split ────────────────────────────────────────────────
set.seed(47)
idx_kelas1_all_noa   <- which(data_utama$fire_presence == 1)
idx_kelas0_all_noa   <- which(data_utama$fire_presence == 0)
idx_kelas1_train_noa <- sample(idx_kelas1_all_noa,
                                size = floor(0.8 * length(idx_kelas1_all_noa)))
idx_kelas1_test_noa  <- setdiff(idx_kelas1_all_noa, idx_kelas1_train_noa)
n_kelas0_train_noa   <- 500000 - length(idx_kelas1_train_noa)
idx_kelas0_train_noa <- sample(idx_kelas0_all_noa, size = n_kelas0_train_noa)
idx_kelas0_test_noa  <- setdiff(idx_kelas0_all_noa, idx_kelas0_train_noa)
idx_test_noa         <- c(idx_kelas0_test_noa, idx_kelas1_test_noa)
idx_train_noa        <- c(idx_kelas0_train_noa, idx_kelas1_train_noa)

train_data_noa  <- data_utama[idx_train_noa, ] |> select(-IDUNIK)
X_train_raw_noa <- train_data_noa[, ..PREDICTOR_COLS]
y_train_raw_noa <- train_data_noa$fire_presence

## ── Standardisasi TANPA ASLT ─────────────────────────────
preproc_dwd_noa    <- preProcess(X_train_raw_noa, method = c("center", "scale"))
X_train_scaled_noa <- predict(preproc_dwd_noa, X_train_raw_noa) |> as.data.frame()

## ── ADASYN ───────────────────────────────────────────────
adasyn_result_noa <- ADAS(X      = X_train_scaled_noa,
                           target = y_train_raw_noa, K = 5)
train_adasyn_noa  <- adasyn_result_noa$data

set.seed(48)
idx_k0_noa     <- which(train_adasyn_noa$class == "0")
idx_k1_noa     <- which(train_adasyn_noa$class == "1")
idx_k0_sub_noa <- sample(idx_k0_noa,
                          size = min(length(idx_k1_noa) * 3,
                                     length(idx_k0_noa)))
train_balanced_noa <- train_adasyn_noa[c(idx_k0_sub_noa, idx_k1_noa), ]
set.seed(48)
train_balanced_noa <- train_balanced_noa[sample(nrow(train_balanced_noa)), ]

X_train_final_noa <- as.matrix(train_balanced_noa[, 1:9])
y_train_final_noa <- ifelse(train_balanced_noa$class == "1", 1, -1)
X_train_ref_noa   <- X_train_final_noa

rm(X_train_raw_noa, train_data_noa, X_train_scaled_noa,
   adasyn_result_noa, train_adasyn_noa)
gc()

## ── Auto-Sigma Non-ASLT ───────────────────────────────────
cat("\nMenghitung optimal sigma (Non-ASLT)...\n")
set.seed(50)
n_sigma_sample_noa <- min(10000L, nrow(X_train_final_noa))
idx_sigma_noa      <- sample(nrow(X_train_final_noa), n_sigma_sample_noa)
sigma_range_noa    <- sigest(X_train_final_noa[idx_sigma_noa, ],
                              frac = 0.5, scaled = FALSE)
optimal_sigma_noa  <- sigma_range_noa[2]
cat(sprintf("[RBF-Non-ASLT] Optimal sigma: %.6f\n", optimal_sigma_noa))

## ── Sub-sampling Non-ASLT (Mencegah OOM) ─────────────────
set.seed(99)
MAX_DWD_TRAIN_NOA <- 3000L
idx_fit_noa       <- sample(1:nrow(X_train_final_noa), min(MAX_DWD_TRAIN_NOA, nrow(X_train_final_noa)))

X_train_dwd_fit_noa <- X_train_final_noa[idx_fit_noa, ]
y_train_dwd_fit_noa <- y_train_final_noa[idx_fit_noa]
X_train_ref_noa     <- X_train_dwd_fit_noa

## ── Fit DWD Non-ASLT ─────────────────────────────────────
cat("\nTraining DWD RBF Non-ASLT (Sub-sampled 15k)...\n")
tic()
dwd_model_rbf_noa <- kerndwd(
  x      = X_train_dwd_fit_noa,
  y      = y_train_dwd_fit_noa,
  kern   = rbfdot(sigma = optimal_sigma_noa),
  lambda = lambda_seq,
  qval   = 1
)
toc()

set.seed(49)
cv_dwd_rbf_noa <- cv.kerndwd(
  x      = X_train_dwd_fit_noa,
  y      = y_train_dwd_fit_noa,
  kern   = rbfdot(sigma = optimal_sigma_noa),
  lambda = lambda_seq,
  qval   = 1,
  nfolds = 5
)
lambda_opt_idx_noa <- which(dwd_model_rbf_noa$lambda == cv_dwd_rbf_noa$lambda.min)

## ── Prediksi Non-ASLT per chunk ───────────────────────────
n_test_noa       <- length(idx_test_noa)
hasil_pred_noa   <- vector("character", n_test_noa)
hasil_aktual_noa <- vector("character", n_test_noa)
hasil_score_noa  <- vector("numeric",   n_test_noa)

cat(sprintf("\nPrediksi DWD-RBF Non-ASLT: %d chunk...\n",
            ceiling(n_test_noa / CHUNK_SIZE)))
tic()
for (i in seq(1, n_test_noa, by = CHUNK_SIZE)) {
  idx_end   <- min(i + CHUNK_SIZE - 1L, n_test_noa)
  idx_chunk <- idx_test_noa[i:idx_end]
  chunk     <- data_utama[idx_chunk, ]
  X_chunk   <- predict(preproc_dwd_noa,
                        chunk[, ..PREDICTOR_COLS]) |> as.matrix()

  score_raw   <- predict(dwd_model_rbf_noa,
                          kern = rbfdot(sigma = optimal_sigma_noa),
                          x    = X_train_ref_noa,
                          newx = X_chunk,
                          s    = cv_dwd_rbf_noa$lambda.min)
  score_chunk <- as.numeric(score_raw[, lambda_opt_idx_noa])

  hasil_score_noa[i:idx_end]  <- score_chunk
  hasil_pred_noa[i:idx_end]   <- ifelse(score_chunk > 0, "1", "0")
  hasil_aktual_noa[i:idx_end] <- as.character(chunk$fire_presence)
  cat(sprintf("  Progress (Non-ASLT): %.1f%%\n", idx_end / n_test_noa * 100))
  gc()
}
toc()

metrics_dwd_rbf_noa <- eval_metrics(
  hasil_aktual_noa, hasil_pred_noa, hasil_score_noa,
  label = "DWD RBF + Non-ASLT"
)

fwrite(data.frame(
  index    = idx_test_noa,
  aktual   = hasil_aktual_noa,
  prediksi = hasil_pred_noa,
  score    = hasil_score_noa
), "hasil_evaluasi_dwd_rbf_noa.csv")


# ============================================================
# ██████████████████████████████████████████████████████████
#     SKENARIO 3 & 4 — RANDOM FOREST (Non-ASLT & ASLT)
# ██████████████████████████████████████████████████████████
# Helper function run_rf_pipeline() menjalankan seluruh
# pipeline RF untuk kedua skenario sekaligus.
# ============================================================

# Konversi target ke character untuk ranger
data_utama$fire_presence <- as.character(data_utama$fire_presence)

run_rf_pipeline <- function(seed_split,
                             seed_adasyn,
                             use_aslt   = FALSE,
                             zero_cols  = NULL,
                             label_tag  = "") {

  cat(sprintf("\n\n══════════════════════════════════════════════\n"))
  cat(sprintf("  SKENARIO RF: %s\n", label_tag))
  cat(sprintf("══════════════════════════════════════════════\n"))

  ## ── Split ──────────────────────────────────────────────
  set.seed(seed_split)
  idx1_all   <- which(data_utama$fire_presence == "1")
  idx0_all   <- which(data_utama$fire_presence == "0")
  idx1_train <- sample(idx1_all, size = floor(0.8 * length(idx1_all)))
  idx1_test  <- setdiff(idx1_all, idx1_train)
  n0_train   <- 500000 - length(idx1_train)
  idx0_train <- sample(idx0_all, size = n0_train)
  idx0_test  <- setdiff(idx0_all, idx0_train)
  idx_t      <- c(idx0_test,  idx1_test)
  idx_tr     <- c(idx0_train, idx1_train)

  cat(sprintf("  Train: %d | Test: %d\n", length(idx_tr), length(idx_t)))

  train_data <- data_utama[idx_tr, ] |> select(-IDUNIK)
  X_raw      <- train_data[, ..PREDICTOR_COLS]
  y_raw      <- train_data$fire_presence

  ## ── ASLT (opsional) ────────────────────────────────────
  lambda_map_rf <- NULL
  if (use_aslt) {
    cat(sprintf("\n--- ASLT pada RF [%s] ---\n", label_tag))
    aslt_out      <- apply_aslt(X_raw,
                                 target_cols = zero_cols,
                                 verbose     = TRUE)
    X_raw         <- aslt_out$data
    lambda_map_rf <- aslt_out$lambda_map
  }

  ## ── Standardisasi ──────────────────────────────────────
  preproc_rf <- preProcess(X_raw, method = c("center", "scale"))
  X_scaled   <- predict(preproc_rf, X_raw) |> as.data.frame()

  ## ── ADASYN + Undersample ───────────────────────────────
  adasyn_res <- ADAS(X = X_scaled, target = as.character(y_raw), K = 5)
  tr_ada     <- adasyn_res$data

  set.seed(seed_adasyn)
  ik0     <- which(tr_ada$class == "0")
  ik1     <- which(tr_ada$class == "1")
  ik0_sub <- sample(ik0, size = min(length(ik1) * 3, length(ik0)))
  tr_bal  <- tr_ada[c(ik0_sub, ik1), ]
  set.seed(seed_adasyn)
  tr_bal  <- tr_bal[sample(nrow(tr_bal)), ]

  X_fin  <- tr_bal[, 1:9]
  y_fin  <- factor(tr_bal$class)
  tr_fin <- cbind(X_fin, label = y_fin)

  cat("\nSetelah ADASYN + Undersample:\n")
  print(table(tr_fin$label))

  ## ── Class Weight ───────────────────────────────────────
  n_tot <- nrow(tr_fin)
  n_0   <- sum(tr_fin$label == "0")
  n_1   <- sum(tr_fin$label == "1")
  cw    <- ifelse(tr_fin$label == "1",
                  n_tot / (2 * n_1),   # bobot tinggi (minoritas)
                  n_tot / (2 * n_0))   # bobot rendah (mayoritas)

  cat(sprintf("  Weight kelas 0: %.4f | Weight kelas 1: %.4f\n",
              n_tot / (2 * n_0), n_tot / (2 * n_1)))

  rm(X_raw, train_data, X_scaled, adasyn_res, tr_ada, X_fin, y_fin)
  gc()

  ## ── Training Random Forest ─────────────────────────────
  cat(sprintf("\nTraining Random Forest [%s]...\n", label_tag))
  set.seed(seed_adasyn)
  tic()
  rf_mod <- ranger(
    label ~ .,
    data          = tr_fin,
    num.trees     = 500,
    mtry          = 3,
    min.node.size = 10,
    importance    = "impurity",
    probability   = TRUE,
    case.weights  = cw,
    num.threads   = parallel::detectCores() - 1,
    seed          = 42
  )
  toc()

  rm(tr_fin, cw); gc()

  ## ── Feature Importance ─────────────────────────────────
  imp <- data.frame(
    Variabel   = names(rf_mod$variable.importance),
    Importance = rf_mod$variable.importance
  ) |> dplyr::arrange(desc(Importance))
  cat("\nFeature Importance:\n"); print(imp)

  ## ── Prediksi Test per Chunk 200K ───────────────────────
  n_test_rf <- length(idx_t)
  hp        <- vector("character", n_test_rf)
  ha        <- vector("character", n_test_rf)
  hs        <- vector("numeric",   n_test_rf)

  cat(sprintf("\nPrediksi RF [%s]: %d baris, %d chunk...\n",
              label_tag, n_test_rf, ceiling(n_test_rf / CHUNK_SIZE)))
  tic()
  for (i in seq(1, n_test_rf, by = CHUNK_SIZE)) {
    ie  <- min(i + CHUNK_SIZE - 1L, n_test_rf)
    ic  <- idx_t[i:ie]
    ch  <- data_utama[ic, ]

    # ASLT pada chunk TEST jika mode ASLT aktif
    ch_x <- if (use_aslt) {
      aslt_ch <- apply_aslt(ch[, ..PREDICTOR_COLS],
                             lambda_map = lambda_map_rf,
                             verbose    = FALSE)$data
      predict(preproc_rf, aslt_ch) |> as.data.frame()
    } else {
      predict(preproc_rf, ch[, ..PREDICTOR_COLS]) |> as.data.frame()
    }

    pr        <- predict(rf_mod, data = ch_x)
    sc        <- as.numeric(pr$predictions[, "1"])
    hs[i:ie]  <- sc
    ha[i:ie]  <- as.character(ch$fire_presence)
    cat(sprintf("  [%s] Progress: %.1f%%\n", label_tag, ie / n_test_rf * 100))
    gc()
  }
  toc()

  ## ── Tuning Threshold (max F1) ──────────────────────────
  cat("\nMencari threshold optimal (F1 maximum)...\n")
  thrs <- seq(0.01, 0.99, by = 0.01)
  f1s  <- sapply(thrs, function(thr) {
    pp   <- ifelse(hs >= thr, "1", "0")
    TP_  <- sum(pp == "1" & ha == "1")
    FP_  <- sum(pp == "1" & ha == "0")
    FN_  <- sum(pp == "0" & ha == "1")
    pr_  <- ifelse((TP_ + FP_) > 0, TP_ / (TP_ + FP_), 0)
    rc_  <- ifelse((TP_ + FN_) > 0, TP_ / (TP_ + FN_), 0)
    ifelse((pr_ + rc_) > 0, 2 * pr_ * rc_ / (pr_ + rc_), 0)
  })
  best_thr_rf <- thrs[which.max(f1s)]
  hp          <- ifelse(hs >= best_thr_rf, "1", "0")
  cat(sprintf("[RF %s] Best threshold (F1): %.2f\n", label_tag, best_thr_rf))

  ## ── Evaluasi ───────────────────────────────────────────
  metrics <- eval_metrics(ha, hp, hs,
                           label = paste0("RF ", label_tag))

  ## ── Simpan CSV ─────────────────────────────────────────
  fwrite(
    data.frame(aktual = ha, prediksi = hp, score = hs),
    paste0("hasil_evaluasi_rf_", tolower(gsub(" ", "_", label_tag)), ".csv")
  )

  return(list(
    metrics    = metrics,
    model      = rf_mod,
    importance = imp,
    threshold  = best_thr_rf,
    preproc    = preproc_rf,
    lambda_map = lambda_map_rf,
    idx_test   = idx_t,
    aktual     = ha,
    pred       = hp,
    score      = hs
  ))
}


## ── Jalankan Skenario 3: RF Non-ASLT ─────────────────────
rf_non_aslt <- run_rf_pipeline(
  seed_split = 87,
  seed_adasyn = 88,
  use_aslt    = FALSE,
  label_tag   = "Non-ASLT"
)

## ── Jalankan Skenario 4: RF + ASLT ───────────────────────
rf_aslt <- run_rf_pipeline(
  seed_split  = 87,
  seed_adasyn = 88,
  use_aslt    = TRUE,
  zero_cols   = ZERO_COLS,
  label_tag   = "ASLT"
)


# ============================================================
# ██████████████████████████████████████████████████████████
#   TASK 3 — TABEL PERBANDINGAN 4-WAY
# ██████████████████████████████████████████████████████████
# Metrics: Accuracy, Sensitivity, Specificity, F1-Score, AUC
# Skenario:
#   1. DWD RBF + Non-ASLT
#   2. DWD RBF + ASLT
#   3. Random Forest + Non-ASLT
#   4. Random Forest + ASLT
# ============================================================

buat_baris <- function(m, nama) {
  data.frame(
    Model       = nama,
    Accuracy    = round(m$Accuracy,    4),
    Sensitivity = round(m$Sensitivity, 4),
    Specificity = round(m$Specificity, 4),
    F1_Score    = round(m$F1,          4),
    AUC         = round(m$AUC,         4),
    stringsAsFactors = FALSE
  )
}

tabel_perbandingan <- rbind(
  buat_baris(metrics_dwd_rbf_noa,   "DWD RBF + Non-ASLT"),
  buat_baris(metrics_dwd_rbf_aslt,  "DWD RBF + ASLT"),
  buat_baris(rf_non_aslt$metrics,   "Random Forest + Non-ASLT"),
  buat_baris(rf_aslt$metrics,       "Random Forest + ASLT")
)

cat("\n\n╔════════════════════════════════════════════════════════════╗\n")
cat("║          TABEL PERBANDINGAN METRIK — 4 SKENARIO            ║\n")
cat("╠════════════════════════════════════════════════════════════╣\n")
print(tabel_perbandingan, row.names = FALSE)
cat("╚════════════════════════════════════════════════════════════╝\n\n")

fwrite(tabel_perbandingan, "tabel_perbandingan_4_skenario.csv")

## ── Barplot Perbandingan ──────────────────────────────────
tabel_long <- tabel_perbandingan |>
  pivot_longer(cols = -Model, names_to = "Metrik", values_to = "Nilai") |>
  mutate(
    Metrik = factor(Metrik,
                    levels = c("Accuracy", "Sensitivity", "Specificity",
                               "F1_Score", "AUC")),
    Model  = factor(Model,
                    levels = c("DWD RBF + Non-ASLT",
                               "DWD RBF + ASLT",
                               "Random Forest + Non-ASLT",
                               "Random Forest + ASLT"))
  )

p_comp <- ggplot(tabel_long, aes(x = Model, y = Nilai, fill = Model)) +
  geom_col(width = 0.65, show.legend = FALSE) +
  geom_text(aes(label = scales::percent(Nilai, accuracy = 0.01)),
            vjust = -0.4, size = 3.2, fontface = "bold") +
  facet_wrap(~Metrik, scales = "free_y", ncol = 3) +
  scale_fill_manual(values = c("#264653", "#2A9D8F", "#E9C46A", "#E76F51")) +
  scale_y_continuous(labels  = scales::percent_format(accuracy = 1),
                     expand  = expansion(mult = c(0, 0.18))) +
  scale_x_discrete(guide = guide_axis(angle = 30)) +
  labs(
    title    = "Perbandingan Metrik 4 Skenario Model",
    subtitle = "DWD RBF vs Random Forest × ASLT vs Non-ASLT",
    x = NULL, y = "Nilai"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    strip.text         = element_text(face = "bold", size = 11),
    strip.background   = element_rect(fill = "#f0f0f0", color = NA),
    plot.title         = element_text(face = "bold", size = 14),
    plot.subtitle      = element_text(color = "grey40"),
    panel.grid.major.x = element_blank()
  )

ggsave("barplot_perbandingan_4_skenario.png", p_comp,
       width = 14, height = 9, dpi = 300, bg = "white")


# ============================================================
#               SIMPAN SEMUA MODEL & ARTEFAK
# ============================================================

## DWD RBF + ASLT
saveRDS(dwd_model_rbf,  "dwd_rbf_aslt_model.rds")
saveRDS(cv_dwd_rbf,     "dwd_rbf_aslt_cv.rds")
saveRDS(preproc_dwd,    "dwd_rbf_aslt_preproc.rds")
saveRDS(lambda_map_dwd, "dwd_rbf_aslt_lambda_map.rds")
saveRDS(optimal_sigma,  "dwd_rbf_aslt_sigma.rds")

## DWD RBF + Non-ASLT
saveRDS(dwd_model_rbf_noa, "dwd_rbf_noa_model.rds")
saveRDS(cv_dwd_rbf_noa,    "dwd_rbf_noa_cv.rds")
saveRDS(preproc_dwd_noa,   "dwd_rbf_noa_preproc.rds")
saveRDS(optimal_sigma_noa, "dwd_rbf_noa_sigma.rds")

## RF
saveRDS(rf_non_aslt$model,     "rf_noa_model.rds")
saveRDS(rf_non_aslt$preproc,   "rf_noa_preproc.rds")
saveRDS(rf_non_aslt$threshold, "rf_noa_threshold.rds")
saveRDS(rf_aslt$model,         "rf_aslt_model.rds")
saveRDS(rf_aslt$preproc,       "rf_aslt_preproc.rds")
saveRDS(rf_aslt$lambda_map,    "rf_aslt_lambda_map.rds")
saveRDS(rf_aslt$threshold,     "rf_aslt_threshold.rds")

cat("\n✔ Semua model dan artefak berhasil disimpan.\n")
