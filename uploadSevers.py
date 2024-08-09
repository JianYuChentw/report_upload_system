import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException
from utils import has_common_substring, resource_path

urls=[]

# 輪詢網頁
def load_website_with_retry(urls, headless, timeout=10):
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('detach', True)
        
        # 無頭模式啟用
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        chromedriver_path = os.path.abspath(os.path.join(os.getcwd(), resource_path("chromedriver-win64/chromedriver.exe")))
        print('驅動器位置',chromedriver_path)
        s=Service(chromedriver_path)

        driver = webdriver.Chrome(service=s, options=options )
     
        for url in urls:
            try:
                driver.set_page_load_timeout(timeout)
                driver.get(url)
                WebDriverWait(driver, timeout).until(lambda d: d.execute_script('return document.readyState') == 'complete')
                print(f"網頁在 {url} 成功加載")
                return driver # 成功加載，返回WebDriver實例
            except TimeoutException:
                print(f"加載 {url} 超時，嘗試下一個網址")
            except Exception as e:
                print(f"加載 {url} 時發生錯誤: {e}")

    except Exception as e:
            print(f"啟動 {url} 時發生錯誤: {e}")
            if driver:
                driver.quit()
            return False


def fastUpload(loginData, searchData):
    try:
        result=[]
        
        # 前往網站
        driver=load_website_with_retry(urls, False, 30)

        if not driver:
            result.append(creatCaseObject('', 'report', 404, "失敗", '網站讀取過久，請確認網頁是否阻塞，或網路是否正常'))
            return result
        
        # 取得帳號,密碼,登入鍵元素
        findMemberIdInput= driver.find_element(By.NAME, 'MemberID')
        findMemberPassworld_input= driver.find_element(By.NAME, 'MemberPW')
        findLoginBtn= driver.find_element(By.NAME, 'b1')

        # 輸入帳號密碼執行登入
        findMemberIdInput.send_keys(loginData['MemberID'])
        findMemberPassworld_input.send_keys(loginData['MemberPW'])
        findLoginBtn.click()
        try:
            alert = driver.switch_to.alert
            alertTexxt = alert.text
            print('出現彈窗警示:',alertTexxt) 
            alert.accept()
            result.append(creatCaseObject('', 'report', 404, "失敗", alertTexxt))
            return result
        except NoAlertPresentException:
            pass
            print('登入成功!')
            

        # 轉跳民眾檢舉系統
        findpublicReportBtn=driver.find_element(By.XPATH, '/html/body/table/tbody/tr[8]/td[1]/div/table/tbody/tr/td')
        findpublicReportBtn.click()
        # 切換視窗
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        print('轉跳民眾檢舉系統!')
        
        startWindoe= driver.window_handles
        # print('執行批量作業前的',startWindoe)
        print('執行批量作業')

        for obj in searchData:
                
            # 輸入檢舉案號執行檢索
            findReportCaseNo= WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, 'Sys_ReportCaseNo')))
            
            findReportCaseNo.clear()
            findReportCaseNo.send_keys(obj['caseNumber'])
                
            findSearchBtn= WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, 'btnSelt')))
            
            findSearchBtn.click() 

            
            # 指定目錄路徑和文件名前綴 

            current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    

            directoryPath = os.path.join(current_path, "rulingImg")

            print('上傳系統',directoryPath)

            # 初始化結果列表
            print('初始化案件圖片路徑!')

            # 無照片處理
            matchedFiles = []


            # 尋找資料夾
            for root, dirs, files in os.walk(directoryPath):
                for file in files:
                # 檢查文件名是否以指定的前綴開始且是 jpg 格式
                    if file.startswith(obj['caseNumber']) and file.lower().endswith('.jpg'):
                        filePath = os.path.join(root, file)
                        reverseSlash=filePath.replace('\\','/')
                        matchedFiles.append(reverseSlash)

            print(len(matchedFiles))
            


            if obj['report']:

                if len(matchedFiles)<1:
                    noImg = creatCaseObject(obj['caseNumber'], obj['report'], 400, "失敗", "無照片不執行上傳作業!")
                    result.append(noImg)
                    continue

                try:
                    print(f'尋照檢舉對象:{obj['caseNumber']}!')
                    reportBtn = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table/tbody/tr[2]/td[15]/input[2]')
                    print(f'發現案件:{obj['caseNumber']},選擇檢舉!')
                    reportBtn.click()
                    
                    windowsSecond = driver.window_handles
                    driver.switch_to.window(windowsSecond[-1])
                    try:
                        alert = driver.switch_to.alert
                        alertTexxt = alert.text
                        print('首次出現彈窗警示:',alertTexxt) 
                        alert.accept()
                    except NoAlertPresentException:
                        print('未出現彈窗警示')
                        pass
                except Exception as e:
                    noFinnd = creatCaseObject(obj['caseNumber'], obj['report'], 400, "失敗", "未找到該案件")
                    result.append(noFinnd)
                    continue



                try:
                    repeatedrReports="/html/body/form/table/tbody/tr[1]/td[3]/a"
                    findRepeatedr= driver.find_element(By.XPATH, repeatedrReports)
                    print(findRepeatedr.text)
                    result.append(creatCaseObject(obj['caseNumber'], 'report', 400, "失敗", '該案件有重複檢舉紀錄,請至智慧系統內核定'))
                    print('偵測七日內重複檢舉!')
                    driver.close()
                    driver.switch_to.window(windows[-1])
                    continue
                except Exception as e:
                    pass

                # # 切窗 third
                windowsThird = driver.window_handles
                # print('前往上傳區前的',windowsThird)
        

                #前往上傳區
                findToUpload= WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/table/tbody/tr[5]/td/input[8]')))
                findToUpload.click()
                time.sleep(1)

                # 切窗
                windowsFourth = driver.window_handles
                driver.switch_to.window(windowsFourth[-1])
                


                print('上傳指定照片!')
                # 上傳指定文件
                findUploadInput= WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/p[2]/input')))
                findUploadInput.send_keys(matchedFiles[0])

                # 執行上傳
                findUploadBtn1= WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/table[2]/tbody/tr/td/input[1]')))
                findUploadBtn1.click()
                wait = WebDriverWait(driver, 3)
                print(f'照片{obj['caseNumber']}-1完成!')
                
                alert = wait.until(EC.alert_is_present())

                alert.accept()

                # 回到前頁
                driver.switch_to.window(windowsThird[-1])
                
                try:
                    alert = driver.switch_to.alert
                    alertTexxt = alert.text
                    print('二次出現彈窗警示:',alertTexxt) 
                    alert.accept()
                except NoAlertPresentException:
                    print('未出現彈窗警示')
                    pass

                #前往上傳區
                findToUpload= WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/table/tbody/tr[5]/td/input[8]')))
                findToUpload.click()

                time.sleep(1)

                # 切窗 fifth
                windowsFifth = driver.window_handles
                driver.switch_to.window(windowsFifth[-1])

                # 上傳指定文件
                findUploadInput= WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/p[2]/input')))
                findUploadInput.send_keys(matchedFiles[1])

                # 執行上傳
                findUploadBtn2= WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/table[2]/tbody/tr/td/input[1]')))
                findUploadBtn2.click()
                wait = WebDriverWait(driver, 3)
                print(f'照片{obj['caseNumber']}-2完成!')
                alert = wait.until(EC.alert_is_present())
                alert.accept()
                time.sleep(1)

                # 回到前頁
          
                driver.switch_to.window(windowsThird[-1])
                try:
                    alert = driver.switch_to.alert
                    alertTexxt = alert.text
                    print('三次出現彈窗警示:',alertTexxt) 
                    alert.accept()
                except NoAlertPresentException:
                    print('未出現彈窗警示')
                    pass

                # 選擇車型
                findCarTypeInput= WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'CarSimpleID')))
                findCarTypeInput.send_keys(obj['carType'])
                print(f'輸入車型:{obj['carType']}!')
                

                windowsThird = driver.window_handles
                driver.switch_to.window(windowsThird[-1])
                findInformantBtn= WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table/tbody/tr[3]/td[4]/table/tbody/tr/td[1]/img')))
                findInformantBtn.click()
                
                # 切窗
                windowsFourth = driver.window_handles
                driver.switch_to.window(windowsFourth[-1])
                  
                time.sleep(1)
                # 輸入檢舉執行人
                try:
                    print(f'檢索檢舉執行人!')
                    xpathName=f"//td[text()='{loginData['InformantName']}']"
                    findName= driver.find_element(By.XPATH, xpathName)
                    findName.click()
                    print(f'選擇檢舉執行人:{loginData['InformantName']}!')
                except Exception as e:
                    noFinnd = creatCaseObject(obj['caseNumber'], obj['report'], 414, "失敗", "照片已完成上傳，未找到該檢舉人")
                    result.append(noFinnd)
                    return result
        
                driver.switch_to.window(windowsThird[-1])

                # # 變更法條
                if obj['adjustLaw']:
                    print('選擇變更法條')
                    findAdjustLawBtn = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table/tbody/tr[2]/td[4]/table/tbody/tr/td[1]/img[1]')
                    findAdjustLawBtn.click()
                    # 切窗
                    windowsFifth = driver.window_handles
                    driver.switch_to.window(windowsFifth[-1])

                    try:
                        findAdjustLawInput = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/input[1]')
                        findAdjustLawInput.clear()
                        print('輸入法條搜索')
                        findAdjustLawInput.send_keys(obj['lawOption1'])
                        AdjustLawSearchBtn = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td/input[3]')
                        AdjustLawSearchBtn.click()

                        # 取得法條
                        findAdjustLaw = driver.find_element(By.XPATH, '//*[@id="ItemID"]')
                        
                        # 預測可能有4次機會
                        adjustLawXpath=['/html/body/form/table/tbody/tr[6]/td[2]','/html/body/form/table/tbody/tr[7]/td[2]',
                                        '/html/body/form/table/tbody/tr[8]/td[2]', '/html/body/form/table/tbody/tr[9]/td[2]']

                        found = False
                
                        for xpath in adjustLawXpath:
                            print('迴圈:',xpath,(adjustLawXpath))

                            try:
                                findAdjustLaw = driver.find_element(By.XPATH, xpath)
                                AdjustLaweStr=findAdjustLaw.text.strip()
                                cartypeStr=str(obj['carType'])

                                if has_common_substring(AdjustLaweStr , '0'):
                                    print('找到車種0通用法條', '對應', 0)
                                    findAdjustLaw.click()
                                    found = True
                                    break
                                
                                if has_common_substring(AdjustLaweStr , cartypeStr):
                                    print('找到',AdjustLaweStr, '對應', cartypeStr)
                                    findAdjustLaw.click()
                                    found = True
                                    break


                            except NoSuchElementException:
                                # 如果未找到元素，等待一段時間後繼續嘗試
                                print('沒找到',cartypeStr)
                                time.sleep(1)
                                continue


                        if not found:
                            noFind = creatCaseObject(obj['caseNumber'], obj['report'], 414, "失敗", "照片已完成上傳，但未找到該法條編號")
                            result.append(noFind)
                            return result

                    except Exception as e:
                        noFinnd = creatCaseObject(obj['caseNumber'], obj['report'], 414, "失敗", "照片已完成上傳，但未找到該法條編號")
                        result.append(noFinnd)
                        return result

                driver.switch_to.window(windowsThird[-1])
                
                findSaveBtn= driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[5]/td/input[1]')
                time.sleep(2)
                ftxt=findSaveBtn.get_attribute('value')
                print('我在等待送出')
                print('點擊',ftxt)
                # findSaveBtn.click()

                # 預測彈窗 
                try:
                    WebDriverWait(driver, 10).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alertTexxt = alert.text
                    print('出現彈窗警示:',alertTexxt) 
                    alert.accept()
                    uploadResult=creatCaseObject(obj['caseNumber'], obj['report'], obj['carType'], "成功", "執行完畢")
                    result.append(uploadResult)
                except (NoAlertPresentException, TimeoutException) as e:
                    print('未出現彈窗警示', e)
                    uploadResult=creatCaseObject(obj['caseNumber'], obj['report'], obj['carType'], "失敗", "照片已完成上傳，網頁處理過久未收到成功回應。")
                    result.append(uploadResult)
                    pass

                driver.switch_to.window(windows[-1])


            else:
                uploadResult=creatCaseObject(obj['caseNumber'], obj['report'], obj['carType'], "成功", "因'不檢舉'未執行任何動作")
                result.append(uploadResult)
                # reportBtn= WebDriverWait(driver, 10)
                # .until(EC.visibility_of_element_located((By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table/tbody/tr[2]/td[15]/input[3]')))
                # reportBtn.click()
                # driver.switch_to.window(startWindoe[0])
                
                    
    except Exception as e:
                    noFinnd = creatCaseObject(obj['caseNumber'], obj['report'], 400, "失敗", "ERR")
                    result.append(noFinnd)
        
       
    finally:
        # 關閉瀏覽器視窗
        driver.quit() 
        # print('finally result',result)
        return result
    

