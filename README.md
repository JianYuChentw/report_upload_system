# **Report Upload System**

> **系統說明**  
> `Report Upload System` 是一款專為公家機關設計的系統介面，用於處理民眾檢舉案件。系統旨在簡化繁瑣的批量處理與上傳操作流程，提升工作效率。

---

# **main**

> **初次啟動說明**  
> 首次啟動系統時，會在當前資料夾的上層自動建立 `rulingImg` 資料夾，用於儲存案件照片。此外，系統還會在該資料夾內建立 `close_case` 資料夾，用於儲存結案照片。

---

# **Page1**

> **資料處理與監聽**  
> 系統會監聽 `rulingImg` 資料夾，以獲取並處理案件照片（篩選條件詳見註1）。  
> 當沒有符合條件的案件資料時，系統將顯示無法進行操作的 `A` 畫面，並持續監聽該資料夾。只有在讀取到至少一件符合篩選條件且具有兩張照片的案件後，才會切換至 `B` 畫面。

### **註1: 照片篩選條件**

- **檔名格式**：
  - 檔名必須以一個英文字母（大寫或小寫）開頭，後面跟隨11位數字。
  - 檔案必須以 `.jpg` 為副檔名（不區分大小寫）。

- **篩選條件**：
  - 只處理符合上述檔名格式且以 `.jpg` 結尾的檔案。
  - 如果某檔名部分（首位英文字母加上11位數字）在目錄中只出現一次，則忽略該檔案。
  - 保留檔名中獨特的部分，相同的檔名部分（如 "A12345678901"）只保留一個。

- **排序條件**：
  - 依據檔名中11位數字部分進行排序，排序順序為由大到小。

---

## **勾選功能**

> 系統允許勾選是否處理案件，支持全選（最多十筆）、部分勾選及取消勾選。

## **開啟監聽資料夾**

> 使用者可以手動開啟監聽資料夾，將案件檔案放入其中以供系統檢索。

## **開始檢索**

> 系統在開始檢索前需先登入帳號與密碼。檢索過程會從監聽資料夾中讀取符合條件的案件照片，並自動進行處理。

---

# **Page2**

> **資料與圖片渲染**  
> 系統將前往指定網站爬取案件對應的相關資料，並通過預設資料夾獲取案件照片，最終在此頁面中渲染展示。

## **圖片滾動縮放**

> 使用 `Ctrl+滑鼠滾輪` 可對照片進行縮放操作，便於查看細節。

## **資訊編輯**

> 使用者可對案件資訊進行編輯，包括檢舉與否、車牌號碼（可恢復原始資訊）、車型及修正條文等選項。若選擇不檢舉，則需提供相應的理由。

## **條文編號增刪**

> 因應法律條文可能發生變動，系統允許使用者在處理案件時增刪條文，提升靈活性。

## **開始處理（送出）**

> 當選定要檢舉的對象並完成資訊編輯後，使用者可輸入舉發人資訊並開始執行自動化爬蟲操作。

---

# **Page3**

> **案件處理與結果展示**  
> 系統將再次前往指定網站執行案件處理操作，並在此頁面中渲染結果。成功處理的案件，其對應的圖片將被移動至結案資料夾 `close_case` 中。

---

# **專案資訊**
- **軟體開發作者**: Jian-Yu Chen
- **聯絡方式**: [coke818572@gmail.com](mailto:email@example.com)
- **GitHub**: [JianYuChentw](https://github.com/JianYuChentw) 

**使用技術**
- **前端框架**: PyQt6
- **後端技術**: Python 3
- **資料監聽**: watchdog
- **自動化爬蟲**: Selenium 
- **版本控制**: Git
--- 
- **介面設計作者**: Lauren Huang
- **聯絡方式**: [rukihuang382@gmail.com](mailto:email@example.com)
- **Behance**: [Huang Lauren](https://www.behance.net/ruki38291d4)

