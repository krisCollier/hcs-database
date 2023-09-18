import pandas as pd
import dbms_commands as dbms
import xlsxwriter
from datetime import datetime


class Player:
    playerID = -1
    gamertag = ""
    forename = ""
    surname = ""
    nation = ""
    twitter = ""

    def __init__(self, gamertag):
        self.gamertag = gamertag
        self.GetFromSQL()

    def __str__(self):
        return f"{self.gamertag}"

    def SetPlayerID(self, id):
        self.playerID = id

    def GetAllPlayerDetails(self):
        print(f"{self.playerID}, {self.gamertag}, {self.forename}, {self.surname}, {self.nation}, {self.twitter}")

    def UpdateFromSQL(self, sqlData):
        self.playerID = int(sqlData[0])
        self.forename = sqlData[2]
        self.surname = sqlData[3]
        self.nation = sqlData[4]
        self.twitter = sqlData[5]

    def InitFromSQL(self):
        result = dbms.GetPlayerFromDatabase(self.gamertag)
        if result is not None:
            self.UpdateFromSQL(result)

    def GetFromSQL(self):
        result = dbms.GetPlayerFromDatabase(self.gamertag)
        if result is not None:
            self.UpdateFromSQL(result)
        else:
            self.AddToSQL()

    def AddToSQL(self):
        if self.playerID != -1:
            return
        newID = dbms.AddPlayerToDatabase(self.gamertag, self.forename, self.surname, self.nation, self.twitter)
        self.SetPlayerID(newID)

    def AddToTeamSQL(self, teamID):
        if teamID not in dbms.GetTeamIDsForPlayer(self.playerID):
            dbms.AddPlayerToTeam(self.playerID, teamID)

    def UpdateDetails(self):
        print("]--Updating player details--[\n"
              "-----------------------------")
        self.forename = str(input(f"Please enter a forename for: {self.gamertag}: \n"))
        self.surname = str(input(f"Please enter a surname for: {self.gamertag}: \n"))
        self.nation = str(input(f"Please enter a nation for: {self.gamertag}: \n"))
        self.twitter = str(input(f"Please enter a twitter for: {self.gamertag}: \n"))


class Team:
    teamID = -1
    teamName = ""
    nation = ""
    players = []

    def __init__(self, teamName, players):
        self.teamName = teamName
        self.players = players

    def __str__(self):
        if len(self.players) >= 4:
            return f"{self.teamID} {self.teamName} ({self.players[0]}, {self.players[1]}, {self.players[2]}, {self.players[3]})"
        return f"{self.teamID} {self.teamName} ({self.nation})"

    def SetTeamID(self, id):
        self.teamID = id

    def UpdateName(self, newName):
        self.teamName = newName

    def AddPlayer(self, player):
        self.players.append(player)

    def GetPlayer(self, gamertag):
        return list(player for player in self.players if player.gamertag == gamertag)[0]

    def UpdateAllPlayerDetails(self):
        for player in self.players:
            player.UpdateDetails()

    def UpdateFromSQL(self, sqlData):
        self.teamID = int(sqlData[0])
        self.teamName = sqlData[1]
        self.nation = sqlData[2]

    def InitFromSQL(self):
        playerIDs = list(player.playerID for player in self.players)
        teamData = dbms.GetTeamFromPlayers(playerIDs)
        if teamData is not None:
            self.UpdateFromSQL(dbms.GetTeamFromPlayers(playerIDs))

    def GetFromSQL(self):
        result = dbms.GetTeamFromTeamname(self.teamName)
        if result is not None:
            self.UpdateFromSQL(result)
        else:
            self.AddToSQL()
        self.AddPlayersToTeamSQL()

    def AddToSQL(self):
        newID = dbms.AddTeamToDatabase(self.teamName, self.nation)
        self.SetTeamID(newID)

    def AddPlayersToTeamSQL(self):
        if self.teamID == -1:
            return
        for player in self.players:
            player.AddToTeamSQL(self.teamID)

    def IsGamertagInTeam(self, name):
        return any(player for player in self.players if player.gamertag == name)


