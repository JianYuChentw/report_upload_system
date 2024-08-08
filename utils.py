import json, shutil,os ,sys, re, glob
from collections import Counter

# 確保打包後檔案集中讀取
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 会创建一个临时文件夹，并把路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 讀取 JSON
def process_json_data(file_path):
    full_path = resource_path(file_path)
    if not os.path.exists(full_path):
        create_json_file(full_path)  # 如果檔案不存在，建立檔案
    with open(full_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 存檔json
def save_json_data(file_path, data):
    full_path = resource_path(file_path)
    with open(full_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# 建立JSON檔案 空陣列
def create_json_file(file_name):
    # 獲取桌面路徑
    current_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 構建文件的完整路徑
    file_path = os.path.join(current_path, file_name)
    
    # 初始化內容為空列表
    content = []
    
    # 檢查文件是否已存在，若不存在則建立
    if not os.path.exists(file_path):
        with open(file_path, 'w') as json_file:
            json.dump(content, json_file)
        print(f"文件 {file_path} 已建立，內容為空列表")
    else:
        print(f"文件 {file_path} 已經存在")

# 建立JSON檔案 空字典
def create_empty_dict_json_file(file_name):
    file_path = resource_path(file_name)
    
    # 確保資料夾存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 初始化內容為空字典
    content = {}

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(content, json_file, ensure_ascii=False, indent=4)
    print(f"文件 {file_path} 已建立，內容為空字典")


# 增加法條編號
def add_law_number(law_number):
    file_path = resource_path('resources/articleNumber.json')
    laws = process_json_data(file_path)
    if law_number not in laws:
        laws.append(law_number)
        save_json_data(file_path, laws)
        print(f"新增的條文編號: {law_number}")
    else:
        print(f"條文編號 {law_number} 已存在")

# 移除法條編號
def delete_law_number(law_number):
    file_path = resource_path('resources/articleNumber.json')
    laws = process_json_data(file_path)
    if law_number in laws:
        laws.remove(law_number)
        save_json_data(file_path, laws)
        print(f"刪除的條文編號: {law_number}")
    else:
        print(f"條文編號 {law_number} 不存在")

# 預存帳號密碼
def save_credentials(username, password):
    credentials = {'username': username, 'password': password}
    filename = resource_path('resources/credentials.json')

    with open(filename, 'w') as f:
        json.dump(credentials, f)

# 讀取預存帳號密碼
def load_credentials():
    filename = resource_path('resources/credentials.json')
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
                if not content:
                    return None, None
                credentials = json.loads(content)
                return credentials.get('username'), credentials.get('password')
        except (json.JSONDecodeError, KeyError):
            return None, None
    return None, None


# 儲存舉發人
# def save_informants(informants):
#     filename = resource_path('resources/informants.json')
#     with open(filename, 'w') as file:
#         json.dump(informants, file)

# # 讀取舉發人
# def load_informants():
#     filename = resource_path('resources/informants.json')
#     if os.path.exists(filename):
#         try:
#             with open(filename, 'r') as file:
#                 content = file.read().strip()
#                 if not content:
#                     return []
#                 return json.loads(content)
#         except json.JSONDecodeError:
#             return []
#     return []

# 捕捉檔名  #0619
def get_sorted_filenames(directory):
   # 定義檔名的正則表達式模式，匹配首位英文字母加上剛好11位數字的部分
   pattern = re.compile(r'^[A-Za-z]\d{11}')
  
   # 讀取資料夾中的所有檔案
   files = os.listdir(directory)
  
   # 過濾出符合條件的檔名
   filtered_files = [f for f in files if pattern.match(f) and f.lower().endswith('.jpg')]
  
   # 提取首位英文字母加上至少11位數字的部分並去掉 .jpg 擴展名
   extracted_files = [pattern.match(f).group() for f in filtered_files]
  
   # 計算每個提取的文件名出現的次數
   file_counts = Counter(extracted_files)
  
   # 移除只出現一次的項目
   filtered_extracted_files = [f for f in extracted_files if file_counts[f] > 1]
  
   # 移除重複的項目
   unique_files = list(set(filtered_extracted_files))
  
   # 依據數字部分由大到小排序，只取前11位數字進行比較
   sorted_files = sorted(unique_files, key=lambda x: int(re.search(r'\d{11}', x[1:12]).group()), reverse=True)
  
   return sorted_files

# 字串核對
def has_common_substring(str1, str2):
   # 找出str1中所有可能的子字串
   substrings1 = set()
   for i in range(len(str1)):
       for j in range(i + 1, len(str1) + 1):
           substrings1.add(str1[i:j])


   # 檢查str2中是否包含任何一個str1的子字串
   for i in range(len(str2)):
       for j in range(i + 1, len(str2) + 1):
           if str2[i:j] in substrings1:
               return True


   return False


# 移動檔案至指定資料夾
def move_matching_files(case_numbers, target_directory):
   
   # 定義來源資料夾
   fileName = 'rulingImg'
   current_path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
   directory = os.path.join(current_path, fileName)


   # 確保目標資料夾存在，如果不存在則創建
   print( case_numbers)
   os.makedirs(target_directory, exist_ok=True)


   for case_number in case_numbers:
       # 定義正則表達式模式，允許案號後面有其他字元
       pattern = re.compile(f"^{re.escape(case_number)}.*\.jpe?g$", re.IGNORECASE)
       search_pattern_jpg = os.path.join(directory, "*.jpg")
       search_pattern_jpeg = os.path.join(directory, "*.jpeg")


       # 搜尋符合的檔案
       all_image_paths = glob.glob(search_pattern_jpg) + glob.glob(search_pattern_jpeg)
       image_paths = [path for path in all_image_paths if pattern.match(os.path.basename(path))]
       image_paths = [path.replace("\\", "/") for path in image_paths]


       # 將對應檔案移入目標資料夾並打印檔名
       for image_path in image_paths:
            shutil.move(image_path, os.path.join(target_directory, os.path.basename(image_path)))
            print(f"Moved file: {os.path.basename(image_path)}")


# 過濾成功案件
def filter_successful_cases(data):
   # 過濾出 operation 為 '成功' 的 caseNumber
   successful_cases = [item['caseNumber'] for item in data if item['operation'] == '成功']
   return successful_cases

# 檢查桌面使否有rulingImg資料夾
def ensure_ruling_img_folder():
   
   current_path = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
   
   ruling_img_folder = os.path.join(current_path, "rulingImg")
   print('檢查是否有rulingImg資料夾',ruling_img_folder)
   close_case_folder = os.path.join(ruling_img_folder, "close_case")
  
   # 檢查並創建 rulingImg 資料夾
   if not os.path.exists(ruling_img_folder):
       os.makedirs(ruling_img_folder)
       print(f"已創建資料夾: {ruling_img_folder}")
   else:
       print(f"資料夾已存在: {ruling_img_folder}")
  
   # 檢查並創建 close_case 資料夾
   if not os.path.exists(close_case_folder):
       os.makedirs(close_case_folder)
       print(f"已創建資料夾: {close_case_folder}")
   else:
       print(f"資料夾已存在: {close_case_folder}")


# 儲存舉發人
def save_informants(informants):
    filename = resource_path('resources/informants.json')
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # 確保資料夾存在
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(informants, file, ensure_ascii=False, indent=4)  # 使用 indent=4 使 JSON 檔案更具可讀性

# 讀取舉發人
def load_informants():
    filename = resource_path('resources/informants.json')
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    create_empty_dict_json_file('resources/informants.json')
                    return {}
                data = json.loads(content)
                if isinstance(data, dict):
                    return data
                else:
                    create_empty_dict_json_file('resources/informants.json')
                    return {}
        except (json.JSONDecodeError, IOError):
            create_empty_dict_json_file('resources/informants.json')
            return {}
    else:
        create_empty_dict_json_file('resources/informants.json')
        return {}
