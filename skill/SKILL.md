---
name: musicgen-local
description: 在使用者的 Windows 機器上以 Meta MusicGen 本機生成遊戲配樂與可循環背景音樂。當 Codex 需要離線產生音樂、快速迭代 loop 風格提示詞、驗證本機 MusicGen 環境，或用命令列方式輸出 wav 音檔時使用。
---

# MusicGenLocal V0.91b

使用這個 skill 時，目標是透過 `facebook/musicgen-small` 在本機生成 `.wav` 音樂，並沿用專案內已建立好的 Python 環境與腳本。

## 安裝與前置

1. 專案根目錄為 `C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal`。
2. 若尚未建立環境，先執行：

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\setup-musicgen-local.ps1
```

3. 若要把 skill 安裝到 Codex，執行：

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\install-skill.ps1
```

4. 安裝後重新啟動 Codex。

## 使用方式

1. 優先用 `scripts/generate_music.py` 或 `generate-bgm-local.ps1`，不要重寫生成流程。
2. 若需求是快速測試 prompt，先生成 4 到 12 秒短片段。
3. 若需求是遊戲背景音樂，prompt 應包含 `instrumental only`、`seamless loop`、`no vocals`、`no spoken words`、`no dramatic intro`、`no fade-out outro`。
4. 產出後保留 `.wav`、`.prompt.txt` 與 `.json` 詳細資料，方便重現。
5. 若使用者改要圖形介面，改用 `musicgen-local-ui`。

## 常用指令

建立環境：

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\setup-musicgen-local.ps1
```

生成 8 秒測試版：

```powershell
C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\generate-bgm-local.ps1 -Seconds 8 -Seed 42
```

直接指定 prompt 檔：

```powershell
C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\skill\.venv\Scripts\python.exe C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\skill\scripts\generate_music.py --prompt-file C:\path\to\prompt.txt --out C:\Temp\music-loop.wav --seconds 8
```

## 相關檔案

- `scripts/setup_venv.ps1`：建立 `.venv` 並安裝依賴
- `scripts/generate_music.py`：本機生成核心 CLI
- `references/prompting.md`：loop / 遊戲 BGM prompt 參考

若工作重點是 GUI 啟動、參數面板、音檔庫管理或單檔 `exe`，請改用 `musicgen-local-ui`。