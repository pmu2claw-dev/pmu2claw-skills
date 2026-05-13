# PseudoCode / I2C 相關指令

## PseudoCode — I2C 指令

```
PseudoCode  Command  Reg  Var
```

H 欄填 `I2C` 時使用。

### 5 種 Command

| Command | 功能 |
|---------|------|
| `WriteVar` | 把變數 Var（英文字母開頭）的值寫到 Reg |
| `WriteVal` | 把數值 Var 寫到 Reg |
| `ReadVar` | 把 Reg 的值讀出存到變數 Var |
| `ReadVal` | 讀出 Reg 的值，與預期數值 Var 比較 |
| `0x[aa]` | 指定 slave address 做 I2C 操作 |

### Reg 格式

- `Reg` — 整個 register（default 8 bit）
- `Reg:N~0` — 部分 bit，例如 `0x53:4~0` = register 0x53 的 bit[4:0]，bit[7:5] 不變

### Var 格式

- `Var` — 整個變數或 register
- `Var:N~0` — 部分 bit，例如 `T2:4~0` = 變數 T2 的 bit[4:0]

### 範例

```
PseudoCode WriteVar 0x81:3~0 T36:5~2
```
→ 把 T36 的 bit[5:2] 寫到 register 0x81 的 bit[3:0]，0x81 的 bit[7:4] 不變。

```
PseudoCode WriteVal 0x81 0xbb
```
→ 把 data 0xbb 寫到 register 0x81（8bit 全寫）。

```
PseudoCode ReadVar 0x81:3~0 GBY29:5~2
```
→ 讀出 register 0x81 的 bit[3:0]，存到 GBY29 的 bit[5:2]。

```
PseudoCode ReadVal 0x81 0xbb
```
→ 讀出 register 0x81 的值，與 0xbb 比較，不符則 error。

```
PseudoCode 0xb0 0x81 0xbb
```
→ 對 slave address 0x58（因為 0xb0 的 bit[7:1] = 0x58, bit[0]=0 表示 write）做 I2C write，把 0xbb 寫到 register 0x81。

```
PseudoCode 0xb1 0x81 GBY20
```
→ 對 slave address 0x58 做 I2C read（bit[0]=1），讀出 register 0x81 存到 GBY20。

---

## I2C_BURST_READ — I2C Burst 讀取

連續讀取多個 register。

## I2C_BURST_WRITE — I2C Burst 寫入

連續寫入多個 register。

---

## BOOTLOADER_EXEC — 執行 Bootloader

## BOOTLOADER_READ — 讀取 Bootloader

---

## 為何用 Pseudo Code？

如果 I2C command list 很多，一行一行寫到 H 欄會造成可讀性差、難以 debug。
把常用 command list 包裝成 Pseudo Code sheet 中的巨集指令，可以：
- 增加可讀性
- 減少 typo
- 方便 debug
