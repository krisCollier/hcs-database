CREATE TABLE Players (
	PlayerID int NOT NULL IDENTITY(1,1) PRIMARY KEY,
	Gamertag varchar(30) NOT NULL UNIQUE,
	Forename varchar(40),
	Surname varchar(40),
	Nation varchar(40),
	Twitter varchar(40)
);

CREATE TABLE Teams (
	TeamID int NOT NULL IDENTITY(1,1) PRIMARY KEY,
	TeamName varchar(20) NOT NULL UNIQUE,
	Nation varchar(35)
);

CREATE TABLE EventNames (
	EventID int NOT NULL IDENTITY(1,1) PRIMARY KEY,
	EventName varchar(35) NOT NULL,
	StartedDate DateTime,
	EndedDate DateTime,
	Region varchar(15),
	Nation varchar(35)
);

CREATE TABLE TeamsToPlayers (
	TeamID int NOT NULL REFERENCES dbo.Teams(TeamID),
	PlayerID int NOT NULL REFERENCES dbo.Players(PlayerID),
	DateAdded Date NOT NULL,
	Active Bit NOT NULL,
	PRIMARY KEY(TeamID, PlayerID)
);

CREATE TABLE Series (
	SeriesID int NOT NULL IDENTITY(1,1) PRIMARY KEY,
	EventID int NOT NULL REFERENCES dbo.EventNames(EventID),
	Winning_TeamID int NOT NULL REFERENCES dbo.Teams(TeamID),
	Losing_TeamID int NOT NULL REFERENCES dbo.Teams(TeamID),
	DateTimeOfSeries DateTime,
	Winner_maps int,
	Loser_maps int
);

CREATE TABLE Matches (
	MatchID int NOT NULL IDENTITY(1,1) PRIMARY KEY,
	SeriesID int NOT NULL REFERENCES dbo.Series(SeriesID),
	Winning_TeamID int REFERENCES dbo.Teams(TeamID),
	Losing_TeamID int REFERENCES dbo.Teams(TeamID),
	DateTimeOfMatch DateTime,
	GameType varchar(15),
	Map varchar(20),
	Winner_score int,
	Loser_score int,
	Match_length int
);

CREATE TABLE SlayMatchData (
	MatchID int NOT NULL REFERENCES dbo.Matches(MatchID),
	PlayerID int NOT NULL REFERENCES dbo.Players(PlayerID), 
	Kills int,
	Deaths int,
	Assists int,
	KD float,
	DamageDone int,
	DamageTaken int,
	Accuracy float,
	ShotsFired int,
	ShotsLanded int,
	Perfects int,
	Betrayals int,
	Suicides int,
	Score int,
	PRIMARY KEY(MatchID, PlayerID)
);

CREATE TABLE MedalMatchData (
	MatchID int NOT NULL REFERENCES dbo.Matches(MatchID),
	PlayerID int NOT NULL REFERENCES dbo.Players(PlayerID), 
	Overkill int,
	Triple_Kill int,
	Double_Kill int,
	HailMary float,
	Killing_Spree int,
	Killing_Frenzy int,
	Shot_Caller int,
	Back_Smack float,
	Bomber int,
	Boxer int,
	Reversal int,
	Spotter int,
	Stick int,
	Hill_Guardian int,
	No_Scope int,
	Clock_Stop int,
	Grenadier int,
	Sneak_King int,
	Ballista int,
	Sharpshooter int,
	PRIMARY KEY(MatchID, PlayerID)
);