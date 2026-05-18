# Build Commands

## Windows — Nuitka 编译

使用 **PowerShell**（推荐）：

```powershell
python -m nuitka `
  --standalone `
  --windows-console-mode=disable `
  --windows-icon-from-ico=gmId.ico `
  --include-data-files=gmId.ico=gmId.ico `
  --enable-plugin=pyqt5 `
  --disable-plugin=matplotlib `
  --nofollow-import-to=PIL `
  --nofollow-import-to=matplotlib `
  --include-package=pyqtgraph `
  --include-package=scipy `
  --include-package=h5py `
  --jobs=20 `
  --assume-yes-for-downloads `
  --output-dir=build `
  --output-filename=gmIdSizing `
  runGmIdSizing.py
```

或使用 **cmd**：

```cmd
python -m nuitka ^
  --standalone ^
  --windows-console-mode=disable ^
  --windows-icon-from-ico=gmId.ico ^
  --include-data-files=gmId.ico=gmId.ico ^
  --enable-plugin=pyqt5 ^
  --disable-plugin=matplotlib ^
  --nofollow-import-to=PIL ^
  --nofollow-import-to=matplotlib ^
  --include-package=pyqtgraph ^
  --include-package=scipy ^
  --include-package=h5py ^
  --jobs=20 ^
  --assume-yes-for-downloads ^
  --output-dir=build ^
  --output-filename=gmIdSizing ^
  runGmIdSizing.py
```

产物位于 `build\runGmIdSizing.dist\`。

---

## Windows — Inno Setup 打包

```powershell
Copy-Item gmId.ico build\runGmIdSizing.dist\
ISCC.exe setup.iss
```

输出安装包 `gmIdSizing_Setup.exe`。

---

## Linux — Nuitka 编译

```bash
python3 -m nuitka --standalone \
    --include-data-files=gmId.ico=gmId.ico \
    --enable-plugin=pyqt5 \
    --disable-plugin=matplotlib \
    --nofollow-import-to=PIL \
    --nofollow-import-to=matplotlib \
    --include-package=pyqtgraph \
    --include-package=scipy \
    --include-package=h5py \
    --jobs=20 \
    --assume-yes-for-downloads \
    --output-dir=build \
    --output-filename=gmIdSizing \
    runGmIdSizing.py
```

---

## Linux — deb 打包

```bash
cp -r build/runGmIdSizing.dist/* deb/opt/gmIdSizing/
dpkg-deb --build deb gmIdSizing_amd64.deb
```

---

## Qt Designer UI 更新

使用 Qt Designer 修改 `gmIdSizingGuiVp1.ui` 后，重新生成 Python 代码：

```bash
pyuic5 gmIdSizingGuiVp1.ui -o gmIdSizingGuiVp1.py
```