# 定義回傳格式
def creatCaseObject(caseNumber, report, carType, operation, description):
     caseObject= {
        'caseNumber': caseNumber,
        'report': report,
        'carType': carType,
        'operation': operation,
        'description':description
        }
     return caseObject 
     
# 獲取車牌
def getPlateNumberFromCaseNumber(input_data, username, password):
    try:
        driver=None
        loginData = { 'account': username, 'password': password}
        results=[]
        status=True
        # 前往網站
        driver = load_website_with_retry(urls, True, 30)
        # print('driver',driver)
        if not driver:
            status=False
            results.append('網站讀取過久，請確認網頁是否阻塞，或網路是否正常。')
            return 

        # 取得帳號,密碼,登入鍵元素
        findMemberIdInput= driver.find_element(By.NAME, 'MemberID')
        findMemberPassworld_input= driver.find_element(By.NAME, 'MemberPW')
        findLoginBtn= driver.find_element(By.NAME, 'b1')

        # 輸入帳號密碼執行登入
        findMemberIdInput.send_keys(loginData['account'])
        findMemberPassworld_input.send_keys(loginData['password'])
        findLoginBtn.click()
        try:

            alert = driver.switch_to.alert
            alertTexxt = alert.text
            results.append(alertTexxt)
            print('出現彈窗警示:',alertTexxt) 
            alert.accept()
            status=False
           
            return

        except NoAlertPresentException: 
            print('未出現彈窗警示')
            pass
            
        # 轉跳民眾檢舉系統 
        print('登入成功!')

        findpublicReportBtn=driver.find_element(By.XPATH, '/html/body/table/tbody/tr[8]/td[1]/div/table/tbody/tr/td')
        findpublicReportBtn.click()
        # 切換視窗
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])

        print('執行批量車牌取得')

        for obj in input_data:
                
            # 輸入檢舉案號執行檢索
            findReportCaseNo= WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, 'Sys_ReportCaseNo')))
            
            findReportCaseNo.clear()
            findReportCaseNo.send_keys(obj)
                
            findSearchBtn= WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, 'btnSelt')))
            
            findSearchBtn.click()
            try:
                findPlateNumber = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table/tbody/tr[2]/td[5]')
                plateNumber=findPlateNumber.text
                print(plateNumber)
                
               
                reportBtn = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table/tbody/tr[2]/td[15]/input[2]')
                
                reportBtn.click()
                windowsSecond = driver.window_handles
                driver.switch_to.window(windowsSecond[-1])
                try:
                    alert = driver.switch_to.alert
                    alertTexxt = alert.text
                    print('出現彈窗警示:',alertTexxt) 
                    alert.accept()
                except NoAlertPresentException:
                    print('未出現彈窗警示')
                    pass
                
                # 取得法條
                adjustLawInput = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table/tbody/tr[2]/td[4]/table/tbody/tr/td[1]/input[1]')
                adjustLawValue=adjustLawInput.get_attribute('value')
                print('取得法條編號:', adjustLawValue)
                results.append({'caseNumber':obj, 'carNumber':plateNumber ,'adjustLaw':adjustLawValue})
                driver.switch_to.window(windows[-1])
            except Exception as e: 
                results.append({'caseNumber':obj, 'carNumber':'無對應車牌', 'adjustLaw':''})
                continue

    except Exception as e:
        status=False
        results.append('帳號密碼有誤或網頁操作發生錯誤，請重新再嘗試!')       
       
    finally:
        try:
            alert = driver.switch_to.alert
            alertTexxt = alert.text
            print('出現彈窗警示:',alertTexxt) 
            alert.accept()
        except NoAlertPresentException:
                # print('finall未出現彈窗警示')                    
                pass
        # 關閉瀏覽器視窗
        driver.quit() 
        # print('finally result',result)
        print(results)
        return {"status": status, "data": results, 'loginData':loginData }




