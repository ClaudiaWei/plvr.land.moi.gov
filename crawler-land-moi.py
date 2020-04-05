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
    gcontext = ssl.SSLContext()
    with req.urlopen(request, context=gcontext) as response:
        data = response.read().decode("utf-8")  # str type
        sdata = io.StringIO(data)
        df = pd.read_csv(sdata)
        
        new_header = df.iloc[0] #grab the first row for the header
        df = df[1:] #take the data less the header row
        df.columns = new_header #set the header row as the df header

        df["df_name"] = time[0:3] + "_" + time[4] + "_" + fileName[0:2] + fileName[11]
        df.to_csv(time + fileName + ".csv", index=False, encoding="utf_8_sig")
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
            print(pageURL)
            dfProcessed = getData(pageURL, time, fileName)
            if dfAll is None:
                dfAll = dfProcessed
            else:
                dfAll = dfAll.append(dfProcessed, ignore_index=True)
    dfAll.to_csv("dfAll.csv", index=False, encoding="utf_8_sig")
    return dfAll

dfAll = combineData()

def parseFloor(x):
    x = x.strip("層")
    x = cn2an.cn2an(x, "normal")
    return x

dfAll['total floor number'] = dfAll['total floor number'].map(parseFloor, na_action='ignore')
dfAll = dfAll[dfAll['main use'].str.contains("住家用", na=False)]
dfAll= dfAll[dfAll['building state'].str.contains("住宅大樓", na=False)]
dfAll= dfAll[dfAll['total floor number'] >= 13]
dfAll.to_csv("filter.csv", index=False, encoding="utf_8_sig")


