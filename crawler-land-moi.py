import urllib.request as req
import numpy as np
import pandas as pd
import ssl
import io

"""1.開發【爬蟲程式】下載【內政部不動產時價登錄網 】中,【103年第1季】~【108年第2
季】、位於【臺北市/新北市/高雄市】的【不動產買賣】資料,【桃園市/臺中市】
的【預售屋買賣】資料,下載檔案格式選擇【CSV格式】,請選擇【非本期下載】。"""

def getData(url, time, fileName):
    request = req.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }) 
    gcontext = ssl.SSLContext()
    with req.urlopen(request, context=gcontext) as response:
        data = response.read().decode("utf-8")  # str type
        sdata = io.StringIO(data)
        df = pd.read_csv(sdata)
        df["df_name"] = time[0:3] + "_" + time[4] + "_" + fileName[0:2] + fileName[11]
        df.to_csv(time + fileName + ".csv", index=False, header=False, encoding="utf_8_sig")
        return df

def generateTime(fromTime, toTime):
    # 檢查 fromTime, toTime 格式是否正確，srting, S前面數字後面1~4
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
              
def combineData():
    times = generateTime("103S2","104S2")
    fileNames = ["A_lvr_land_A"] # , "F_lvr_land_A", "H_lvr_land_B", "B_lvr_land_B", "E_lvr_land_A"
    dfAll = None
    for time in times:
        for fileName in fileNames:
            pageURL = "https://plvr.land.moi.gov.tw//DownloadSeason?season=" + time + "&fileName=" + fileName + ".csv"
            dfProcessed = getData(pageURL, time, fileName)
            if dfAll is None:
                dfAll = dfProcessed
            else:
                dfAll = dfAll.append(dfProcessed)
    dfAll.to_csv("dfAll.csv", index=False, header=False, encoding="utf_8_sig")
    return dfAll

combineData()

"""2. 使用【pandas】套件,讀取所有檔名【 X_lvr_land_X 】的資料集,分別建立 dataframe 物
件,設定以【第二列英文】做為 dataframe 欄位標頭,並新增欄位【df_name】(內容請用
程式將資料補齊,例如: 106年第1季/新北市/不動產買賣 -> 106_1_F_A、 105年第2季/台中市
/預售屋買賣-> 105_2_B_B)。"""


# 3. 操作 dataframe 物件,將所有物件合併成【df_all】。
