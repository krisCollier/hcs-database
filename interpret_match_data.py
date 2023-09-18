from datetime import datetime

import pandas as pd
import components as cp
import output_components as oc

from os import listdir
from os.path import isfile, join

# Leafapp .csv

DIFFERENT_FILES = 3

# Options
autoPlayer = False
autoTeam = False

### Specify event DEFAULT=1 (Scrim)
eventID = 1

redTeam = cp.Team("Red", [])
blueTeam = cp.Team("Blue", [])


# FOLDER PROCESSING

def ContainsMatchTime(fileList):
    if str(fileList[0].replace(".csv", "")) in str(fileList[1]):
        return True
    return False


def GetFilesToProcess():
    fileList = GetFilesInFolder("TempSeriesData/")
    if (len(fileList) % DIFFERENT_FILES) != 0:
        print("Warning - Invalid file amount detected. Please check the files in the folder")
        return []
    return fileList


def GetFilesInFolder(folderPath):
    return [folderPath + filename for filename in listdir(folderPath) if isfile(join(folderPath, filename))]


def GetMatchLengthTxt(filepath):
    with open(filepath) as file:
        line = file.readline()
        return line


def GetMatchScoresTxt(filepath):
    with open(filepath) as file:
        line = file.readline()
        return line


def GetMatchScores(filepath):
    rawScores = GetMatchScoresTxt(filepath).split(",")
    if rawScores[0] > rawScores[1]:
        return rawScores[0], rawScores[1]
    else:
        return rawScores[1], rawScores[0]


def GetWinner(redTeam, redTeamMaps, blueTeam, blueTeamMaps):
    if redTeamMaps > blueTeamMaps:
        return redTeam, blueTeam, redTeamMaps, blueTeamMaps
    else:
        return blueTeam, redTeam, blueTeamMaps, redTeamMaps


def GetInitTeams(df):
    for i in range(0, len(df)):
        gamertag = df.iloc[i]['Player']
        win = df.iloc[i]['Outcome'] == "Win"
        if win:
            redTeam.AddPlayer(cp.Player(gamertag))
        else:
            blueTeam.AddPlayer(cp.Player(gamertag))

    redTeam.InitFromSQL()
    blueTeam.InitFromSQL()

    if redTeam.teamID == -1:
        redTeam.UpdateName(str(input(f"Please enter a team name for the following team: {redTeam}: \n")))
        redTeam.nation = (str(input(f"Please enter a nation for the following team: {redTeam}: \n")))
        redTeam.GetFromSQL()

    if blueTeam.teamID == -1:
        blueTeam.UpdateName(str(input(f"Please enter a team name for the following team: {blueTeam}: \n")))
        blueTeam.nation = (str(input(f"Please enter a nation for the following team: {blueTeam}: \n")))
        blueTeam.GetFromSQL()

    return redTeam, blueTeam

def GetPlayerIDFromTeams(gamertag, redTeam, blueTeam):
    if redTeam.IsGamertagInTeam(gamertag):
        return redTeam.GetPlayer(gamertag).playerID
    if blueTeam.IsGamertagInTeam(gamertag):
        return blueTeam.GetPlayer(gamertag).playerID
    return None

def GetPlayerTeam(player, teamOne: cp.Team, teamTwo: cp.Team):
    if teamOne.IsGamertagInTeam(player):
        return teamOne, teamTwo
    if teamTwo.IsGamertagInTeam(player):
        return teamTwo, teamOne
    print("ERROR - Player not in teams")
    return None, None


def GetWinnerFromDataFrame(df, redTeam: cp.Team, blueTeam: cp.Team):
    player = df.iloc[0]["Player"]
    win = df.iloc[0]["TeamOutcome"] == "Win"
    playerTeam, notPlayerTeam = GetPlayerTeam(player, redTeam, blueTeam)
    if win:
        return playerTeam, notPlayerTeam
    else:
        return notPlayerTeam, playerTeam


def GetRawMatchesFromDataFrame(df):
    rawMatches = []
    for index in range(8):
        rawMatches.append(cp.RawMatchData(df.iloc[index]))

    return rawMatches


def ProcessFile(files, redTeam, blueTeam):
    df = pd.read_csv(files[0])

    # Data for match
    mapWinner, notWinner = GetWinnerFromDataFrame(df, redTeam, blueTeam)
    winnerScore, loserScore = GetMatchScores(files[1])
    matchLen = GetMatchLengthTxt(files[2])
    gameType = df.iloc[0]["Category"]
    map = df.iloc[0]["Map"]
    dateTime = datetime.strptime(df.iloc[0]["Date"], '%Y-%m-%dT%H:%M:%SZ')

    # print(f"{dateTime} : {gameType} on {map} : {mapWinner.teamName} - {winnerScore} vs {loserScore} - {notWinner.teamName} ({matchLen})")
    match = cp.Match(str(dateTime), mapWinner, notWinner, gameType, map, winnerScore, loserScore, matchLen)
    match.rawMatches = [] # UNSURE WHY WE DO THIS
    match.AddRawMatches(GetRawMatchesFromDataFrame(df))

    for rawMatch in match.rawMatches:
        rawMatch.SetPlayerID(GetPlayerIDFromTeams(rawMatch.gamertag, redTeam, blueTeam))

    return match


def ProcessFiles(filesToProcess):
    redTeamMaps = 0
    blueTeamMaps = 0
    maps = []

    noOfFiles = len(filesToProcess)
    filesToProcess.sort()
    print(filesToProcess)

    # Process first file differently because we
    print(f"Currently processing: {filesToProcess[0]} (out of {int(noOfFiles / DIFFERENT_FILES)})")
    df = pd.read_csv(filesToProcess[0])
    redTeam, blueTeam = GetInitTeams(df)

    matchData = ProcessFile(filesToProcess[0:DIFFERENT_FILES], redTeam, blueTeam)
    maps.append(matchData)

    if matchData.winningTeam == redTeam:
        redTeamMaps += 1
    if matchData.winningTeam == blueTeam:
        blueTeamMaps += 1

    pointer = DIFFERENT_FILES
    while pointer < noOfFiles:
        print(f"Currently processing: {filesToProcess[pointer]} (out of {int(noOfFiles / DIFFERENT_FILES)})")
        matchData = ProcessFile(filesToProcess[pointer:pointer + DIFFERENT_FILES], redTeam, blueTeam)
        maps.append(matchData)

        if matchData.winningTeam == redTeam:
            redTeamMaps += 1
        if matchData.winningTeam == blueTeam:
            blueTeamMaps += 1

        pointer += DIFFERENT_FILES
    print("Processing complete")

    # Series init
    seriesWinner, seriesLoser, winnerMaps, loserMaps = GetWinner(redTeam, redTeamMaps, blueTeam, blueTeamMaps)
    seriesResult = cp.Series(eventID, seriesWinner, seriesLoser, str(maps[0].dateTime), winnerMaps, loserMaps)
    seriesResult.AddMatches(maps)

    # Result print for GUI
    print(seriesResult)
    seriesResult.ShowAllMatches()
    seriesResult.AddToSQL()

    curSeries = cp.SeriesOut(seriesResult.seriesID)
    oc.GenerateSeriesReport(curSeries)


# ProcessFiles(GetFilesToProcess())
