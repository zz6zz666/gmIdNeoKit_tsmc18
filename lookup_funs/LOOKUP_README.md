# tsmc18 查找表使用操作指南

## TSMC 180nm 工艺库

### 1. 工艺库位置

```text
D:\tsmc18_lookup\
├── tsmc18-nch-tt.mat       (1.8V nch, typical corner)
├── tsmc18-nch-ff.mat       (1.8V nch, fast corner)
├── tsmc18-nch-fs.mat       (1.8V nch)
├── tsmc18-nch-sf.mat       (1.8V nch)
├── tsmc18-nch-ss.mat       (1.8V nch, slow corner)
├── tsmc18-pch-tt.mat       (1.8V pch, typical corner)
├── tsmc18-pch-ff.mat       (1.8V pch, fast corner)
├── tsmc18-pch-fs.mat       (1.8V pch)
├── tsmc18-pch-sf.mat       (1.8V pch)
├── tsmc18-pch-ss.mat       (1.8V pch, slow corner)
└── tsmc18_5v\              (5V 器件目录)
    ├── tsmc18-nch_5-tt.mat (5V nch_5, typical corner)
    ├── tsmc18-nch_5-ff.mat (5V nch_5, fast corner)
    ├── tsmc18-nch_5-fs.mat (5V nch_5)
    ├── tsmc18-nch_5-sf.mat (5V nch_5)
    ├── tsmc18-nch_5-ss.mat (5V nch_5, slow corner)
    ├── tsmc18-pch_5-tt.mat (5V pch_5, typical corner)
    ├── tsmc18-pch_5-ff.mat (5V pch_5, fast corner)
    ├── tsmc18-pch_5-fs.mat (5V nch_5)
    ├── tsmc18-pch_5-sf.mat (5V nch_5)
    └── tsmc18-pch_5-ss.mat (5V pch_5, slow corner)
```

正常设计使用 `tt`（typical）corner。

### 2. 工艺参数概览

| 参数 | 数值 |
|------|------|
| **电源电压** $V_{DD}$ | **1.8 V** |
| **默认 $V_{DS}$** | **0.9 V**（$V_{DD}/2$） |
| **默认 $V_{SB}$** | 0 V |
| $V_{GS}$ 范围 | 0 ~ 1.8 V，步长 0.01 V |
| $V_{DS}$ 范围 | 0 ~ 1.8 V，步长 0.01 V （默认可取 0.9V = 1.8V / 2） |
| $V_{SB}$ 范围 | 0.0 ~ 1.6 V，步长 0.1 V（17 个点） |
| L 范围 | 0.18 ~ 2.0 µm（51 个点），详细值见下方 |
| 仿真宽度 W | 5 µm（所有查表结果已归一化到此宽度） |

> **L 详细值（51 点）**：
> 
> 0.18~0.5（步长 0.01，部分 0.025）：
> `0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.325, 0.35, 0.375, 0.40, 0.425, 0.45, 0.475, 0.50`
> 
> 0.525~1.0（步长 0.025）：
> `0.525, 0.55, 0.575, 0.60, 0.625, 0.65, 0.675, 0.70, 0.725, 0.75, 0.775, 0.80, 0.825, 0.85, 0.875, 0.90, 0.925, 0.95, 0.975, 1.00`
> 
> 1.1~2.0（步长 0.1）：
> `1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0`

> **注意**：工艺库数据已更新（2026-06-04），L 网格从原先的 12 个点大幅扩展至 51 个点，VSB 范围从 0.6 V 扩展到 1.6 V。`lookupVGS` Mode 2 能处理更大的 VSB 范围，更适用于差分对等场景。

### 2.b 5V 器件

`tsmc18_5v/` 目录下存放 5V 耐压器件（如 IO 管、输出级等），参数如下：

| 参数 | 数值 |
|------|------|
| **电源电压** | **5.5 V** |
| $V_{GS}$ / $V_{DS}$ 范围 | 0 ~ 5.5 V，步长 0.01 V |
| $V_{SB}$ 范围 | 0.0 ~ 5.0 V，步长 0.25 V（21 个点） |
| L 范围 | nch_5: 0.6 ~ 10 µm（55 点） / pch_5: 0.5 ~ 10 µm（57 点），详细值见下方 |
| 仿真宽度 W | 5 µm |

```python
# 加载 5V 器件（文件较大 ~9GB，加载需约 40s）
nch_5 = loadmat(r"D:\tsmc18_lookup\tsmc18_5v\tsmc18-nch_5-tt.mat")
pch_5 = loadmat(r"D:\tsmc18_lookup\tsmc18_5v\tsmc18-pch_5-tt.mat")

# API 用法与 1.8V 器件完全相同
gain = lookup(nch_5, 'GM_GDS', 'GM_ID', 10, 'VDS', 2.5, 'L', 1.0)
```

> **L 详细值**：
> 
> nch_5（55 点，0.6~10 µm）：
> 0.6~3.0（步长 0.05）：
> `0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.75, 1.80, 1.85, 1.90, 1.95, 2.00, 2.05, 2.10, 2.15, 2.20, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50, 2.55, 2.60, 2.65, 2.70, 2.75, 2.80, 2.85, 2.90, 2.95, 3.00`
> 3.5~10（长沟道离散值）：
> `3.5, 4.0, 5.0, 6.0, 8.0, 10.0`
> 
> pch_5（57 点，0.5~10 µm，比 nch 多 `0.50`, `0.55` 两点，其余与 nch 一致）

