import urllib.request as req
import numpy as np
import pandas as pd
import ssl
import io
import cn2an

def getData(url, time, fileName):
    request = req.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    })
    # https 網站
    gcontext = ssl.SSLContext()
    with req.urlopen(request, context=gcontext) as response:
        data = response.read().decode("utf-8")
        sdata = io.StringIO(data)
        df = pd.read_csv(sdata)
        # 設定以【第二列英文】做為 dataframe 欄位標頭
        new_header = df.iloc[0] 
        df = df[1:] 
        df.columns = new_header
        # 新增欄位【df_name】
        df["df_name"] = time[0:3] + "_" + time[4] + "_" + fileName[0:2] + fileName[11]
        df.to_csv(time + fileName + ".csv", index=False, encoding="utf_8_sig")
        return df

def generateTime(fromTime, toTime):
    # 檢查 fromTime, toTime 格式是否為字 S前後數字為整數
    if not isinstance(fromTime, str):
        return
    if not isinstance(toTime, str):
        return
    if len(fromTime.split("S")) != 2:
        return
    if len(toTime.split("S")) != 2:
        return 
    try:
        int(fromTime.split("S")[0])
        int(fromTime.split("S")[1])
        int(toTime.split("S")[0])
        int(toTime.split("S")[1])
    except ValueError:
        print(ValueError)
        return

    # 以 S 切割字串，分成兩個部分
    first = fromTime.split("S")
    last = toTime.split("S")

    # 轉換成數字
    fromTimeYear = int(first[0])
    fromTimeSeason = int(first[1])
    toTimeYear = int(last[0])
    toTimeSeason = int(last[1])
    times = []

    # 開始依據數字補上中間的時間
    for i in range(fromTimeYear, toTimeYear+1):
        for j in range(1, 5):
            if i > fromTimeYear and i < toTimeYear:
                times.append(str(i) + "S" + str(j))
            elif i == fromTimeYear and j >= fromTimeSeason:
                times.append(str(fromTimeYear) + "S" + str(j))
            elif i == toTimeYear and j <= toTimeSeason:
                times.append(str(toTimeYear) + "S" + str(j))
    return times
              
def combineData(fromTime, toTime):
    times = generateTime(fromTime, toTime)
    # 請求的檔案名稱
    fileNames = ["A_lvr_land_A", "F_lvr_land_A", "H_lvr_land_B", "B_lvr_land_B", "E_lvr_land_A"] 
    dfAll = None
    for time in times:
        for fileName in fileNames:
            # 請求的網址
            pageURL = "https://plvr.land.moi.gov.tw//DownloadSeason?season=" + time + "&fileName=" + fileName + ".csv"
            print(pageURL)
            dfProcessed = getData(pageURL, time, fileName)
            if dfAll is None:
                dfAll = dfProcessed
            else:
                dfAll = dfAll.append(dfProcessed, ignore_index=True)
    dfAll.to_csv("dfAll.csv", index=False, encoding="utf_8_sig")
    return dfAll

# 先判斷是否為數值，再去掉 ["total floor number"] 欄位的"層"字，並且將中文轉為數字
def parseFloor(x):
    try:
        x_int = int(x)
        return x_int
    except ValueError:
        x = x.strip("層")
        x = cn2an.cn2an(x, "normal")
        return x

def generateFilterCsv(dfAll):
    dfAll["total floor number"] = dfAll["total floor number"].map(parseFloor, na_action="ignore")
    # 【主要用途】為【住家用】
    dfAll = dfAll[dfAll["main use"].str.contains("住家用", na=False)]
    # 【建物型態】為【住宅大樓】
    dfAll = dfAll[dfAll["building state"].str.contains("住宅大樓", na=False)]
    # 【總樓層數】需【大於等於十三層】
    dfAll = dfAll[dfAll["total floor number"] >= 13]
    # 從【df_all】篩選出結果,並輸出【filter.csv 檔案】
    dfAll.to_csv("filter.csv", index=False, encoding="utf_8_sig")
    return dfAll

def generateCountCsv(dfAll):
    # 計算【總件數】
    count = dfAll["df_name"].count()
    # 計算【總車位數】(透過交易筆棟數)
    # 取得車位右邊index的數值做加總
    def parseParking(x):
        x = x.split("車位")
        return int(x[1])
    dfAll["parking pen number"] = dfAll["transaction pen number"].map(parseParking, na_action="ignore")
    sumParkingSpace = dfAll["parking pen number"].sum()
    # 計算【平均總價元】
    dfAll["total price NTD"] = pd.to_numeric(dfAll["total price NTD"])
    avgPricing = dfAll["total price NTD"].mean()
    # 計算【平均車位總價元】
    dfAll["the berth total price NTD"] = pd.to_numeric(dfAll["the berth total price NTD"])
    avgParkingSpace = dfAll["the berth total price NTD"].sum() / sumParkingSpace
    # 從【df_all】計算出結果,並輸出【count.csv 檔案】
    dfCount = pd.DataFrame([[count, sumParkingSpace, avgPricing, avgParkingSpace]],
                            columns=["總件數", "總車位數", "平均總價元", "平均車位總價元"])
    dfCount.to_csv("count.csv", index=False, encoding="utf_8_sig")
    return dfCount

if __name__ == "__main__":
    dfAll = combineData("103S1","105S2")
    dfAllFiltered = generateFilterCsv(dfAll)
    dfCount = generateCountCsv(dfAllFiltered)