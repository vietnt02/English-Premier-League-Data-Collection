/*
1. Based on the data collected, perform a query to get the rankings for all seasons
2. Perform a query to retrieve the matches with the largest difference in each season.
3. Perform a query to calculate the time taken to achieve a hattrick for each hattrick scored by a player in a match. Sort the results by the time taken in ascending order.
*/

-- 1. Based on the data collected, perform a query to get the rankings for all seasons
WITH MatchPoints AS (
    SELECT
        M.season,
        M.match_id,
        T1.team_name AS team,
        CASE 
            WHEN M.home_team_id = T1.team_id THEN
                CASE 
                    WHEN M.home_team_scores > M.away_team_scores THEN 3
                    WHEN M.home_team_scores = M.away_team_scores THEN 1
                    ELSE 0
                END
            WHEN M.away_team_id = T1.team_id THEN
                CASE 
                    WHEN M.home_team_scores < M.away_team_scores THEN 3
                    WHEN M.home_team_scores = M.away_team_scores THEN 1
                    ELSE 0
                END
        END AS points
    FROM
        dbo.matches M
        LEFT JOIN dbo.teams T1 ON M.home_team_id = T1.team_id

    UNION ALL

    SELECT
        M.season,
        M.match_id,
        T2.team_name AS team,
        CASE 
            WHEN M.away_team_id = T2.team_id THEN
                CASE 
                    WHEN M.home_team_scores < M.away_team_scores THEN 3
                    WHEN M.home_team_scores = M.away_team_scores THEN 1
                    ELSE 0
                END
            WHEN M.home_team_id = T2.team_id THEN
                CASE 
                    WHEN M.home_team_scores > M.away_team_scores THEN 3
                    WHEN M.home_team_scores = M.away_team_scores THEN 1
                    ELSE 0
                END
        END AS points
    FROM
        dbo.matches M
        LEFT JOIN dbo.teams T2 ON M.away_team_id = T2.team_id
)

SELECT 
    season,
    team,
    SUM(points) AS total_points,
    ROW_NUMBER() OVER(PARTITION BY MatchPoints.season ORDER BY SUM(points) DESC) AS season_rank
FROM MatchPoints
GROUP BY
    season,
    team
ORDER BY
    season,
    total_points DESC;

-- 2. Perform a query to retrieve the matches with the largest difference in each season.

SELECT
	M2.match_id
	, T.team_name AS home_team_name
	, TT.team_name AS away_team_name
	, M2.home_team_scores
	, M2.away_team_scores
	, M2.kickoff
	, M2.season
	, M2.attendance
FROM
	(
	SELECT
		*
		, RANK() OVER(PARTITION BY(season) ORDER BY ABS(M.home_team_scores - M.away_team_scores) DESC) AS rank_gd
	FROM 
		dbo.matches M
	) AS M2
	LEFT JOIN dbo.teams T ON T.team_id = M2.home_team_id
	LEFT JOIN dbo.teams TT ON TT.team_id = M2.away_team_id
WHERE
	M2.rank_gd = 1

-- 3. Perform a query to calculate the time taken to achieve a hattrick for each hattrick scored by a player in a match. Sort the results by the time taken in ascending order.

WITH for_hattrick AS (
	SELECT
		match_id
		, scorer_player_id
		, goal_id
		, LEFT(time, 2) AS new_time
		, COUNT(*) OVER(PARTITION BY match_id, scorer_player_id) AS match_goals
		, RANK() OVER(PARTITION BY match_id, scorer_player_id ORDER BY LEFT(time, 2)) AS goal_num
		, LAG(LEFT(time, 2),2) OVER(PARTITION BY match_id, scorer_player_id ORDER BY LEFT(time, 2)) AS lag_time
	FROM dbo.goals
	GROUP BY
		match_id
		, scorer_player_id
		, goal_id
		, LEFT(time, 2)
)

SELECT 
	for_hattrick.match_id
	, P.first_name + ' ' + P.last_name AS player_name
	, CONVERT(INT, for_hattrick.new_time) - CONVERT(INT, for_hattrick.lag_time) AS hattrick_time
FROM for_hattrick
	LEFT JOIN dbo.players P ON for_hattrick.scorer_player_id = P.player_id
WHERE
	for_hattrick.match_goals >= 3
	AND for_hattrick.lag_time IS NOT NULL
	AND P.first_name + ' ' + P.last_name IS NOT NULL
ORDER BY 
	hattrick_time
	, for_hattrick.match_id
