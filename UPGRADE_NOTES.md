# EKSPERIMEN_16 v6.0 — Protocol Upgrade Notes

## Perubahan dari v5.2 ke v6.0

### Backend (`backend/app.py`)

#### NEW: ManeuverQueue (§7.5.1 Pencegahan Deadlock)
- Kelas baru `ManeuverQueue` memastikan tidak ada dua manuver yang menggunakan platoon yang sama secara bersamaan
- Implementasi Teorema 4.1 (Isolasi Transfer): `{P_src, P_dst} ∩ {P_src2, P_dst2} = ∅`
- Lock berbasis `threading.Lock()` dengan `try_acquire()` dan `release()`

#### NEW: FSM TRANSFER State (§3.4)
- State TRANSFER ditambah ke `VehicleFSM` (selain CACC, DEGRADED, ACC, EMERGENCY)
- Aktif ketika `transfer_cooldown > 0` pada kendaraan bukan leader
- Headway multiplier: `h_TRANSFER = 1.5 × h_normal` (Proposisi 8.1, §8.6)

#### NEW: Precondition Validation (§4.2, §6.3, §5.4)
- `validate_transfer()`: cek C1–C6
- `validate_swap()`: cek S1–S6 termasuk beda kecepatan < 5 m/s (S6)
- `validate_promote()`: cek Proposisi 5.1
- REST API: `POST /api/validate_maneuver`
- Socket event: `validate_maneuver` → `maneuver_validation`

#### NEW: Emergency Leader Promotion (§5.5, Algorithm 2)
- `_check_emergency_promotion()` berjalan setiap step
- Trigger: AoI kendaraan kedua (V1) ≥ 500ms
- Otomatis promosi V1 menjadi leader darurat dengan cooldown 3s
- Emit socket event: `emergency_promotion`

#### IMPROVED: swap_leaders() (§6)
- Validasi S1–S6 sebelum eksekusi
- Cek kecepatan kompatibel: |v_A - v_B| < 5 m/s (S6)
- ManeuverQueue integration
- Phase logging: `'phase': 'COMPLETE'`
- Return: `vel_diff_ms` untuk monitoring

#### IMPROVED: promote_next_leader() (§5)
- Validasi Proposisi 5.1
- Algorithm 1: reset integral semua member di belakang
- ManeuverQueue integration
- Phase logging

#### IMPROVED: transfer_vehicle() (§4)
- Validasi C1–C6
- Algorithm 1: reset integral kendaraan yang tertinggal (§4.5)
- ManeuverQueue integration (Teorema 4.1)
- Eq. 19: `x_k_new = x_tail - L_tail - d_ref_k - g_safety`
- Phase logging dengan `tail_vehicle` info

#### IMPROVED: _pid_ff_control() (§8.6)
- Headway boost 1.5× saat cooldown aktif (Proposisi 8.1)
- `h_maneuver = 1.5 * h_normal` selama periode stabilisasi

#### IMPROVED: to_dict() (§9.2)
- Field baru: `transfer_cooldown` (detik tersisa)
- FSM state dilaporkan sebagai 'TRANSFER' saat cooldown > 0

#### IMPROVED: get_platoon_info()
- Field baru: `avg_speed_kmh`, `in_maneuver`, `leader_velocity`
- Setiap vehicle: `transfer_cooldown`, `aoi_ms`, `spacing_error`, `reported_state`

#### IMPROVED: step()
- Memanggil `_check_emergency_promotion()` setiap step
- State update menyertakan `maneuver_queue` status

#### NEW APIs
- `POST /api/validate_maneuver` — validasi prasyarat sebelum eksekusi
- `GET /api/maneuver_queue_status` — status ManeuverQueue
- Socket: `validate_maneuver` → `maneuver_validation`

### Frontend (`frontend/simulation.html`)

#### NEW: ManeuverQueue Status Panel
- Badge real-time: "Bebas" (hijau) atau "Manuver Aktif: Pn" (merah)
- Referensi Teorema 4.1 ditampilkan saat queue busy

#### NEW: TRANSFER State Display
- Badge biru muda `TRANSFER` untuk kendaraan dalam cooldown
- Cooldown progress bar + timer ("⏱ Cooldown 1.8s (h=1.5×normal)")
- CSS class `.transfer-mode` pada vehicle card

#### NEW: Real-Time Precondition Validation
- Setiap dropdown selection memicu socket `validate_maneuver`
- Display precondition result: ✓ hijau (OK) atau ✗ merah (error)
- Swap: tampilan kecepatan A/B + beda kecepatan dengan warna risk indicator

#### NEW: Protocol FSM Visualizer Panel
- Menampilkan distribusi state FSM per platoon
- Tooltip cooldown per kendaraan
- Badge "⚡ Manuver Aktif" saat platoon dalam antrian

#### NEW: Emergency Promotion Alert
- Fixed-position toast notification saat emergency promotion terjadi
- Auto-dismiss setelah 5 detik

#### IMPROVED: Platoon Status List
- Menampilkan cooldown timer per kendaraan
- AoI per kendaraan
- Kecepatan rata-rata per platoon
- Warna border merah saat platoon dalam manuver

#### IMPROVED: Maneuver Log
- Timestamp pada setiap log entry
- Phase tracking (§COMPLETE, §EMERGENCY)
- Referensi protokol (§4, §5, §6, §5.5)
- Vehicle ID info lebih detail

#### IMPROVED: Dropdown Transfer
- Kendaraan dengan cooldown aktif di-disable
- Label menampilkan cooldown tersisa

## Referensi Dokumen Protokol
- §4: Protokol Transfer Anggota Antar-Platoon
- §5: Protokol Promosi Leader Intra-Platoon
- §5.5: Promosi Darurat (Algorithm 2)
- §6: Protokol Pertukaran Leader Antar-Platoon
- §7.5: Sinkronisasi Multi-Platoon & Pencegahan Deadlock
- §8.6: String Stability Selama Manuver (Proposisi 8.1)
- §4.5: Konsistensi Predecessor (Algorithm 1)
- Teorema 4.1: Isolasi Transfer
- Proposisi 5.1: Keamanan Promosi Leader
- Kondisi S1–S6: Prasyarat Swap Leader
- Kondisi C1–C6: Prasyarat Transfer Anggota