class Series:
    seriesID = -1
    winningTeam = ""
    losingTeam = ""
    winnerMaps = ""
    loserMaps = ""
    matches = []

    def __init__(self, eventID, winningTeam, losingTeam, datetime, winnerMaps, loserMaps):
        self.eventID = eventID
        self.winningTeam = winningTeam
        self.losingTeam = losingTeam
        self.datetime = datetime
        self.winnerMaps = winnerMaps
        self.loserMaps = loserMaps

    def __str__(self):
        return f"{self.datetime}: {self.winningTeam.teamName} {self.winnerMaps} - {self.loserMaps} {self.losingTeam.teamName}"

    def ShowAllMatches(self):
        for match in self.matches:
            print(match)

    def SetSeriesID(self, id):
        self.seriesID = id
        for match in self.matches:
            match.SetSeriesID(self.seriesID)

    def AddMatch(self, match):
        self.matches.append(match)

    def AddMatches(self, matches):
        for match in matches:
            self.matches.append(match)

    def AddToSQL(self):
        seriesID = dbms.GetSeriesIDFromTeamsAndDate(self.winningTeam.teamID, self.losingTeam.teamID, self.datetime)
        if seriesID is None:
            self.SetSeriesID(dbms.AddSeriesToDatabase(
                (self.eventID, self.winningTeam.teamID, self.losingTeam.teamID, self.datetime, self.winnerMaps,
                 self.loserMaps)))
            for match in self.matches:
                match.AddToSQL()
        else:
            print("ERROR>Series Already Added")
            print("SERIES FAILED TO ADD")


class Match:
    seriesID = -1
    matchID = -1
    gametype = ""
    map = ""
    winnerScore = 0
    loserScore = 0
    matchLength = 0
    rawMatches = []

    def __init__(self, dateTime, winningTeam, losingTeam, gametype, map, winnerScore, loserScore, matchLength):
        self.dateTime = dateTime
        self.map = map
        self.winningTeam = winningTeam
        self.losingTeam = losingTeam
        self.gametype = gametype
        self.map = map
        self.winnerScore = winnerScore
        self.loserScore = loserScore
        self.matchLength = matchLength

    def __str__(self):
        beforeColon = f"{self.dateTime} : {self.gametype} on {self.map}"
        return f"{beforeColon.ljust(50)}: {self.winningTeam.teamName} - {self.winnerScore} " \
               f"vs {self.loserScore} - {self.losingTeam.teamName} ({self.matchLength})"

    def SetSeriesID(self, id):
        self.seriesID = id

    def SetMatchID(self, id):
        """Update match ID and then all matchData's IDs"""
        self.matchID = id
        for match in self.rawMatches:
            match.SetMatchID(id)

    def AddRawMatches(self, matches):
        for match in matches:
            self.rawMatches.append(match)
        # print(f"{self.gametype} {self.map} Added {len(matches)} rawMatchDatas")

    def AddToSQL(self):
        self.SetMatchID(dbms.AddMatchToDatabase((self.seriesID, self.winningTeam.teamID, self.losingTeam.teamID,
                                                 self.dateTime, self.gametype, self.map, self.winnerScore,
                                                 self.loserScore, self.matchLength)))
        for match in self.rawMatches:
            match.AddToSQL()

    def PrintScoreboard(self):
        print("Gamertag  , K , A , D ,  KD  , dmgD , dmgT ,  Acc , shF , shL , Pe, Be, Su,  Scr ")
        for match in self.rawMatches:
            print(match)


