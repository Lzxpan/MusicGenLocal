# MusicGenLocal V0.91b

`MusicGenLocal V0.91b` 是一個本機離線音樂生成工具，現在同時提供：

- 命令列生成流程
- 全中文桌面 GUI `MusicGenLocal 音樂工作站 V0.91b`
- `musicgen-local` 與 `musicgen-local-ui` 兩個 Codex skill
- `PyInstaller --onefile` 單檔 exe 打包流程

它的目標是讓使用者可以快速用中文選擇風格、類型、樂器、情緒、節奏與時長，生成遊戲用 BGM 原型，然後在同一個軟體內直接試聽、重新命名與整理成品。

## 功能特色

- 本機離線生成，不依賴雲端付費 API
- GUI 所有欄位、按鈕、提示與狀態皆為繁體中文
- 支援 `風格`、`類型`、`樂器`、`情緒`、`節奏 / BPM`、`時長`、`大小調`、`能量感`
- `補強描述` 可自由追加細節
- 生成前可直接編修實際送進模型的提示詞
- 背景生成佇列，不會把 GUI 卡死
- 內建音檔庫，可播放 / 暫停 / 停止 / 更名 / 刪除 / 帶回設定
- 每首成品都會保存 `.prompt.txt` 與 `.json` 詳細資料
- 可打包成單檔 `exe`

## 技術選型

目前 GUI 版本採用：

- `Python 3.9+`
- `PySide6`
- `Meta MusicGen`
- `torch`
- `transformers`
- `PyInstaller`

這是目前最穩妥的組合，因為可以直接重用既有 MusicGen 核心，不需要再做 `C#` 與 `Python` 的跨語言橋接，也方便輸出 Windows 單檔執行檔。

## 專案結構

```text
MusicGenLocal/
├─ app/
│  ├─ core/
│  ├─ prompting/
│  ├─ services/
│  ├─ ui/
│  └─ main.py
├─ build-portable-ui.ps1
├─ generate-bgm-local.ps1
├─ launch-musicgen-ui.ps1
├─ musicgenlocal-ui.spec
├─ install-skill.ps1
├─ setup-musicgen-local.ps1
├─ prompts/
├─ music/
├─ skill/
└─ skill-ui/
```

## 系統需求

- Windows 10/11
- Python 3.9 以上
- PowerShell
- 建議至少 16 GB RAM
- 若以 CPU 生成 30 秒音樂，請預期等待時間明顯高於 8 秒測試版

## 安裝方式

### 1. 下載專案

```powershell
git clone https://github.com/Lzxpan/MusicGenLocal.git
cd MusicGenLocal
```

