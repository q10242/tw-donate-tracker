import requests
import csv

# 設定搜尋 URL
base_url = "https://ardata.cy.gov.tw/api/v1/search"
data_url = "https://ardata.cy.gov.tw/api/v1/search/data"

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
data = requests.get(data_url).json()
data = data.get('classTypes', [])
type_mapping = {d['acctCd']: d['acctNm'] for d in data}

# 建立 CSV 檔案並寫入標題列
with open('donations.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = [
        '序號', '擬參選人/政黨', '參選公職名稱', '申報序號/年度', '交易日期', '收支科目', '捐贈者/支出對象', '身分證/統一編號', '收入金額', '支出金額',
        '支出用途', '金錢類', '地址', '聯絡電話', '返還/繳庫', '關聯政黨名稱', '關聯政黨職位', '關聯人與政黨關係', '不同版本說明','捐贈方式','存入專戶日期'
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
            print(f'已爬取 {name} 第 {current_page} 頁 , 共 {data.get("paging", {}).get("pageCount", 1)} 頁')
            if current_page < data.get('paging', {}).get('pageCount', 1):
                current_page += 1
            else:
                break

print("已將結果存儲為 donations.csv")
