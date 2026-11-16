# Integrated DECIDE Decision Cockpit
**Dynamic Demand to Production Decision System** — TI4001 Proyek Rekayasa Inter-Disiplin ITB, Kelompok 39.

Satu aplikasi Streamlit, tiga role (PPC / Production Planner, Supply Planner, Leader Produksi), delapan halaman H01–H08, menjalankan proses TO-BE (CFD langkah 1–19) secara end-to-end.

> Data simulasi · Tidak terhubung SAP. Struktur dan angka acuan mengikuti dokumen tugas; konteks pasar (posisi merek, harga ritel, kalender campaign) dikalibrasi dengan referensi publik — lihat bagian 10.

---

## 1. Instalasi & menjalankan
```bash
pip install -r requirements.txt
streamlit run app.py
python -m pytest tests -v          # 21 test (TC01–TC19 + 2 kalibrasi)
```

## 2. Hasil audit codebase (sebelum perubahan)
| Kategori | Fitur |
|---|---|
| **A. Implemented & berfungsi (dipertahankan)** | Buffer/ROP engine, AHP + consistency test, P1/P2/P3, MRP material, cek kapasitas, sequencing rule 1–3, ETA engine, KPI, styling Poppins, process tracker, kontrol dokumen, sasaran mutu, NC/CAPA, navigasi sidebar + Select Role |
| **B. UI ada, logic belum tersambung** | Supply Planner hanya memberi feedback teks (tidak memengaruhi gate) · H05 tanpa aksi review PPC · HOLD tidak terhubung ke H06 · "Use Selected Scenario" tidak menyimpan schedule aktif · approval memakai status string sederhana · rilis tanpa langkah eksekusi · H08 hanya KPI rencana · replanning hanya navigasi |
| **C. Belum ada** | Mulai siklus + validasi data (langkah 2–3) · konfirmasi pasokan awal Available/Partial/Not Available (7) · status machine terpusat · eksekusi simulasi & hasil aktual (16–17) · plan vs actual (18) · siklus/revisi baru + arsip (19) · audit trail lengkap |

## 3. File yang diubah / ditambah
| File | Perubahan |
|---|---|
| `engine/workflow_engine.py` | **baru** — state machine terpusat, audit trail, arsip, panduan langkah berikutnya (menggantikan `approval_engine.py`) |
| `engine/actual_engine.py` | **baru** — hasil aktual deterministik, KPI aktual, plan vs actual |
| `engine/feasibility_engine.py` | konfirmasi pasokan awal ikut menentukan gate; alasan HOLD "Material shortage — …" / "Capacity unavailable — …"; kolom `Hold_Type` |
| `engine/scenario_engine.py` | meneruskan `supply_confirmation` ke gate |
| `engine/quality_engine.py` | trigger replanning 6 jenis (termasuk data aktual); NC dari hasil aktual |
| `utils/state.py` | state terpusat, mirror variabel sesi, akses role sesuai UI Tree, helper transisi |
| `utils/styles.py` | kartu "langkah berikutnya", banner simulasi SAP, badge status baru |
| `app.py` | sidebar siklus/revisi, kartu langkah berikutnya |
| `views/overview.py` | panel langkah 1–3 + tombol Mulai Siklus; sumber data |
| `views/feasibility.py` | stepper 6–8 + Gate, editor konfirmasi pasokan awal, tombol eskalasi HOLD → H06 |
| `views/sequencing.py` | panel PPC Review: Accept Proposed Plan / Evaluate with What-if |
| `views/scenario.py` | Run Scenario tercatat, KPI Comparison (8 KPI + delta), Schedule Comparison, Use Selected Scenario, preset demo, Leader read-only |
| `views/approval.py` | langkah 13–17, lembar pengesahan, audit trail lengkap, arsip |
| `views/monitoring.py` | KPI aktual (8), plan vs actual, baseline vs approved, Start Replanning |
| `scripts/generate_data.py`, `data/supplier.csv` | label data simulasi, nama supplier netral |
| `tests/test_engine.py` | TC01–TC19 |

Tidak diubah: formula Buffer/ROP, metode AHP & bobot, aturan P1/P2/P3, rule sequencing, ETA engine, nama halaman H01–H08, styling.

## 4. State variable (session_state)
| Variabel | Isi |
|---|---|
| `workflow` | dict tunggal sumber kebenaran: `status`, `cycle`, `revision`, `revision_events`, `initial_supply`, `active_*`, `material_final`, `leader_decision`, `supply_feedback`, `execution_status`, `actual`, `actual_kpi`, `history`, `archive` |
| `active_scenario` · `active_schedule` · `active_revision` · `execution_status` · `workflow_status` | mirror dari `workflow` (dibaca lintas halaman) |
| `params_baseline` · `params_alt` · `alt_ran` | parameter skenario What-if |
| `role` · `nav` · `flash` | role aktif, halaman, notifikasi |

## 5. Workflow status
`DRAFT → FEASIBILITY_CHECK → (HOLD | PLAN_REVIEW) → SCENARIO_REVIEW → MATERIAL_FINAL_CONFIRMATION → MATERIAL_FINAL_CONFIRMED → APPROVED → READY_FOR_SAP_RELEASE → RELEASED_SIMULATION → (MONITORING | REPLANNING_REQUIRED) → SCENARIO_REVIEW (siklus baru)`

