# Ha Health Record

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5.svg)](https://www.home-assistant.io/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/oaoomg/ha_health_record)](https://github.com/WOOWTECH/ha_health_record/releases)

[English](README.md) | **繁體中文**

一個用於追蹤家庭成員健康紀錄的 Home Assistant 自訂整合。透過專屬側邊欄面板，管理任何紀錄類型，支援完整時間軸、篩選和即時編輯功能。

![健康紀錄面板](screenshots/record-tab.png)

## 功能特色

- **多成員管理** - 為多位家庭成員獨立追蹤健康紀錄
- **彈性紀錄類型** - 內建類型（餵食、睡眠、體重、身高）加上無限自訂類型，可設定單位和預設數值
- **專屬側邊欄面板** - 完整功能的 UI，支援日期篩選、搜尋、類型切換、即時編輯和紀錄時間軸
- **Home Assistant 實體** - 每個紀錄類型會建立 sensor、number、button 和 text 實體，原生整合 HA
- **事件驅動自動化** - 觸發 `ha_health_record_record_logged` 事件，可用於自動化
- **CSV 匯出** - 將成員的所有紀錄匯出為 CSV 檔案
- **完全本地** - 所有資料儲存在 Home Assistant 本地，無雲端依賴

## 安裝方式

### HACS（建議）

1. 在 Home Assistant 中開啟 HACS
2. 點擊右上角的三點選單
3. 選擇 **自訂儲存庫**
4. 輸入儲存庫網址：`https://github.com/WOOWTECH/ha_health_record`
5. 選擇類別：**Integration**
6. 點擊 **新增**，然後在 HACS 整合列表中找到「Ha Health Record」並點擊 **下載**
7. 重新啟動 Home Assistant

### 手動安裝

1. 從 [GitHub Releases](https://github.com/WOOWTECH/ha_health_record/releases) 下載最新版本
2. 將 `custom_components/ha_health_record` 資料夾複製到 Home Assistant 的 `config/custom_components/` 目錄：
   ```
   config/
   └── custom_components/
       └── ha_health_record/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           ├── coordinator.py
           ├── const.py
           ├── sensor.py
           ├── number.py
           ├── button.py
           ├── text.py
           ├── panel.py
           └── frontend/
               ├── ha-health-record-panel.js
               └── sidebar-title.js
   ```
3. 重新啟動 Home Assistant

## 設定

### 新增第一位成員

1. 前往 **設定** > **裝置與服務**
2. 點擊 **+ 新增整合**
3. 搜尋 **Ha Health Record**
4. 輸入成員名稱（例如「寶寶小明」），可選填自訂 ID
5. 點擊 **送出**

![設定流程](screenshots/config-flow.png)

整合會自動建立側邊欄面板項目。

### 新增更多成員

對每位家庭成員重複上述設定流程。每位成員會有各自獨立的裝置、實體和資料儲存。

### 管理紀錄類型

紀錄類型可在側邊欄面板的 **設定** 分頁中新增、編輯或刪除。每個紀錄類型包含：
- **名稱** - 顯示名稱（例如「餵食」）
- **單位** - 測量單位（例如「ml」、「kg」、「cm」）
- **預設數值** - 固定值或「上次數值」模式，方便快速輸入

## 面板 UI

### 成員切換

在面板標題列切換家庭成員，或直接新增成員。

![成員切換](screenshots/member-switcher.png)

### 成員總覽

一覽總紀錄數、最新紀錄時間、紀錄類型數量及最新數值。

![成員總覽](screenshots/member-overview.png)

### 紀錄分頁

瀏覽完整紀錄時間軸，支援日期範圍篩選、文字搜尋和紀錄類型切換。點擊任一紀錄可展開編輯或刪除。

![紀錄分頁](screenshots/record-tab.png)

### 設定分頁

管理成員資訊、紀錄類型（新增/編輯/刪除），以及將資料匯出為 CSV。

![設定分頁](screenshots/settings-tab.png)

### 新增紀錄對話框

選擇類型、設定時間、輸入數值，並可選填備註來記錄新的健康紀錄。

![新增紀錄對話框](screenshots/add-record-dialog.png)

## 授權條款

本專案採用 [GNU 通用公共授權條款第 3 版](LICENSE) 授權。