class RawMatchData:
    matchID = -1
    playerID = -1
    gamertag = ""
    kills = 0
    deaths = 0
    assists = 0
    kd = 0
    damageDone = 0
    damageTaken = 0
    accuracy = 0
    shotsFired = 0
    shotsLanded = 0
    perfects = 0
    betrayals = 0
    suicides = 0
    score = 0

    def __init__(self, playerDataFrame):
        self.gamertag = playerDataFrame["Player"]
        self.kills = int(playerDataFrame["Kills"])
        self.deaths = int(playerDataFrame["Deaths"])
        self.assists = int(playerDataFrame["Assists"])
        self.kd = float(round(self.kills / self.deaths, 2))
        self.damageDone = int(playerDataFrame["DamageDone"])
        self.damageTaken = int(playerDataFrame["DamageTaken"])
        self.accuracy = float(playerDataFrame["Accuracy"])
        self.shotsFired = int(playerDataFrame["ShotsFired"])
        self.shotsLanded = int(playerDataFrame["ShotsLanded"])
        self.perfects = int(playerDataFrame["Perfects"])
        self.betrayals = int(playerDataFrame["Betrayals"])
        self.suicides = int(playerDataFrame["Suicides"])
        self.score = int(playerDataFrame["Score"])

    def __str__(self):
        return f"{self.gamertag.ljust(10)}, {str(self.kills).ljust(2)}, {str(self.assists).ljust(2)}, {str(self.deaths).ljust(2)}, " \
               f"{str(self.kd).ljust(5)}, {str(self.damageDone).ljust(5)}, {str(self.damageTaken).ljust(5)}, {str(self.accuracy).ljust(5)}, " \
               f"{str(self.shotsFired).ljust(4)}, {str(self.shotsLanded).ljust(4)}, {str(self.perfects).ljust(2)}, {str(self.betrayals).ljust(2)}, " \
               f"{str(self.suicides).ljust(2)}, {str(self.score).ljust(5)}"

    def SetMatchID(self, id):
        self.matchID = id

    def SetPlayerID(self, id):
        self.playerID = id

    def AddToSQL(self):
        if self.IDsAreValid():
            dbms.AddRawMatchDataToDatabase((self.matchID, self.playerID, self.kills, self.deaths, self.assists, self.kd,
                                            self.damageDone, self.damageTaken,
                                            self.accuracy, self.shotsFired, self.shotsLanded, self.perfects,
                                            self.betrayals, self.suicides, self.score))
        else:
            print("ERROR: invalid IDs")

    def IDsAreValid(self):
        return self.playerID != -1 and self.matchID != -1


""" DATA ACQUISITION CLASSES """


class SeriesOut:
    seriesID = -1
    eventName = ""
    winningTeam = ""
    losingTeam = ""
    winnerMaps = ""
    loserMaps = ""
    datetime = None
    matches = []

    def __init__(self, seriesID):
        seriesData = dbms.GetSeriesFromSeriesID(seriesID)
        self.seriesID = seriesID

        self.eventName = dbms.GetEventNameFromID(seriesData[1])
        self.winningTeam = dbms.GetTeamFromTeamID(seriesData[2])[1]
        self.losingTeam = dbms.GetTeamFromTeamID(seriesData[3])[1]
        self.datetime = seriesData[4]
        self.winnerMaps = seriesData[5]
        self.loserMaps = seriesData[6]

        self.GetMatches()

    def GetMatches(self):
        matchIDs = dbms.GetMatchesFromSeriesID(self.seriesID)
        for matchID in matchIDs:
            self.matches.append(MatchOut(matchID[0], self.seriesID))

    def WriteGameNumber(self, worksheet, row, gameNumber):
        headers = [
            "Game " + str(gameNumber)
        ]
        for col, dp in enumerate(headers):
            worksheet.write_column(row, col, [dp])

    def WriteToCSV(self):
        workbook = xlsxwriter.Workbook(self.GetSheetName())
        worksheet = workbook.add_worksheet()
        self.WriteSeriesHeader(worksheet)

        for x, match in enumerate(self.matches):
            self.WriteGameNumber(worksheet, (15 + 17 * x), x + 1)
            match.WriteMatchHeader(worksheet, (16 + 17 * x))
            self.WriteStatHeaders(worksheet, (18 + 17 * x))
            match.WriteStatlines(worksheet, (19 + 17 * x))

        workbook.close()

    def GetSheetName(self):
        return f'{self.datetime.strftime("%Y%m%d")}-{self.winningTeam}vs{self.losingTeam}.xlsx'

    def GetHeaders(self):
        return [
            self.eventName,
            self.winningTeam, self.winnerMaps,
            "vs",
            self.loserMaps, self.losingTeam,
            self.datetime.strftime("%d/%m/%Y, %H:%M")
        ]


