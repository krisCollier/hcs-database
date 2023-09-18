import time
import pyodbc as odbc
import logging
from collections import Counter

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('dbms_requests')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('dbms_requests.log')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.propagate = False


def GetConnection():
    DRIVER_NAME = 'SQL SERVER'
    SERVER = 'MARKNOBLESRIGHT\SQLEXPRESS'
    DATABASE = 'UHCL-Scrim-Data'

    connection_str = f"""
        DRIVER={{{DRIVER_NAME}}};
        SERVER={SERVER};
        DATABASE={DATABASE};
        Trust_Connection=yes;
    """
    return odbc.connect(connection_str)


def CloseConnection(connection):
    connection.close()

""" EVENTNAMES """

def GetEventNameFromID(eventID):
    queryVar = (eventID,)
    query = f'SELECT EventName FROM dbo.EventNames WHERE EventID=?;'
    output = SelectOneQuery(query, queryVar)
    if output is not None:
        return output[0]
    return None

""" PLAYERS """


def GetPlayerFromDatabase(gamertag):
    logger.info(f"SELECT {gamertag} FROM dbo.Players")
    cnxn = GetConnection()
    cursor = cnxn.cursor()
    queryVar = (gamertag,)
    cursor.execute(f'SELECT * FROM dbo.Players WHERE Gamertag=?;', queryVar)
    return cursor.fetchone()


def GetPlayerIDFromDatabase(gamertag):
    logger.info(f"SELECT PlayerID OF {gamertag} FROM dbo.Players")
    cnxn = GetConnection()
    cursor = cnxn.cursor()
    queryVar = (gamertag,)
    cursor.execute(f'SELECT PlayerID FROM dbo.Players WHERE Gamertag=?;', queryVar)
    return cursor.fetchone()[0]


def AddPlayerToDatabase(gamertag, forename, surname, nation, twitter):
    cnxn = GetConnection()
    cursor = cnxn.cursor()
    queryVar = (gamertag, forename, surname, nation, twitter)
    logger.info(f"INSERT {queryVar} INTO dbo.Players")
    cursor.execute("INSERT INTO dbo.Players VALUES (?, ?, ?, ?, ?)", queryVar)
    cnxn.commit()
    return GetPlayerIDFromDatabase(gamertag)


def GetPlayerFromID(id):
    queryVar = (id,)
    query = f'SELECT Gamertag FROM dbo.Players WHERE PlayerID=?;'
    return SelectOneQuery(query, queryVar)


def GetTeamFromPlayers(players):
    teamID = GetTeamIDFromPlayers(players)
    return GetTeamFromTeamID(teamID)


def GetTeamFromTeamname(teamname):
    queryVar = (teamname,)
    query = f'SELECT * FROM dbo.Teams WHERE TeamName=?;'
    return SelectOneQuery(query, queryVar)


def GetTeamFromTeamID(teamID):
    queryVar = (teamID,)
    query = f'SELECT * FROM dbo.Teams WHERE TeamID=?;'
    return SelectOneQuery(query, queryVar)


def GetTeamIDFromPlayers(playerIDs):
    queryVar = (playerIDs[0], playerIDs[1], playerIDs[2], playerIDs[3])
    query = f'SELECT TeamID FROM dbo.TeamsToPlayers WHERE PlayerID = ? OR PlayerID = ? OR PlayerID = ? OR PlayerID = ?;'
    return TryGetTeamIDFromResult(SelectAllQuery(query, queryVar))


def TryGetTeamIDFromResult(resultQuery):
    queryArr = []
    teamID = -1

    for el in resultQuery:
        queryArr.append(el[0])

    for index, cnt in enumerate(Counter(queryArr).values()):
        if cnt == 4:
            teamID = list(Counter(queryArr).keys())[0]
            break
    return teamID


def GetTeamIDFromTeamname(teamname):
    queryVar = (teamname,)
    query = f'SELECT TeamID FROM dbo.Teams WHERE TeamName=?;'
    return SelectOneQuery(query, queryVar)[0]


def AddTeamToDatabase(teamname, nation):
    queryVar = (teamname, nation)
    query = "INSERT INTO dbo.Teams VALUES (?, ?)"
    InsertQuery(query, queryVar)
    return GetTeamIDFromTeamname(teamname)


def GetTeamIDsForPlayer(playerID):
    queryVar = (playerID,)
    query = f'SELECT TeamID FROM dbo.TeamsToPlayers WHERE PlayerID=?;'
    teamIDs = SelectAllQuery(query, queryVar)
    return [teamIDs[0] for teamIDs in teamIDs]


