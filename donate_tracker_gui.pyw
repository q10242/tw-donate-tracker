import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import requests
import csv
import threading

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    name_list_entry.delete(0, tk.END)
    name_list_entry.insert(0, file_path)

def start_crawling():
    text_output.insert(tk.END, f'程序開始\n')
    global stop_crawling  # 使用全域變數
    stop_crawling = False  # 重設停止爬取變數
    name_list_file = name_list_entry.get()
    if not name_list_file:
        messagebox.showerror("Error", "Please select a name list file.")
        return
    
    # Read the name list from the selected file
    with open(name_list_file, 'r', encoding='utf-8') as file:
        names = file.read().splitlines()
    
    # Set up crawling parameters
    base_url = "https://ardata.cy.gov.tw/api/v1/search"
    data_url = "https://ardata.cy.gov.tw/api/v1/search/data"
    params = {
        'page': 1,
        'pageSize': 500,
        'orderBy': 'Date',
        'orderDirection': 'ASC',
        'keywordRanges': ['Candidate', 'PoliticalParty', 'Donor', 'ExpenditureTarget']
    }
    data = requests.get(data_url).json()
    data = data.get('classTypes', [])
    type_mapping = {d['acctCd']: d['acctNm'] for d in data}
    
    # Create CSV file and write header
    output_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not output_file:
        messagebox.showerror("Error", "Please choose a location to save the CSV file.")
        return
    # Clear the text_output widget
    text_output.delete("1.0", tk.END)
   
    # 創建一個新的執行緒來運行爬取
    crawling_thread = threading.Thread(target=crawl_data, args=(names, base_url, params, type_mapping , output_file))
    crawling_thread.start()
        
def crawl_data(names, base_url, params, type_mapping, output_file):
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = [
            '序號', '擬參選人/政黨', '參選公職名稱', '申報序號/年度', '交易日期', '收支科目', '捐贈者/支出對象', '身分證/統一編號', '收入金額', '支出金額',
            '支出用途', '金錢類', '地址', '聯絡電話', '返還/繳庫', '關聯政黨名稱', '關聯政黨職位', '關聯人與政黨關係', '不同版本說明','捐贈方式','存入專戶日期'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # 遍歷每個名字
        for name in names:
            if stop_crawling:  # 檢查是否需要停止爬取
                crawl_info = f'已中斷爬取\n'
                text_output.insert(tk.END, crawl_info)
                return
            params['keyword'] = name
            current_page = 1
            
            while True:
                root.update()  # 更新 GUI
                text_output.insert(tk.END, f'正在爬取 {name} 第 {current_page} 頁\n')
                print(f'正在爬取 {name} 第 {current_page} 頁\n')
                params['page'] = current_page
                
                # 發送 GET 請求
                response = requests.get(base_url, params=params)
                
                # 解析 JSON 格式的回應
                data = response.json()
                
                # 取出資料部分
                donations = data.get('data', [])
                
                # 寫入 CSV 檔案
                for donation in donations:
                    acctCd = donation.get('typeCode', 'N/A')
                    acctNm = type_mapping.get(acctCd, 'N/A')
                    writer.writerow({
                        '序號': donation.get('id', 'N/A'),
                        '擬參選人/政黨': donation.get('name', 'N/A'),
                        '參選公職名稱': donation.get('electionName', 'N/A'),
                        '申報序號/年度': donation.get('yearOrSerial', 'N/A'),
                        '交易日期': donation.get('transactionDate', 'N/A'),
                        '收支科目': acctNm,
                        '捐贈者/支出對象': donation.get('donor', 'N/A'),
                        '身分證/統一編號': donation.get('donorIdentifier', 'N/A'),
                        '收入金額': donation.get('receivedAmount', 'N/A'),
                        '支出金額': donation.get('donationAmount', 'N/A'),
                        '支出用途': donation.get('donationUse', 'N/A'),
                        '金錢類': donation.get('isMoney', 'N/A'),
                        '地址': donation.get('donorAddress', 'N/A'),
                        '聯絡電話': donation.get('tel', 'N/A'),
                        '返還/繳庫': donation.get('returnOrPaytrs', 'N/A'),
                        '關聯政黨名稱': donation.get('rpPartyName', 'N/A'),
                        '關聯政黨職位': donation.get('rpPartyTitle', 'N/A'),
                        '關聯人與政黨關係': donation.get('rpRelationStr', 'N/A'),
                        '不同版本說明': donation.get('diffVersionStr', 'N/A'),
                        '捐贈方式': donation.get('payType', 'N/A'),
                        '存入專戶日期': donation.get('saveAccountDate', 'N/A')
                    })
                
                # 若還有下一頁，則繼續爬取
                crawl_info = f'已爬取 {name} 第 {current_page} 頁 , 共 {data.get("paging", {}).get("pageCount", 1)} 頁\n'
                print(crawl_info)
                text_output.insert(tk.END, crawl_info)
                if current_page < data.get('paging', {}).get('pageCount', 1):
                    current_page += 1
                else:
                    break
        text_output.insert(tk.END, f'爬取結束\n')

# 函數來中斷爬取
def stop_crawling_func():
    text_output.insert(tk.END, f'已經中斷爬取\n')
    global stop_crawling
    stop_crawling = True

# Create the main GUI window
root = tk.Tk()
root.title("政治獻金爬蟲程式")

# Create GUI components
name_list_label = tk.Label(root, text="關鍵字名單(一行一個關鍵字):")
name_list_entry = tk.Entry(root)
browse_button = tk.Button(root, text="選取檔案", command=browse_file)
start_button = tk.Button(root, text="開始爬蟲", command=start_crawling)


# Create a text widget for displaying crawling information
text_output = tk.Text(root, height=10, width=50)
text_output.pack(pady=10)

# Create the Stop Crawling button
stop_button = tk.Button(root, text="停止", command=stop_crawling_func)
stop_button.pack(pady=5)

# Place GUI components on the window
name_list_label.pack(pady=10)
name_list_entry.pack(fill=tk.X, padx=10)
browse_button.pack(pady=5)
start_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
