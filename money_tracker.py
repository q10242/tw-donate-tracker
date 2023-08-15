import requests
import csv

# 設定搜尋 URL
base_url = "https://ardata.cy.gov.tw/api/v1/search"

# 讀取名單檔案
with open('name-list.txt', 'r', encoding='utf-8') as file:
    names = file.read().splitlines()

# 定義搜尋參數
params = {
    'page': 1,
    'pageSize': 1000,
    'orderBy': 'Date',
    'orderDirection': 'ASC',
    'keywordRanges': ['Candidate', 'PoliticalParty', 'Donor', 'ExpenditureTarget']
}

# 建立 CSV 檔案並寫入標題列
with open('donations.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = [
        '編號', '候選人/政黨', '選舉名稱', '年度/連任次數', '捐贈日期', '類別', '捐贈者', '統一編號', '收款金額', '捐款金額',
        '捐款用途', '是否為金錢', '捐贈者地址', '電話', '退還或支付', '關聯政黨名稱', '關聯政黨職位', '關聯人與政黨關係', '不同版本說明'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # 遍歷每個名字
    for name in names:
        params['keyword'] = name
        current_page = 1
        
        while True:
            params['page'] = current_page
            
            # 發送 GET 請求
            response = requests.get(base_url, params=params)
            
            # 解析 JSON 格式的回應
            data = response.json()
            
            # 取出資料部分
            donations = data.get('data', [])
            
            # 寫入 CSV 檔案
            for donation in donations:
                writer.writerow({
                    '編號': donation.get('id', 'N/A'),
                    '候選人/政黨': donation.get('name', 'N/A'),
                    '選舉名稱': donation.get('electionName', 'N/A'),
                    '年度/連任次數': donation.get('yearOrSerial', 'N/A'),
                    '捐贈日期': donation.get('transactionDate', 'N/A'),
                    '類別': donation.get('typeCode', 'N/A'),
                    '捐贈者': donation.get('donor', 'N/A'),
                    '統一編號': donation.get('donorIdentifier', 'N/A'),
                    '收款金額': donation.get('receivedAmount', 'N/A'),
                    '捐款金額': donation.get('donationAmount', 'N/A'),
                    '捐款用途': donation.get('donationUse', 'N/A'),
                    '是否為金錢': donation.get('isMoney', 'N/A'),
                    '捐贈者地址': donation.get('donorAddress', 'N/A'),
                    '電話': donation.get('tel', 'N/A'),
                    '退還或支付': donation.get('returnOrPaytrs', 'N/A'),
                    '關聯政黨名稱': donation.get('rpPartyName', 'N/A'),
                    '關聯政黨職位': donation.get('rpPartyTitle', 'N/A'),
                    '關聯人與政黨關係': donation.get('rpRelationStr', 'N/A'),
                    '不同版本說明': donation.get('diffVersionStr', 'N/A')
                })
            
            # 若還有下一頁，則繼續爬取
            print(f'已爬取 {name} 第 {current_page} 頁 , 共 {data.get("paging", {}).get("pageCount", 1)} 頁')
            if current_page < data.get('paging', {}).get('pageCount', 1):
                current_page += 1
            else:
                break

print("已將結果存儲為 donations.csv")
