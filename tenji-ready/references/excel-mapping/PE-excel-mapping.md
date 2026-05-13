# Pump Express (PE) — TenJI Excel Mapping

來源基底：`/home/user/.openclaw/shared-knowledge/protocol/official/PE.md`
真實性：`verified-official`
用途：把 PE 1.0 / 2.0 測試欄位版轉成可直接落到 TenJI Test Note（B~N 欄）的 mapping。

## Mapping 原則
- 採 TenJI 固定欄位 `B~N`。
- PE 1.0 / 2.0 核心不是 D+/D-，而是 **VBUS current pulsing / load modulation**，所以量測條件要明寫示波器與電流探棒。
- 週期長、反應慢，timing row 應用 `_TMU` 並標示單位 `ms` / `s`。

## Protocol → TenJI 欄位對應

| Protocol field | TenJI 欄位 | 寫法建議 |
|---|---|---|
| protocol | C (Test_Item) | 固定 `PE` / `PE1` / `PE2` |
| signaling_path | I / N | `VBUS load modulation` |
| current_pulse_detect | H / I | 寫示波器 + current probe 量測條件 |
| target_voltage_step | J/K/L/M | 5V / 7V / 9V / 12V ... 或 0.5V step |
| source_transition | H / I | request 後觀察 VBUS 切換 |
| long_cycle_timing | D / J/K/L/M | 反應時間 / 週期拆 `_TMU` |
| fail / fallback | I / N | pulse decode fail 時維持或回退安全電壓 |
| log_keywords | N | `current pulse / VBUS modulation / slow response / fallback` |

## 建議 Test Note 骨架

| B | C | D | E | F | G | H | I | J | K | L | M | N |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | PE | PE_VBUS_PULSE_DET | PWR_PE |  | Run Pattern | Scope + current probe on VBUS | 驗證 sink 透過 current pulsing / load modulation 在 VBUS 上送出 PE request pattern | 待補 |  | 待補 | A | physical layer |
| 2 | PE | PE_REQ_7V | PWR_PE |  | Wait 2s | JudgeV VBUS 6.5V 7.5V | 驗證 PE request 後 Source 可切到 7V 檔位 | 6.5 | 7.0 | 7.5 | V | PE1 example |
| 2 | PE | PE_REQ_9V | PWR_PE |  | Wait 2s | JudgeV VBUS 8.5V 9.5V | 驗證 PE request 後 Source 可切到 9V 檔位 | 8.5 | 9.0 | 9.5 | V | voltage transition |
| 2 | PE | PE_STEP_0P5V | PWR_PE |  | Wait 2s | JudgeV VBUS 5V 20V | 驗證 PE2.0 可依 step 調整 VBUS（0.5V/step） | 待補 | target | 待補 | V | step behavior |
| 2 | PE | PE_RESP_TMU | PWR_PE |  | Run Pattern | MeasDelay pulse_train_end VBUS_target | 量測 pulse request 到 VBUS 到位的反應時間 | 待補 |  | 待補 | s | long-cycle timing |
| 2 | PE | PE_FALLBACK_SAFE | PWR_PE |  | Run Pattern | JudgeV VBUS 4.75V 5.25V | pulse decode fail / abort 時，應停留或回退到安全電壓 | 4.75 | 5.00 | 5.25 | V | fallback |

## 拆項建議
- 依 PE1 / PE2 分開
- 各 target voltage 各自獨立 row
- timing / settle / fallback 獨立成 `_TMU` 或 exception row