class MatchOut:
    seriesID = -1
    matchID = -1
    gametype = ""
    map = ""
    winnerScore = 0
    loserScore = 0
    matchLength = ""
    statlines = []

    def __init__(self, matchID, seriesID):
        self.matchID = matchID
        self.seriesID = seriesID

        self.GetDataFromSQL()

        self.GetMatches()

    def GetDataFromSQL(self):
        matchData = dbms.GetMatchDataFromMatchID(self.matchID)

        self.dateTime = matchData[4]
        self.map = matchData[6]
        self.winningTeam = dbms.GetTeamFromTeamID(matchData[2])[1]
        self.losingTeam = dbms.GetTeamFromTeamID(matchData[3])[1]
        self.gametype = matchData[5]
        self.winnerScore = int(matchData[7])
        self.loserScore = int(matchData[8])
        self.matchLength = ConvertMatchLength(matchData[9])

    def GetMatches(self):
        # WHY DO I NEED TO CLEAR ARRAY
        self.statlines = []
        slayData = dbms.GetAllSlayDataForMatchID(self.matchID)
        for statline in slayData:
            matchData = MatchDataOut(statline)
            self.statlines.append(matchData)

    def WriteStatlines(self, worksheet, row):
        for i, statline in enumerate(self.statlines):
            self.WritePlayerData(statline.getDataDict(), worksheet, row + i)

    def WritePlayerData(self, statline, worksheet, row):
        print(statline.values())
        for col, dp in enumerate(statline.values()):
            worksheet.write_column(row, col, [dp])

    def GetHeaders(self):
        return [
            self.map,
            self.gametype, "",
            self.winningTeam,
            self.winnerScore, self.loserScore,
            self.losingTeam,
            "",
            self.matchLength
        ]

    def GetStatHeaders(self):
        return [
            "Gamertag", "K", "D", "A", "KD", "dmgD"
            , "dmgT", "Acc", "Fired", "Landed"
            , "Perf", "dmg%", "dmgD/K", "dmgD/D"
            , "dmgD/Min", "dmgT/K", "dmgT/D"
            , "dmgT/Min", "Land/D", "KA/D"
            , "dmg[+/-]", "[+/-]"
        ]