Cabang revisi: `MATERIAL_FINAL_CONFIRMATION` atau `MATERIAL_FINAL_CONFIRMED` → `REVISION_REQUIRED` → H06 → ajukan ulang. Setiap revisi menaikkan nomor revisi dokumen; replanning menaikkan siklus + revisi dan mengarsipkan rencana lama.

| Role | Aksi yang tampil |
|---|---|
| PPC | Mulai siklus, Eskalasi HOLD, Accept Proposed Plan, Evaluate with What-if, Run Scenario, Use Selected Scenario, Release Final Schedule, Simpan & Eksekusi, Update Hasil Aktual, Start Replanning |
| Supply Planner | Konfirmasi Pasokan Awal, Confirm Final Material, Need Revision |
| Leader Produksi | Approve Schedule, Request Revision (H06 hanya lihat) |

## 6. Test case (black-box sesuai CFD)
| TC | Skenario | Hasil |
|---|---|---|
| 01 | Data valid → lanjut ke Buffer/ROP | PASS |
| 02 | Field wajib hilang → siklus tidak bisa dimulai | PASS |
| 03 | NIP > ROP → tidak direkomendasikan | PASS |
| 04 | NIP ≤ ROP → qty rekomendasi muncul | PASS |
| 05 | Material shortage → HOLD | PASS |
| 06 | Kapasitas tidak cukup → HOLD | PASS |
| 07 | SKU HOLD tidak masuk H05 | PASS |
| 08 | SKU LAYAK masuk H05 | PASS |
| 09 | P1 didahulukan | PASS |
| 10 | PPC Run What-if → hasil berubah; Leader ditolak | PASS |
| 11 | Use Selected Scenario → H07 memakai schedule skenario | PASS |
| 12 | Leader tidak bisa approve sebelum material final | PASS |
| 13 | Supply Need Revision (4 field wajib) → kembali ke H06 | PASS |
| 14 | Leader Request Revision → H06, revisi bertambah | PASS |
| 15 | Leader approve → PPC bisa release | PASS |
| 16 | Release + eksekusi → RELEASED_SIMULATION | PASS |
| 17 | Plan & actual tersimpan terpisah | PASS |
| 18 | Plan vs actual + deviasi | PASS |
| 19 | Replanning → siklus/revisi baru, histori & arsip utuh | PASS |

## 7. Demo end-to-end (tanpa edit kode)
Kartu **"Giliran Anda / Menunggu …"** di atas setiap halaman menunjukkan role dan halaman berikutnya.

1. **PPC · H01** — lihat KPI (8 SKU Risk), klik **Mulai Siklus Perencanaan** (validasi data).
2. **PPC · H02/H03** — buffer zone, ranking AHP, P1/P2/P3.
3. **Supply Planner · H04** — klik **Konfirmasi Pasokan Awal** → gate: 6 LAYAK, **2 HOLD** (BB-002 tube, SS-005 botol pump).
4. **PPC · H04** — klik **Eskalasi HOLD → H06**.
5. **PPC · H06** — preset **Perbaikan HOLD (demo)** (qty BB-002 85.000 → 72.000, material 110%, ETA supplier −7 hari, kapasitas 120%) → **Run Scenario** → HOLD 2 → 0, LAYAK 6 → 8, stockout risk 4 → 3, sequence berubah.
6. **PPC · H06** — pilih *Alternative* → **Use Selected Scenario**.
7. **Supply Planner · H07** — **Confirm Final Material** (atau *Need Revision* untuk demo cabang revisi).
8. **Leader Produksi · H07** — **Approve Schedule**.
9. **PPC · H07** — **Release Final Schedule** → banner *SIMULATION ONLY — No real SAP transaction executed* → **Simpan & Eksekusi** → **Update Hasil Aktual**.
10. **PPC · H08** — plan vs actual (qty achievement ±97%, 2 isu material, adherence), baseline vs approved, NC → **REPLANNING REQUIRED** → **Start Replanning** (siklus C02, rencana lama diarsipkan, audit trail utuh).

## 8. Limitation
- Eksekusi, rilis SAP, dan hasil aktual adalah simulasi deterministik.
- State tersimpan di sesi browser; refresh / restart server mengulang siklus.
- Satu line liquid; konfirmasi pasokan per material, bukan per pengiriman.
- Login hanya pemilih role; tidak ada autentikasi.

## 9. Known issues
- Pada skenario demo, jumlah order terlambat naik 2 → 3: SS-005 (P1) yang tadinya HOLD kini diproduksi tetapi stoknya habis sebelum waktu minimum QC + distribusi (2 hari kerja). Ini keterbatasan struktural, bukan bug; mitigasinya di luar parameter What-if (transfer stok antar-DC / QC express).
- Grafik Altair belum diverifikasi visual di lingkungan pengembang; logika dan tabel sudah diuji.
- Arsip rencana tidak dapat dipulihkan menjadi rencana aktif (hanya dilihat).

## 10. Sumber & kalibrasi data
- Struktur dataset, posisi stok, ROP, qty rekomendasi, bobot AHP: dokumen tugas TI4001 Kelompok 39.
- Wardah merek BB cream terpopuler 2026 (Top Brand Index 29,3%): GoodStats.
- Harga ritel BB cream/BB tint Wardah ±Rp30–39 ribu: Female Daily, Medicastore.
- Harbolnas 2026: 10–16 Desember (12.12 hari Sabtu); periode 11.11 berbeda per platform: Journal Arta.
- Demand mingguan, BOM, material, supplier, kapasitas: data simulasi yang dikalibrasi ke angka di atas.
