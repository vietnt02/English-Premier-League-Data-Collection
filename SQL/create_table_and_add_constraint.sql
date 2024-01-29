CREATE DATABASE EnglishPremierLeague
GO
USE EnglishPremierLeague
GO

CREATE TABLE teams (
	team_id INT PRIMARY KEY NOT NULL,
	team_name VARCHAR(50),
	founded_year INT,
	city VARCHAR(50),
	wins INT,
	draws INT,
	losses INT,
	total_yellow_cards INT,
	total_red_cards INT,
)

CREATE TABLE coaches (
	coach_id INT PRIMARY KEY NOT NULL,
	first_name NVARCHAR(50),
	last_name NVARCHAR(50),
	country VARCHAR(50),
	birth DATE,
	status VARCHAR(10),
	last_epl_team_id INT,
	matches INT,
	wins INT,
	draws INT,
	losses INT
	CONSTRAINT FK_coach_team_id FOREIGN KEY (last_epl_team_id) REFERENCES dbo.teams(team_id)
)

CREATE TABLE players (
	player_id INT PRIMARY KEY NOT NULL,
	first_name NVARCHAR(50),
	last_name NVARCHAR(50),
	position VARCHAR(50),
	country VARCHAR(50),
	birth DATE,
	appearances INT,
	clean_sheets INT,
	goals INT,
	assists INT,
	red_cards INT,
	yellow_cards INT
)

CREATE TABLE stadiums (
	stadium_id INT PRIMARY KEY NOT NULL,
	stadium_name VARCHAR(50),
	city VARCHAR(50),
	capacity INT
)

CREATE TABLE referees (
	referee_id INT PRIMARY KEY NOT NULL,
	first_name NVARCHAR(50),
	last_name NVARCHAR(50),
	appearances INT,
	red_cards INT,
	yellow_cards INT,
)

CREATE TABLE matches (
	match_id INT PRIMARY KEY NOT NULL,
	home_team_id INT,
	away_team_id INT,
	home_team_scores INT,
	away_team_scores INT,
	stadium_id INT,
	kickoff DATETIME,
	season CHAR(7),
	main_referee_id INT,
	attendance INT,
	CONSTRAINT FK_home_team_id FOREIGN KEY (home_team_id) REFERENCES dbo.teams(team_id),
	CONSTRAINT FK_away_team_id FOREIGN KEY (away_team_id) REFERENCES dbo.teams(team_id),
	CONSTRAINT FK_stadium_id FOREIGN KEY (stadium_id) REFERENCES dbo.stadiums(stadium_id),
	CONSTRAINT FK_main_referee_id FOREIGN KEY (main_referee_id) REFERENCES dbo.referees(referee_id)
)

CREATE TABLE goals (
	goal_id INT PRIMARY KEY NOT NULL,
	match_id INT,
	scorer_player_id INT,
	assist_player_id INT,
	time VARCHAR(10),
	scoring_team_id INT,
	CONSTRAINT FK_match_id FOREIGN KEY (match_id) REFERENCES dbo.matches(match_id),
	CONSTRAINT FK_scorer_player_id FOREIGN KEY (scorer_player_id) REFERENCES dbo.players(player_id),
	CONSTRAINT FK_assist_player_id FOREIGN KEY (assist_player_id) REFERENCES dbo.players(player_id),
	CONSTRAINT FK_scoring_team_id FOREIGN KEY (scoring_team_id) REFERENCES dbo.teams(team_id)
)