class MatchDataOut:
    """ RAW DATA """
    matchID = -1
    playerID = -1
    gamertag = ""
    kills = 0.0
    deaths = 0.0
    assists = 0.0
    kd = 0.0
    damageDone = 0.0
    damageTaken = 0.0
    accuracy = 0.0
    shotsFired = 0.0
    shotsLanded = 0.0
    perfects = 0.0
    betrayals = 0.0
    suicides = 0.0
    score = 0.0

    """ CALCULATED DATA """
    damageRatio = 0.0
    damageDonePerKill = 0.0
    damageDonePerDeath = 0.0
    damageDonePerMinute = 0.0
    damageTakenPerKill = 0.0
    damageTakenPerDeath = 0.0
    damageTakenPerMinute = 0.0
    shotsHitPerLife = 0.0
    kda = 0.0
    damageDiff = 0
    plusMinus = 0

    mapsPlayed = 0

    def __init__(self, sqlData):
        self.matchID = int(sqlData[0])
        self.playerID = int(sqlData[1])
        self.gamertag = dbms.GetPlayerFromID(self.playerID)[0]
        self.kills = int(sqlData[2])
        self.deaths = int(sqlData[3])
        self.assists = int(sqlData[4])
        self.kd = float(sqlData[5])
        self.damageDone = int(sqlData[6])
        self.damageTaken = int(sqlData[7])
        self.accuracy = float(sqlData[8])
        self.shotsFired = int(sqlData[9])
        self.shotsLanded = int(sqlData[10])
        self.perfects = int(sqlData[11])
        self.betrayals = int(sqlData[12])
        self.suicides = int(sqlData[13])
        self.score = int(sqlData[14])
        self.matchLength = int(dbms.GetMatchLengthFromMatchID(self.matchID))

        self.damageRatio = round(self.damageDone / self.damageTaken, 2)
        self.damageDonePerKill = round(self.damageDone / self.kills, 2)
        self.damageDonePerDeath = round(self.damageDone / self.deaths, 2)
        self.damageDonePerMinute = round(self.damageDone / (self.matchLength / 60), 2)
        self.damageTakenPerKill = round(self.damageTaken / self.kills, 2)
        self.damageTakenPerDeath = round(self.damageTaken / self.deaths, 2)
        self.damageTakenPerMinute = round(self.damageTaken / (self.matchLength / 60), 2)
        self.shotsHitPerDeath = round(self.shotsLanded / self.deaths, 2)
        self.kda = round((self.kills + self.assists) / self.deaths, 2)
        self.damageDiff = self.damageDone - self.damageTaken
        self.plusMinus = self.kills - self.deaths
        self.mapsPlayed = 1

    def getDataDict(self):
        dict = vars(self)
        try:
            dict.pop("playerID")
            dict.pop("matchID")
            dict.pop("matchLength")
            dict.pop("betrayals")
            dict.pop("suicides")
            dict.pop("score")
            dict.pop("mapsPlayed")
        except:
            return dict

        return dict

    def setMatchesPlayed(self, matchesPlayed):
        self.mapsPlayed = matchesPlayed

    def AddStatline(self, statline):
        self.kills = self.kills + statline.kills
        self.deaths = self.deaths + statline.deaths
        self.assists = self.assists + statline.assists
        self.damageDone = self.damageDone + statline.damageDone
        self.damageTaken = self.damageTaken + statline.damageTaken
        self.accuracy = self.accuracy + statline.accuracy
        self.shotsFired = self.shotsFired + statline.shotsFired
        self.shotsLanded = self.shotsLanded + statline.shotsLanded
        self.perfects = self.perfects + statline.perfects
        self.betrayals = self.betrayals + statline.betrayals
        self.suicides = self.suicides + statline.suicides
        self.score = self.score + statline.score
        self.matchLength = self.matchLength + statline.matchLength

        self.damageRatio = round(self.damageDone / self.damageTaken, 2)
        self.damageDonePerKill = round(self.damageDone / self.kills, 2)
        self.damageDonePerDeath = round(self.damageDone / self.deaths, 2)
        self.damageDonePerMinute = round(self.damageDone / (self.matchLength / 60), 2)
        self.damageTakenPerKill = round(self.damageTaken / self.kills, 2)
        self.damageTakenPerDeath = round(self.damageTaken / self.deaths, 2)
        self.damageTakenPerMinute = round(self.damageTaken / (self.matchLength / 60), 2)
        self.shotsHitPerDeath = round(self.shotsLanded / self.deaths, 2)
        self.kda = round((self.kills + self.assists) / self.deaths, 2)
        self.damageDiff = self.damageDone - self.damageTaken
        self.plusMinus = self.kills - self.deaths
        self.mapsPlayed += statline.mapsPlayed

    def CalculateAverages(self):
        self.kills = round(self.kills / self.mapsPlayed, 2)
        self.deaths = round(self.deaths / self.mapsPlayed, 2)
        self.assists = round(self.assists / self.mapsPlayed, 2)
        self.damageDone = round(self.damageDone / self.mapsPlayed, 2)
        self.damageTaken = round(self.damageTaken / self.mapsPlayed, 2)
        self.accuracy = round(self.accuracy / self.mapsPlayed, 2)
        self.shotsFired = round(self.shotsFired / self.mapsPlayed, 2)
        self.shotsLanded = round(self.shotsLanded / self.mapsPlayed, 2)
        self.perfects = round(self.perfects / self.mapsPlayed, 2)
        self.betrayals = round(self.betrayals / self.mapsPlayed, 2)
        self.suicides = round(self.suicides / self.mapsPlayed, 2)
        self.score = round(self.score / self.mapsPlayed, 2)
        self.matchLength = round(self.matchLength / self.mapsPlayed, 2)


def ConvertMatchLength(matchLen):
    mins = matchLen // 60
    secs = str(matchLen - (60 * mins)).zfill(2)
    return f"{mins}:{secs}"