> **适用场景**：当电路中存在高于 1.8V 的电压域时（如输出驱动级），应使用 5V 器件。

### 3. 加载工艺库

```python
from lookup_table import loadmat, lookup, lookupVGS

# 典型 corner（常规设计用）
nch = loadmat(r"D:\tsmc18_lookup\tsmc18-nch-tt.mat")
pch = loadmat(r"D:\tsmc18_lookup\tsmc18-pch-tt.mat")

# 查看元信息
print(nch.CORNER)   # 'tt'
print(nch.INFO)     # 'tsmc18, BSIM4'
print(nch.L)        # 沟道长度向量
print(nch.W)        # 仿真总宽度 (µm)
```

### 4. 核心 API：lookup()

三种使用模式：

```python
# Mode 1 – 基础查表（已知 VGS, VDS, VSB, L）
id = lookup(nch, 'ID', 'VGS', 0.6, 'VDS', 0.9, 'L', 0.35, 'VSB', 0)

# Mode 2 – 比值查表（自动计算 A/B）
gm_id = lookup(nch, 'GM_ID', 'VGS', 0.6, 'VDS', 0.9, 'L', 0.35)
id_w  = lookup(nch, 'ID_W',  'VGS', 0.6, 'VDS', 0.9, 'L', 0.35)

# Mode 3 – 交叉查表（用 GM_ID 查其他变量）
gain = lookup(nch, 'GM_GDS', 'GM_ID', 15, 'VDS', 0.9, 'L', 0.35)
ft   = lookup(nch, 'FUG',    'GM_ID', 15, 'VDS', 0.9, 'L', 0.35)
jd   = lookup(nch, 'ID_W',   'GM_ID', 15, 'VDS', 0.9, 'L', 0.35)
```

默认值：
- `L` → `min(data.L)`
- `VDS` → `max(data.VDS) / 2` = **0.9 V**
- `VSB` → 0
- `VGS` → 全 VGS 向量

### 5. 核心 API：lookupVGS()

反向查找：给定 gm/ID 或 ID/W，求 VGS。

```python
# Mode 1 – 已知源端电压（默认 VDS=0.9V, VSB=0）
VGS = lookupVGS(nch, 'GM_ID', 15, 'L', 0.35)

# Mode 1 – 明确指定 VDS, VSB
VGS = lookupVGS(nch, 'GM_ID', 15, 'VDS', 0.5, 'VSB', 0.1, 'L', 0.35)

# Mode 2 – 未知源端电压（差分对尾节点、cascode 等场景）
# 传入 VGB（栅-衬底）和 VDB（漏-衬底），内部自洽求解
VGS = lookupVGS(nch, 'GM_ID', 15, 'VGB', 0.9, 'VDB', 1.2, 'L', 0.35)
```

**Mode 2 内部约束**：
```
VSB = VGB - VGS
VDS = VDB - VSB
```

### 6. 常用查表变量

| 变量 | 含义 | 单位 |
|------|------|------|
| `ID` | 漏极电流 | A |
| `GM` | 跨导 $g_m$ | S |
| `GDS` | 输出电导 $g_{ds}$ | S |
| `VT` | 阈值电压 $V_T$ | V |
| `VDSAT` | 饱和电压 | V |
| `FUG` | 特征频率 $f_T$ | Hz |
| `CGG` | 总栅电容 | F |
| `CGD` | 栅漏电容 | F |
| `GM_ID` | $g_m/I_D$ | S/A |
| `GM_GDS` | $g_m/g_{ds}$（本征增益） | V/V |
| `GDS_ID` | $g_{ds}/I_D$ | S/A |
| `ID_W` | 电流密度 $I_D/W$ | A/µm |

### 7. 关键示例文件

| 文件 | 用途 |
|------|------|
| `lookup_table.py` | 核心模块（`LookupTable`、`lookup`、`lookupVGS`） |
| `ekv_extract.py` | EKV 提取模块 |
| `xtract_demo.py` | EKV 参数提取示例 |
| `plot_demo.py` | 3×3 栅格 gm/ID 图表绘制、mplcursors 交互 |

### 8. 典型用法模式

```python
# 1. 在固定 gm/ID 下扫描不同 L 的本征增益
for L in [0.18, 0.35, 0.5, 1.0]:
    gain = lookup(nch, 'GM_GDS', 'GM_ID', 15, 'VDS', 0.9, 'L', L)
    print(f"L={L:.2f}um, gm/gds={gain:.1f}")

# 2. 查 VGS 自洽确定工作点（二极管连接 |VDS|=|VGS|）
VGS2 = lookupVGS(pch, 'GM_ID', 10, 'L', 0.5)       # 初估
VGS2 = lookupVGS(pch, 'GM_ID', 10, 'VDS', VGS2, 'L', 0.5)  # 一次迭代自洽

# 3. 差分对 M1 用 Mode 2 直接求解（不确定 V_S）
VGS1 = lookupVGS(nch, 'GM_ID', 15, 'VGB', VIC, 'VDB', VOUT, 'L', 0.35)
# 后验：V_S = VIC - VGS1, V_DS1 = VOUT - V_S, V_SB1 = V_S
```