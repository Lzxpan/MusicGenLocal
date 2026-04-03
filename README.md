# MusicGenLocal

`MusicGenLocal` 是一個可獨立使用的本機音樂生成工具，目標是用 `Meta MusicGen` 在本地端生成遊戲背景音樂，特別適合製作可循環播放的 puzzle / arcade 類型 BGM。

這個專案同時包含：

- 可直接執行的本機生成腳本
- 預設的遊戲 BGM prompt
- 一個可安裝到 Codex 的 `musicgen-local` skill

不需要任何雲端 API key。

## 功能特色

- 本機離線生成，不依賴雲端付費 API
- 適合做 4 到 30 秒的遊戲背景音樂原型
- 預設輸出到專案內的 `music/` 資料夾
- 支援 `Seed`，方便重現結果
- 內含 Codex skill，可重複調用

## 專案結構

```text
MusicGenLocal/
├─ generate-bgm-local.ps1
├─ setup-musicgen-local.ps1
├─ prompts/
│  └─ arcade-loop.txt
├─ music/
│  └─ .gitkeep
└─ skill/
   ├─ SKILL.md
   ├─ agents/
   │  └─ openai.yaml
   ├─ references/
   │  └─ prompting.md
   └─ scripts/
      ├─ generate_music.py
      ├─ requirements.txt
      └─ setup_venv.ps1
```

## 系統需求

- Windows PowerShell 或 PowerShell 7
- Python 3.9 以上
- 足夠的磁碟空間下載模型
- 建議至少 16 GB RAM；本專案目前已在 32 GB RAM / CPU 模式下驗證可用

## 安裝方式

### 1. 下載專案

```powershell
git clone <你的 repo URL>
cd MusicGenLocal
```

### 2. 安裝本機生成環境

在專案根目錄執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-musicgen-local.ps1
```

這個指令會：

- 建立 `skill/.venv`
- 安裝 `torch`
- 安裝 `transformers`
- 安裝 `sentencepiece`
- 安裝 `scipy`

第一次安裝會花比較久，因為需要下載模型與 Python 套件。

## 生成音樂

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

### 指定不同 prompt 檔

```powershell
.\generate-bgm-local.ps1 -PromptFile .\prompts\arcade-loop.txt -Seconds 30 -Seed 42
```

## 預設輸出位置

預設會輸出到：

- `.\music\bgm-loop.wav`
- `.\music\bgm-loop.prompt.txt`

也就是：

- 音樂檔會放在專案根目錄的 `music/`
- 實際使用的 prompt 會另外存成文字檔，方便重現

## 如何調整風格

你可以直接修改 `prompts/arcade-loop.txt`。

建議可調整的方向：

- `Retro arcade`
- `puzzle game`
- `seamless loop`
- `8-bit`
- `synth pulse`
- `bright focused energy`
- `BPM`

如果你想做更 chill 的版本，可以往：

- lofi
- mellow
- soft drums
- warm bass

如果你想做更緊張的版本，可以往：

- faster tempo
- sharper synth
- tense arcade action

## 速度與進度條

本機 `MusicGen` 在 CPU 上生成 30 秒音樂，通常會比 8 秒版本慢很多。  
目前 `generate-bgm-local.ps1` 已加入估計型進度條，但那不是模型的真實 token 百分比，只是方便判斷系統仍在工作中。

## Skill 安裝方式

這個專案已經內含 `musicgen-local` skill。

### 快速安裝腳本

在專案根目錄直接執行：

```powershell
.\install-skill.ps1
```

如果你想改用複製而不是 junction：

```powershell
.\install-skill.ps1 -Copy
```

### 方法 1：建立 junction（推薦）

這種方式不會複製檔案，之後你更新 repo，skill 也會同步更新。

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.codex\skills\musicgen-local" -Target "$PWD\skill"
```

如果該路徑已存在，先刪除舊的 skill：

```powershell
cmd /c rmdir "%USERPROFILE%\.codex\skills\musicgen-local"
```

再重新建立 junction。

### 方法 2：直接複製

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item .\skill "$env:USERPROFILE\.codex\skills\musicgen-local" -Recurse -Force
```

如果你用複製方式，之後 repo 更新時，`~/.codex/skills/musicgen-local` 不會自動同步。

## Skill 使用方式

安裝完成後，建議重啟 Codex。

之後你可以直接用：

```text
Use $musicgen-local to generate a loopable retro arcade puzzle game background track.
```

## 常見問題

### 1. 為什麼 30 秒比 8 秒慢很多？

因為 `MusicGen` 是本機模型，CPU 生成時間會隨長度上升而增加。  
30 秒通常明顯比短測試慢。

### 2. 為什麼終端機出現 `>>`？

那是 PowerShell 的續行提示，表示命令沒有正確結束，不代表模型還在生成。  
請直接執行：

```powershell
.\generate-bgm-local.ps1 -Seconds 30 -Seed 42
```

不要外面再包一層：

```powershell
powershell -ExecutionPolicy Bypass -File ...
```

### 3. 這個專案會自動保證完美 loop 嗎？

不會。  
這個工具是「生成 loop 風格背景音樂」，不是自動做 sample-accurate loop 裁切工具。  
若你要更精準的無縫 loop，建議在 DAW 裡再人工微調。

## 目前限制

- 預設使用 `facebook/musicgen-small`
- 以 CPU 模式為主
- 不處理自動剪輯 loop 點
- 不直接整合進 WinForms 或 Unity
- 不保證每次輸出完全一致的聽感，即使有 seed

## 授權

本專案原始碼、PowerShell 腳本、Python 腳本、skill 定義與文件，採用 `Apache License 2.0` 授權。

你可以：

- 免費使用
- 免費修改
- 免費商用
- 重新散布

但請保留：

- `LICENSE`
- `NOTICE`
- 原始版權與出處資訊

如果你要在 README、產品頁或文件中標示來源，建議使用：

```text
Based on MusicGenLocal by Lzxpan
```

補充說明：

- 本專案的授權只涵蓋本 repo 內的原始碼與 skill 內容。
- 透過模型生成的音樂成品，是否以及如何再授權，應由實際產出者自行決定。
- `facebook/musicgen-small` 屬於第三方模型，使用時仍應另外遵守其上游模型與平台條款。
