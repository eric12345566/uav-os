# UAV-OS: 無人機自動飛降作業系統

## 簡介
在畢業專題中，我們必須使用 Tello 在模擬環境中，做出一台可以根據室內定位座標與視覺影像辨識，來進行自動飛行、降落並且達到送貨目標的無人機。因為在開發中發現需要更有系統性的開發這套系統，因此生出了這個專案

## 基礎架構
將「自動飛降核心」、「影像辨識處理」與「Tello操控」分成好幾個執行緒來進行，並且由 UAVCore 來進行控制資料傳遞、全域狀態以及執行緒的狀態監測與操控。

## 使用方式
### 需求
* 建議使用 PyCharm IDE 來進行開發
* 使用 Pipenv 來進行虛擬環境、套件管理

### 安裝步驟
1. 使用 Pycharm 打開「uav-os」專案資料夾
2. 從 Pycharm 設定 Environment，新增一個 pipenv 環境，指定使用 python 3
3. 打開 Pycharm 終端機，輸入以下指令安裝套件
```
pipenv install
```

[pipenv 詳細教學](https://medium.com/@chihsuan/pipenv-%E6%9B%B4%E7%B0%A1%E5%96%AE-%E6%9B%B4%E5%BF%AB%E9%80%9F%E7%9A%84-python-%E5%A5%97%E4%BB%B6%E7%AE%A1%E7%90%86%E5%B7%A5%E5%85%B7-135a47e504f4)