### 2. 建立本機環境

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-musicgen-local.ps1
```

這個步驟會建立 `skill/.venv`，並安裝：

- `torch`
- `transformers`
- `sentencepiece`
- `scipy`
- `PySide6`
- `PyInstaller`

第一次安裝可能會比較久。

## 啟動全中文 GUI

```powershell
powershell -ExecutionPolicy Bypass -File .\launch-musicgen-ui.ps1
```

若 `dist\MusicGenLocal-Studio.exe` 已存在，啟動腳本會優先開啟 exe；否則會使用目前的 Python 環境直接啟動 GUI。

### 直接執行單檔版

如果你已經完成打包，也可以直接執行：

```powershell
.\dist\MusicGenLocal-Studio.exe
```

第一次啟動速度比一般程式慢一些，這是 `PyInstaller --onefile` 的正常現象。

### GUI 使用流程

1. 在左側選擇 `風格`、`類型`、`樂器`、`情緒`、`節奏 / BPM`、`調性主音`、`大小調`、`時長`
2. 需要時填寫 `補強描述`
3. 檢查中下方 `最終生成提示詞`
4. 按 `加入生成佇列`
5. 在中間區域看進度與等待任務
6. 在右側音檔庫試聽、改名、刪除或重帶設定

## 命令列使用方式

### 生成 8 秒測試版

```powershell
.\generate-bgm-local.ps1 -Seconds 8 -Seed 42
```

### 生成 30 秒正式版

```powershell
.\generate-bgm-local.ps1 -Seconds 30 -Seed 42
```

### 指定輸出檔名

```powershell
.\generate-bgm-local.ps1 -Seconds 30 -Seed 42 -Out .\music\bgm-loop-v2.wav
```

### 指定 prompt 檔

```powershell
.\generate-bgm-local.ps1 -PromptFile .\prompts\arcade-loop.txt -Seconds 30 -Seed 42
```

## 模型下載與快取

第一版採「第一次使用自動下載模型，之後離線使用」：

- 預設模型：`facebook/musicgen-small`
- 預設快取位置：`.\model-cache\`

GUI 會直接顯示模型快取位置。

如果本機尚未下載模型：

- 第一次生成時會先初始化模型
- 若網路可用，會自動下載
- 若網路不可用，GUI 會顯示中文錯誤，而不是靜默失敗

## 輸出檔案與詳細資料

每首音樂都會對應：

- `track-name.wav`
- `track-name.prompt.txt`
- `track-name.json`

`.json` 會保存：

- 中文顯示參數
- 底層英文 token 值
- `固定 Seed`
- `模型`
- 最終提示詞
- 建立時間
- 模型快取位置

這讓 GUI 可以直接把舊音檔設定帶回左側表單。

## 單檔 exe 打包

### 建立 exe

```powershell
powershell -ExecutionPolicy Bypass -File .\build-portable-ui.ps1
```

輸出目標：

```text
.\dist\MusicGenLocal-Studio.exe
```

### 單檔 exe 注意事項

- 目前採 `PyInstaller --onefile`
- 啟動速度會比資料夾型發佈慢一些，這是正常現象
- 模型不會直接包進 exe，第一次使用仍需下載到 `model-cache`
- 若要在另一台沒有 Python 的 Windows 機器上使用，可直接複製 `MusicGenLocal-Studio.exe`

## Skill 安裝方式

本專案包含兩個 skill：

- `musicgen-local`
- `musicgen-local-ui`

### 快速安裝

```powershell
.\install-skill.ps1
```

如果你想用複製而不是 junction：

```powershell
.\install-skill.ps1 -Copy
```

### 安裝後確認位置

安裝完成後，預設會在下列位置看到 skill：

```text
C:\Users\Admin\.codex\skills\musicgen-local
C:\Users\Admin\.codex\skills\musicgen-local-ui
```

### Skill 使用方式

1. 執行 `.\install-skill.ps1`
2. 重新啟動 Codex
3. 在新對話中直接指定要用的 skill

### Skill 使用範例

CLI skill：

```text
使用 $musicgen-local 在本機生成一段可循環的街機風解謎遊戲背景音樂。
```

GUI skill：

```text
使用 $musicgen-local-ui 啟動 MusicGenLocal 音樂工作站，並用 GUI 方式生成與管理音樂。
```

### 兩個 skill 的差異

- `musicgen-local`
  - 適合命令列生成、調 prompt、快速做測試片段
- `musicgen-local-ui`
  - 適合啟動圖形介面、用中文表單選參數、管理既有音檔與試聽

## 常見問題

### 為什麼 30 秒生成很久？

因為目前是本機 `MusicGen`，而且大多數情況是在 CPU 上跑。  
GUI 會保持可操作，但生成本身仍然需要時間。

### 為什麼進度條不是很準？

目前是估計型進度，不是模型真實 token 百分比。  
它的用途是讓使用者知道系統仍在工作，而不是精準反映模型內部狀態。

### 這個工具會自動保證完美 loop 嗎？

不會。  
它是做 loop 風格背景音樂生成，不是 sample-accurate 的自動 loop 裁切器。  
如果你需要極精準無縫 loop，仍建議進 DAW 再微調。

## 目前限制

- 預設模型為 `facebook/musicgen-small`
- 以本機單機使用為主
- 沒有雲端同步
- 沒有多人協作
- 沒有波形編輯器
- 沒有自動裁切 loop 點
- 單檔 exe 仍會在第一次執行時花時間初始化與解壓

## 授權

本 repo 內的原始碼、PowerShell 腳本、Python 腳本、GUI 程式、skill 定義與文件，採用 `Apache License 2.0` 授權。

你可以：

- 免費使用
- 免費修改
- 免費商用
- 重新散布

但請保留：

- `LICENSE`
- `NOTICE`
- 原始出處資訊

建議標示：

```text
Based on MusicGenLocal by Lzxpan
```

補充：

- 本 repo 的授權不自動延伸到第三方模型本身
- `facebook/musicgen-small` 仍須遵守其上游授權與平台條款
- 生成出的音樂如何再授權，應由實際產出與使用者自行判斷
