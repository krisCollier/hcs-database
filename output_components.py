import copy

import xlsxwriter

import components as cp


# def CalculateAverageMatchStatlines(statlines : cp.MatchDataOut):
#     statlines = []
#     for match in matches:
#         for statline in match.statlines:
#             if statline.gamertag not in

def CalculateAverageSeriesStatlines(series: cp.SeriesOut):
    averages = {}

    seriesStatlines = GetStatlinesFromSeries(series)

    for statline in seriesStatlines:
        toAdd = statline
        gamertag = statline.gamertag
        if GamertagInStatlinesDict(gamertag, averages):
            toAdd.AddStatline(averages[gamertag])
        averages[gamertag] = toAdd

    for player in averages.keys():
        averages[player].CalculateAverages()

    return averages


def GamertagInStatlinesArray(gamertag, statlines: [cp.MatchDataOut]):
    return gamertag in GetGamertagsInStatlines(statlines)


def GamertagInStatlinesDict(gamertag, statlinesDict):
    return statlinesDict.get(gamertag) is not None


def GetGamertagsInStatlines(statlines: [cp.MatchDataOut]):
    return [statline.gamertag for statline in statlines]


def GetStatlinesFromSeries(series: cp.SeriesOut):
    return [statline for match in copy.deepcopy(series.matches) for statline in match.statlines]


def GetStatlinesDataFromMatch(match: cp.MatchOut):
    return [statline.getDataDict().values() for statline in match.statlines.copy()]


""" CSV OUTPUT FUNCTIONS """


def GenerateSeriesReport(series: cp.SeriesOut):
    sheetname = series.GetSheetName()
    workbook = xlsxwriter.Workbook(sheetname)
    worksheet = workbook.add_worksheet()
    writeToSheet(worksheet, series.GetHeaders(), 0)

    writeToSheet(worksheet, STAT_HEADERS, 2)

    for matchNo, match in enumerate(series.matches):
        writeToSheet(worksheet, GetGameNumber(matchNo + 1), 18 + 20 * matchNo)
        writeToSheet(worksheet, match.GetHeaders(), 19 + 20 * matchNo)
        writeToSheet(worksheet, STAT_HEADERS, 20 + 20 * matchNo)
        writeRowsToSheet(worksheet, GetStatlinesDataFromMatch(match), 21 + 20 * matchNo)

    # avgData = CalculateAverageSeriesStatlines(series)
    # for j, key in enumerate(avgData.keys()):
    #     writeToSheet(worksheet, avgData[key].getDataDict().values(), 3+j)

    workbook.close()
    print(f"Generated {sheetname}")


def writeToSheet(sheet, data, row):
    for col, dp in enumerate(data):
        sheet.write_column(row, col, [dp])


def writeRowsToSheet(sheet, data, startRow):
    for row in range(startRow, startRow + len(data)):
        for col, dp in enumerate(data[row - startRow]):
            sheet.write_column(row, col, [dp])


def GetGameNumber(gameNumber):
    return [
        "Game " + str(gameNumber)
    ]

STAT_HEADERS = [
        "Gamertag", "K", "D", "A", "KD", "dmgD"
        , "dmgT", "Acc", "Fired", "Landed"
        , "Perf", "dmg%", "dmgD/K", "dmgD/D"
        , "dmgD/Min", "dmgT/K", "dmgT/D"
        , "dmgT/Min", "Land/D", "KA/D"
        , "dmg[+/-]", "[+/-]"
    ]


series = cp.SeriesOut(7)
# CalculateAverageSeriesStatlines(series)
GenerateSeriesReport(series)

# data = CalculateAverageStatlines(series)

# big data
# https://leafapp.co/scrims/228/players
# https://leafapp.co/scrims/234/players
# https://leafapp.co/scrims/236/players
