---
name: musicgen-local-ui
description: 啟動並操作 MusicGenLocal 的 Windows 圖形介面。當 Codex 需要開啟 MusicGenLocal 音樂工作站、以中文表單選擇風格與參數、管理已生成音檔、驗證 GUI 流程，或確認單檔 exe 行為時使用。
---

# MusicGenLocal UI V0.91b

這個 skill 專門處理 GUI 與單檔 `exe`，而不是命令列生成流程。

## 安裝與前置

1. 專案根目錄為 `C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal`。
2. 若尚未建立環境，先執行：

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\setup-musicgen-local.ps1
```

3. 若要把 GUI skill 安裝到 Codex，執行：

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\install-skill.ps1
```

4. 安裝後重新啟動 Codex。

## 使用方式

1. 需要 GUI 時，先啟動 `launch-musicgen-ui.ps1` 或直接啟動 `dist\MusicGenLocal-Studio.exe`。
2. 在左側用中文欄位設定 `風格`、`類型`、`樂器`、`情緒`、`節奏 / BPM`、`調性主音`、`大小調`、`時長`、`固定 Seed` 與 `補強描述`。
3. 檢查 `最終生成提示詞`，確認後加入生成佇列。
4. 在右側音檔庫執行播放、暫停、停止、更名、刪除、開啟資料夾、帶回設定。
5. 若需求改成 CLI 或 prompt 微調，改用 `musicgen-local`。

## 常用指令

啟動 GUI：

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\launch-musicgen-ui.ps1
```

建立單檔 exe：

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\build-portable-ui.ps1
```

直接執行單檔版：

```powershell
C:\Users\Admin\Desktop\俄羅斯方塊\MusicGenLocal\dist\MusicGenLocal-Studio.exe
```

## 相關檔案

- `launch-musicgen-ui.ps1`：GUI 啟動入口
- `build-portable-ui.ps1`：單檔 exe 打包腳本
- `musicgenlocal-ui.spec`：PyInstaller 設定
- `app/ui/main_window.py`：主視窗與中文介面

若工作重點是批次生成或直接下指令生音樂，請改用 `musicgen-local`。