def AddPlayerToTeam(playerID, teamID):
    queryVar = (teamID, playerID, time.strftime('%Y-%m-%d'), True)
    query = "INSERT INTO dbo.TeamsToPlayers VALUES (?, ?, ?, ?)"
    InsertQuery(query, queryVar)


def MakePlayerTeamsInactive(playerID):
    queryVar = (False, playerID)
    query = "UPDATE dbo.TeamsToPlayers SET Active = ? WHERE PlayerID = ?"
    InsertQuery(query, queryVar)


""" SERIES """


def GetSeriesIDFromTeamsAndDate(winningTeam, losingTeam, dateTime):
    queryVar = (winningTeam, losingTeam, dateTime)
    query = f'SELECT SeriesID FROM dbo.Series WHERE Winning_TeamID = ? AND Losing_TeamID = ? AND DateTimeOfSeries = ?;'
    output = SelectOneQuery(query, queryVar)
    if output is not None:
        return output[0]
    return None


def AddSeriesToDatabase(queryVar):
    series = GetSeriesByAllVars(queryVar)
    if series is None:
        query = "INSERT INTO dbo.Series VALUES (?, ?, ?, ?, ?, ?)"
        InsertQuery(query, queryVar)
        return GetSeriesIDFromTeamsAndDate(queryVar[1], queryVar[2], queryVar[3])
    return series[0]


def GetSeriesByAllVars(queryVar):
    query = f'SELECT SeriesID FROM dbo.Series WHERE Winning_TeamID = ? AND Losing_TeamID = ? AND DateTimeOfSeries = ? AND Winner_maps = ? AND Loser_maps = ?;'
    return SelectOneQuery(query, queryVar[1:])

def GetSeriesFromSeriesID(seriesID):
    queryVar = (seriesID, )
    query = f'SELECT * FROM dbo.Series WHERE SeriesID = ?;'
    return SelectOneQuery(query, queryVar)

""" MATCH DATA """


def AddMatchToDatabase(queryVar):
    query = "INSERT INTO dbo.Matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    InsertQuery(query, queryVar)
    return GetMatchIDFromSeriesIDAndDateTime(queryVar[0], queryVar[3])


def GetMatchIDFromSeriesIDAndDateTime(seriesID, dateTime):
    queryVars = (seriesID, dateTime)
    query = f'SELECT MatchID FROM dbo.Matches WHERE SeriesID = ? AND DateTimeOfMatch = ?;'
    return SelectOneQuery(query, queryVars)[0]

def GetMatchLengthFromMatchID(matchID):
    queryVar = (matchID, )
    query = f'SELECT Match_Length FROM dbo.Matches WHERE MatchID = ?;'
    output = SelectOneQuery(query, queryVar)
    if output is not None:
        return output[0]
    return None

def GetMatchesFromSeriesID(seriesID):
    queryVar = (seriesID,)
    query = f'SELECT MatchID FROM dbo.Matches WHERE SeriesID = ? ORDER BY DateTimeOfMatch ASC;'
    return SelectAllQuery(query, queryVar)

def GetMatchDataFromMatchID(matchID):
    queryVar = (matchID,)
    query = f'SELECT * FROM dbo.Matches WHERE MatchID = ?;'
    return SelectOneQuery(query, queryVar)



""" SLAY MATCH DATA"""


def AddRawMatchDataToDatabase(queryVar):
    query = "INSERT INTO dbo.SlayMatchData VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    InsertQuery(query, queryVar)


def GetSlayDataFromIDs(matchID, playerID):
    queryVars = (matchID, playerID)
    query = f'SELECT * FROM dbo.SlayMatchData WHERE MatchID = ? AND PlayerID = ?;'
    return SelectOneQuery(query, queryVars)

def GetAllSlayDataForMatchID(matchID):
    queryVars = (matchID, )
    query = f'SELECT * FROM dbo.SlayMatchData WHERE MatchID = ?;'
    return SelectAllQuery(query, queryVars)

""" MAIN QUERIES """


def SelectOneQuery(query, variables):
    logger.info(f"{query} with {variables}")
    cnxn = GetConnection()
    cursor = cnxn.cursor()
    cursor.execute(query, variables)
    data = cursor.fetchone()
    cursor.close()
    cnxn.close()
    return data


def SelectAllQuery(query, variables):
    logger.info(f"{query} with {variables}")
    cnxn = GetConnection()
    cursor = cnxn.cursor()
    cursor.execute(query, variables)
    data = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return data


def InsertQuery(query, variables):
    logger.info(f"{query} with {variables}")
    cnxn = GetConnection()
    cursor = cnxn.cursor()
    cursor.execute(query, variables)
    cnxn.commit()
    cursor.close()
    cnxn.close()
