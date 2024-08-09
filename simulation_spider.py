import time
import random

# 模擬爬蟲相關操作

def run_vehicle_information_spider(input_data, username, password):
    """
    模擬爬蟲函數，根據輸入的案件編號匹配測試資料庫中的對應數據。

    參數:
    input_data (list): 案件編號列表
    username (str): 用戶名
    password (str): 密碼

    返回:
    dict: 包含爬取狀態、數據和登錄信息的字典
    """

    try:
        # 模擬登錄延遲
        time.sleep(1)

        # 假設登錄失敗
        loginTr = True
        if not loginTr:
            return {"status": False, "message": "登入失敗"}

        # 測試資料庫，包含一些示例數據
        testDb = [
            {'caseNumber': 'A00000000003', 'carNumber': 'CVB-5567', 'adjustLaw': '53821507', 'adjustLawcontent': '條文測試敘述'},
            {'caseNumber': 'A00000000006', 'carNumber': 'RVW-9642', 'adjustLaw': '34127640', 'adjustLawcontent': '條文測試敘述'},
            {'caseNumber': 'A00000000018', 'carNumber': 'ACA-9078', 'adjustLaw': '53821507', 'adjustLawcontent': '條文測試敘述'},
            {'caseNumber': 'A00000000257', 'carNumber': 'CVB-8890', 'adjustLaw': '77721507', 'adjustLawcontent': '條文測試敘述'},
            {'caseNumber': 'A00000000254', 'carNumber': 'CVB-5555', 'adjustLaw': '34127640', 'adjustLawcontent': '條文測試敘述'},
            {'caseNumber': 'A00000000260', 'carNumber': 'AAA-8888', 'adjustLaw': '34127640', 'adjustLawcontent': '條文測試敘述'},
            {'caseNumber': 'A66645678902', 'carNumber': 'GRE-1827', 'adjustLaw': '34127640', 'adjustLawcontent': '條文測試敘述'},
        ]

        results = []

        # 匹配輸入的案件編號與測試資料庫中的數據
        for case_number in input_data:
            matched = False
            for case in testDb:
                if case['caseNumber'] == case_number:
                    results.append(case)
                    matched = True
                    break  # 一旦找到匹配的對象，跳出內層循環
            if not matched:
                results.append({'caseNumber': case_number, 'carNumber': '無對應車牌', 'adjustLaw': '', 'adjustLawcontent': ''})

        loginData = {'account': username, 'password': password}
        # print(results)
        return {"status": True, "data": results, 'loginData': loginData}

    except Exception as e:
        # 捕捉通用異常並返回錯誤信息
        print(f"發生錯誤: {e}")
        return {"status": False, "message": f"發生錯誤: {e}"}


def batch_processing_spider(loginData, report_data):
    """
    模擬後台任務處理函數，根據輸入的報告數據生成結果。 
    其中有30%的機會會讓某些操作失敗。

    參數:
    loginData (dict): 包含登錄信息的字典
    report_data (list): 報告數據列表，每個元素是包含案件編號、報告狀態和車型的字典

    返回:
    list: 包含處理結果的字典列表，每個字典包含案件編號、報告狀態、車型、操作狀態和描述
    """
    
    results = []
    try:
        # 模擬處理時間
        time.sleep(1)  # 等待1秒鐘

        # 獲取操作和說明的初始值
        operation = "成功"
        description = "我是測試"

        # 處理 report_data 並生成輸出
        for data in report_data:
            case_number = data.get('caseNumber', 'N/A')
            report = data.get('report', False)
            car_type = data.get('carType', 'N/A')
            
            # 30% 的機會讓操作失敗
            if random.random() < 0.3:
                operation = "失敗"
                description = f'案件 {case_number} 的操作失敗。'
            else:
                operation = "成功"
                description = f'我是測試{case_number}。'
            
            result = {
                'caseNumber': case_number,
                'report': report,
                'carType': car_type,
                'operation': operation,
                'description': description,
            }
            
            results.append(result)

        return results

    except Exception as e:
        print(f"Error: {e}")
        return [{'caseNumber': 'Error', 'report': False, 'operation': 'error', 'description': str(e)}]
