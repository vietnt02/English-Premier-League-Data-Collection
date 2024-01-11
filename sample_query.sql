/*
Based on the data collected, perform a query to get the rankings for each season
*/

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
