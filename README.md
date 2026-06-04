# gmIdNeoKit_tsmc18

TSMC 180nm PDK 模拟电路设计自动化工具集（gm/ID 查找表生成 + GUI 器件尺寸规划）。

本项目基于 [gmIdNeoKit](https://github.com/fengqzHD/gmIdNeoKit)，对 TSMC 180nm 工艺库的 1.8V 和 5V MOS 器件（nch / pch / nch_5v / pch_5v）进行 Spectre （Cadence IC617）扫描仿真、数据提取，生成 gm/ID 查找表，并通过 PyQt5 GUI 完成器件尺寸的交互式规划。

![gmId tsmc18 Demo](gmId_tsmc18_Demo.png)

---

## 项目结构

```
.
├── GUI/                    # PyQt5 GUI 应用（基于查找表的 MOS 尺寸规划与优化）
│   ├── gmIdSizingGuiVp1.py # GUI 主程序
│   ├── gmIdSizingGuiVp1.ui # Qt Designer UI 源文件
│   ├── LupMos.py           # MOS 器件数据解析与插值
│   ├── const.py            # 常量定义
│   ├── runGmIdSizing.py    # GUI 启动入口
│   ├── png2ico.py          # png → ico 图标转换脚本
│   ├── gmId.ico / gmId.png # 应用图标
│   ├── gmIdSizing.desktop  # Linux 桌面入口
│   ├── setup.iss           # Inno Setup 打包脚本
│   ├── BUILD.md            # 构建命令说明
│   └── README.org          # GUI 原始说明文档
├── lookup_funs/            # Python 查找表查询 API 与使用文档
│   ├── lookup_table.py     # 核心模块（LookupTable / lookup / lookupVGS / loadmat）
│   ├── ekv_extract.py      # EKV 参数提取
│   ├── xtract_demo.py      # EKV 提取示例
│   ├── plot_demo.py        # gm/ID 绘图示例
│   └── LOOKUP_README.md    # API 使用指南
├── pipeline.sh             # 1.8V 器件逐 L 流水线（仿真 → 提取 → 清理）
├── pipeline_5v.sh          # 5V 器件逐 L 流水线（仿真 → 提取 → 清理）
├── config_tsmc18.py        # 1.8V 器件扫描参数配置
├── config_tsmc18_5v.py     # 5V 器件扫描参数配置
├── run_sim.py              # 1.8V 器件 Spectre 并行仿真
├── run_sim_5v.py           # 5V 器件 Spectre 并行仿真
├── extract_new.py          # 统一数据提取脚本（1.8V + 5V），生成 .mat 查找表
├── psf_reader.py           # PSF 格式仿真结果读取器
└── gmId_tsmc18_Demo.png    # 工具截图
```

## 运行环境

| 组件                 | 环境要求                                                                           |
| -------------------- | ---------------------------------------------------------------------------------- |
| Spectre 扫描仿真     | VMware 虚拟机 + CentOS 6.5 + Cadence Virtuoso IC 6.1.7                             |
| 数据提取 & .mat 生成 | Python 3.6.8（CentOS 6.5 上从源码编译安装）或 Windows 本地 Python                  |
| GUI 应用             | 预构建安装包开箱即用（推荐）；或 Python 3.x + PyQt5, pyqtgraph, h5py, scipy, numpy |
| 查找表 API           | Python 3.x + numpy, scipy, h5py                                                    |
| Pipeline（推荐）     | Bash + Python + tmpfs（RAM disk），需要 root 权限挂载                              |

> **注意**：CentOS 6.5 过于老旧，Python 3.6.8 需从源码编译。更高版本的 Python 理论上也可工作，但未完整测试。

## 硬件需求

| 项目           | 要求                                          |
| -------------- | --------------------------------------------- |
| 虚拟机内存     | ≥ 20 GB（推荐 24 GB）                        |
| 宿主机内存     | 建议 ≥ 32 GB                                 |
| 持久化磁盘     | ≥ 150 GB（.mat 文件总计约 135 GB）           |
| Pipeline tmpfs | 1.8V: 13 GB / 5V: 16 GB（需从可用内存中分配） |

## 快速开始

### 1. Pipeline 一键运行（推荐）

使用 `pipeline.sh` 和 `pipeline_5v.sh`，**逐 L 增量处理**——每级栅长 L 独立走完 仿真→提取→清理 流程，5 个工艺角并行。原始仿真数据放在 RAM disk 上，提取完即删除，不占用持久化磁盘。

```bash
# 在虚拟机中执行（需要 root 权限以挂载 tmpfs）
sudo bash pipeline.sh
sudo bash pipeline_5v.sh
```

> 编辑脚本顶部的 `MATDIR` 变量可修改 .mat 输出目录，`RAMDIR` 变量指定 RAM disk 挂载点。

### 2. 分步运行

也可手动分步执行。`extract_new.py` 支持 `--srcdir`（原始仿真数据目录）和 `--outdir`（.mat 输出目录）分离，适配 RAM disk 场景。

#### Step 1 — 扫描仿真

```bash
# 1.8V 器件（指定 corner 和输出目录）
python run_sim.py tt --fine --outdir /path/to/raw
# 5V 器件
python run_sim_5v.py tt --fine --outdir /path/to/raw
```

#### Step 2 — 数据提取

```bash
# 提取 .mat 查找表（可在 Windows 本机执行）
python extract_new.py --voltage 18 --fine --srcdir /path/to/raw --outdir /path/to/mat --workers 5
python extract_new.py --voltage 5v --fine --srcdir /path/to/raw --outdir /path/to/mat --workers 5
```

#### Step 3 — 使用查找表 API

```python
from lookup_funs.lookup_table import loadmat, lookup, lookupVGS

nch = loadmat("D:\\tsmc18_lookup\\tsmc18-nch-tt.mat")
gm_id = lookup(nch, 'GM_ID', 'VGS', 0.6, 'VDS', 0.9, 'L', 0.35)
VGS   = lookupVGS(nch, 'GM_ID', 15, 'L', 0.35)
```

详细 API 文档见 `lookup_funs/LOOKUP_README.md`。

#### Step 4 — 启动 GUI

```bash
cd GUI
pip install PyQt5 pyqtgraph h5py scipy numpy
python runGmIdSizing.py
```

## 磁盘空间需求

| 文件                                      | 大小                                  |
| ----------------------------------------- | ------------------------------------- |
| 1.8V 器件单 .mat 文件（nch 或 pch, fine） | ~4.44 GB / 个                         |
| 1.8V 器件全部 .mat（5 corner × 2 type）  | ~44.4 GB                              |
| 5V 器件单 .mat 文件（nch 或 pch, fine）   | ~9 GB / 个                            |
| 5V 器件全部 .mat（5 corner × 2 type）    | ~89.8 GB                              |
| **总计持久化磁盘需求**              | **≥ 150 GB**（含临时文件余量） |
| Pipeline tmpfs（1.8V）                    | 13 GB（RAM disk，随 L 清理不累积）    |
| Pipeline tmpfs（5V）                      | 16 GB（RAM disk，随 L 清理不累积）    |

> Pipeline 模式下原始仿真数据完全存放在 RAM disk（tmpfs）上，每个 L 提取完成后立刻删除，因此不占用持久化磁盘空间。.mat 文件大小的大幅增长源于精细 L 网格（1.8V: 12→51 点, 5V: 12→55/57 点）和更丰富的保存信号（22 个 OP 参数）。

## 性能说明

| 流程                                            | 仿真时间   |
| ----------------------------------------------- | ---------- |
| 1.8V 器件完整扫描（51 L × 17 VSB × 5 corner） | ~5.5 小时  |
| 5V 器件完整扫描（57 L × 21 VSB × 5 corner）   | ~11.5 小时 |

> **IO 瓶颈**：使用 VMware 共享文件夹（hgfs）作为输出目录会显著降低 IO 速度（耗时3x~10x），建议使用虚拟机内部磁盘或 tmpfs 作为原始数据暂存目录，仅在最终 .mat 文件完成后复制到 Windows。
>
> **RAM disk 模式**：`pipeline.sh` 通过 tmpfs 将原始仿真数据放在内存中，每 L 提取完即删除，大幅减少磁盘 IO。需确保虚拟机内存 ≥ 20 GB（建议 24 GB），宿主机可用内存 ≥ 32 GB。

## GUI 使用说明

### Windows 用户（推荐预构建安装包）

直接下载 `gmIdSizing_Setup.exe` 安装包运行即可，无需安装 Python 解释器及依赖库，开箱即用。

> 也可使用 Python 脚本启动：`pip install PyQt5 pyqtgraph h5py scipy numpy` 后执行 `python runGmIdSizing.py`，建议有二次开发需求的用户使用。

### Linux 用户

优先使用预构建的 `.deb` 包。若你的发行版或架构不支持 `.deb`（如 Fedora、Arch、ARM 等），可直接通过 Python 脚本启动：

```bash
pip install PyQt5 pyqtgraph h5py scipy numpy
python runGmIdSizing.py
```

### 操作概要

详见 `GUI/README.org`，概要如下：

1. **加载数据**：点击 `Sel` 选择 .mat 文件所在目录 → 选择文件 → `Set` 设定
2. **设置栅长**：选择 `Ldes`（期望栅长）、`Lref`（参考栅长）、`Lchk`（检查栅长）
3. **绘图**：点击 `Plot` 查看 Vstar / Id / Vgs / GmId 关系曲线
4. **器件尺寸规划**：支持 Syn（偏置计算）、Cal（参数核算）、Opt（跨 L 优化）三种模式

## 致谢

- [gmIdNeoKit](https://github.com/fengqzHD/gmIdNeoKit) — fengqzHD 前辈创建的 GUI 应用（进行了些许 bug 修复与界面调整）
- Paul G.A. Jespers & Boris Murmann — gm/ID 方法学及 [gm/ID Starter Kit](https://web.stanford.edu/~murmann/gmid)

## 交流与联系

欢迎模拟电路设计相关探讨、问题反馈或功能建议。

| 联系方式  | 信息            |
| --------- | --------------- |
| 邮箱      | zz6zz666@qq.com |
| QQ / 微信 | 1807651273      |

— SEU ZZ
