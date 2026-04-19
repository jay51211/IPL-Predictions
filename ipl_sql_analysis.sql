-- =============================================================
-- IPL Analytics & Match Intelligence Platform
-- SQL Analysis File
-- Author: Jay Kumbhar
-- Dataset: matches.csv + deliveries.csv (IPL 2008–2022)
-- =============================================================
-- HOW TO USE:
-- 1. Load matches.csv into a table called `matches`
-- 2. Load deliveries.csv into a table called `deliveries`
-- 3. Run queries in any SQL engine (MySQL / PostgreSQL / SQLite)
-- =============================================================


-- =============================================================
-- SECTION 1: TOURNAMENT OVERVIEW
-- =============================================================

-- Q1. Total number of IPL matches played across all seasons
SELECT COUNT(*) AS total_matches
FROM matches;


-- Q2. Total matches played per season
SELECT season, COUNT(*) AS matches_played
FROM matches
GROUP BY season
ORDER BY season;


-- Q3. Number of unique teams that have participated
SELECT COUNT(DISTINCT team) AS total_teams
FROM (
    SELECT team1 AS team FROM matches
    UNION
    SELECT team2 AS team FROM matches
) AS all_teams;


-- =============================================================
-- SECTION 2: TEAM PERFORMANCE
-- =============================================================

-- Q4. All-time wins leaderboard (Top 10 teams)
SELECT winner, COUNT(*) AS total_wins
FROM matches
WHERE winner IS NOT NULL AND winner != ''
GROUP BY winner
ORDER BY total_wins DESC
LIMIT 10;


-- Q5. Win percentage by team (teams with 50+ matches)
SELECT
    team,
    total_matches,
    total_wins,
    ROUND((total_wins * 100.0 / total_matches), 2) AS win_pct
FROM (
    SELECT
        t.team,
        COUNT(DISTINCT m.id) AS total_matches,
        SUM(CASE WHEN m.winner = t.team THEN 1 ELSE 0 END) AS total_wins
    FROM (
        SELECT team1 AS team FROM matches
        UNION ALL
        SELECT team2 AS team FROM matches
    ) t
    JOIN matches m ON m.team1 = t.team OR m.team2 = t.team
    GROUP BY t.team
) AS stats
WHERE total_matches >= 50
ORDER BY win_pct DESC;


-- Q6. Season-wise champions (winner of the final each season)
SELECT season, winner AS champion
FROM matches
WHERE match_type = 'Final'
   OR result_margin = (
       SELECT MAX(result_margin) FROM matches m2
       WHERE m2.season = matches.season
   )
ORDER BY season;

-- Simpler version if match_type column not available:
SELECT season, winner AS season_winner, COUNT(*) AS wins_in_season
FROM matches
WHERE winner IS NOT NULL
GROUP BY season, winner
ORDER BY season, wins_in_season DESC;


-- Q7. Home vs Away wins analysis
-- (home = city of team matches their home city approximation)
SELECT
    team1 AS home_team,
    COUNT(*) AS home_matches,
    SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) AS home_wins,
    ROUND(SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS home_win_pct
FROM matches
GROUP BY team1
HAVING COUNT(*) >= 20
ORDER BY home_win_pct DESC;


-- =============================================================
-- SECTION 3: TOSS ANALYSIS
-- =============================================================

-- Q8. Does winning the toss help win the match?
SELECT
    COUNT(*) AS total_matches,
    SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS toss_winner_won,
    ROUND(SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS toss_win_match_win_pct
FROM matches
WHERE winner IS NOT NULL AND winner != '';


-- Q9. Bat first vs field first — which decision wins more?
SELECT
    toss_decision,
    COUNT(*) AS times_chosen,
    SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) AS won_after_toss,
    ROUND(SUM(CASE WHEN toss_winner = winner THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_pct
FROM matches
WHERE winner IS NOT NULL AND winner != ''
GROUP BY toss_decision;


-- Q10. Toss decision preference by team
SELECT
    toss_winner AS team,
    SUM(CASE WHEN toss_decision = 'field' THEN 1 ELSE 0 END) AS chose_field,
    SUM(CASE WHEN toss_decision = 'bat' THEN 1 ELSE 0 END) AS chose_bat,
    COUNT(*) AS total_tosses_won
FROM matches
GROUP BY toss_winner
ORDER BY total_tosses_won DESC
LIMIT 10;


-- =============================================================
-- SECTION 4: BATTING ANALYSIS
-- =============================================================

-- Q11. Top 10 run scorers of all time
SELECT
    batsman,
    SUM(batsman_runs) AS total_runs,
    COUNT(DISTINCT match_id) AS matches_played,
    ROUND(SUM(batsman_runs) * 1.0 / COUNT(DISTINCT match_id), 2) AS avg_runs_per_match
FROM deliveries
GROUP BY batsman
ORDER BY total_runs DESC
LIMIT 10;


-- Q12. Most sixes hit — all time
SELECT
    batsman,
    SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END) AS total_sixes
FROM deliveries
GROUP BY batsman
ORDER BY total_sixes DESC
LIMIT 10;


-- Q13. Most fours hit — all time
SELECT
    batsman,
    SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END) AS total_fours
FROM deliveries
GROUP BY batsman
ORDER BY total_fours DESC
LIMIT 10;


-- Q14. Highest strike rates (min 500 balls faced)
SELECT
    batsman,
    SUM(batsman_runs) AS total_runs,
    COUNT(*) AS balls_faced,
    ROUND(SUM(batsman_runs) * 100.0 / COUNT(*), 2) AS strike_rate
FROM deliveries
WHERE wide_runs = 0
GROUP BY batsman
HAVING COUNT(*) >= 500
ORDER BY strike_rate DESC
LIMIT 10;


-- Q15. Best batting average (min 20 innings, using dismissals)
SELECT
    batsman,
    SUM(batsman_runs) AS total_runs,
    COUNT(DISTINCT match_id) AS innings,
    SUM(CASE WHEN player_dismissed = batsman THEN 1 ELSE 0 END) AS dismissals,
    ROUND(
        SUM(batsman_runs) * 1.0 /
        NULLIF(SUM(CASE WHEN player_dismissed = batsman THEN 1 ELSE 0 END), 0),
    2) AS batting_avg
FROM deliveries
GROUP BY batsman
HAVING COUNT(DISTINCT match_id) >= 20
   AND SUM(CASE WHEN player_dismissed = batsman THEN 1 ELSE 0 END) > 0
ORDER BY batting_avg DESC
LIMIT 10;


-- =============================================================
-- SECTION 5: BOWLING ANALYSIS
-- =============================================================

-- Q16. Top 10 wicket takers of all time
SELECT
    bowler,
    COUNT(*) AS total_wickets
FROM deliveries
WHERE dismissal_kind NOT IN ('run out', 'retired hurt', 'obstructing the field')
  AND dismissal_kind IS NOT NULL
  AND dismissal_kind != ''
GROUP BY bowler
ORDER BY total_wickets DESC
LIMIT 10;


-- Q17. Best economy rates (min 200 overs bowled)
SELECT
    bowler,
    SUM(total_runs) AS runs_conceded,
    COUNT(*) AS balls_bowled,
    ROUND(COUNT(*) / 6.0, 1) AS overs_bowled,
    ROUND(SUM(total_runs) * 6.0 / COUNT(*), 2) AS economy_rate
FROM deliveries
WHERE wide_runs = 0 AND noball_runs = 0
GROUP BY bowler
HAVING COUNT(*) >= 1200   -- 200 overs = 1200 legal balls
ORDER BY economy_rate ASC
LIMIT 10;


-- Q18. Most dot balls bowled (pressure bowling)
SELECT
    bowler,
    SUM(CASE WHEN total_runs = 0 THEN 1 ELSE 0 END) AS dot_balls,
    COUNT(*) AS total_balls,
    ROUND(SUM(CASE WHEN total_runs = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS dot_ball_pct
FROM deliveries
GROUP BY bowler
HAVING COUNT(*) >= 500
ORDER BY dot_ball_pct DESC
LIMIT 10;


-- =============================================================
-- SECTION 6: VENUE ANALYSIS
-- =============================================================

-- Q19. Top venues by number of matches hosted
SELECT
    venue,
    COUNT(*) AS matches_hosted
FROM matches
GROUP BY venue
ORDER BY matches_hosted DESC
LIMIT 10;


-- Q20. Average first innings score by venue
SELECT
    m.venue,
    ROUND(AVG(inn_totals.total), 0) AS avg_first_innings_score
FROM matches m
JOIN (
    SELECT match_id, SUM(total_runs) AS total
    FROM deliveries
    WHERE inning = 1
    GROUP BY match_id
) inn_totals ON m.id = inn_totals.match_id
GROUP BY m.venue
HAVING COUNT(*) >= 10
ORDER BY avg_first_innings_score DESC
LIMIT 10;


-- Q21. Venues where chasing teams win more (best venues to bat second)
SELECT
    m.venue,
    COUNT(*) AS total_matches,
    SUM(CASE WHEN m.toss_decision = 'field' AND m.toss_winner = m.winner THEN 1
             WHEN m.toss_decision = 'bat'  AND m.toss_winner != m.winner THEN 1
             ELSE 0 END) AS chased_successfully,
    ROUND(
        SUM(CASE WHEN m.toss_decision = 'field' AND m.toss_winner = m.winner THEN 1
                 WHEN m.toss_decision = 'bat'  AND m.toss_winner != m.winner THEN 1
                 ELSE 0 END) * 100.0 / COUNT(*),
    2) AS chase_win_pct
FROM matches m
WHERE winner IS NOT NULL AND winner != ''
GROUP BY m.venue
HAVING COUNT(*) >= 15
ORDER BY chase_win_pct DESC
LIMIT 10;


-- =============================================================
-- SECTION 7: PLAYER OF THE MATCH ANALYSIS
-- =============================================================

-- Q22. Most Player of the Match awards
SELECT
    player_of_match,
    COUNT(*) AS potm_awards
FROM matches
WHERE player_of_match IS NOT NULL AND player_of_match != ''
GROUP BY player_of_match
ORDER BY potm_awards DESC
LIMIT 10;


-- =============================================================
-- SECTION 8: ADVANCED — WINDOW FUNCTIONS
-- =============================================================

-- Q23. Season-wise top run scorer using WINDOW function
SELECT season, batsman, season_runs
FROM (
    SELECT
        m.season,
        d.batsman,
        SUM(d.batsman_runs) AS season_runs,
        RANK() OVER (PARTITION BY m.season ORDER BY SUM(d.batsman_runs) DESC) AS rnk
    FROM deliveries d
    JOIN matches m ON d.match_id = m.id
    GROUP BY m.season, d.batsman
) ranked
WHERE rnk = 1
ORDER BY season;


-- Q24. Cumulative runs scored by a team across a season
SELECT
    m.season,
    m.date,
    m.team1,
    SUM(d.total_runs) AS match_runs,
    SUM(SUM(d.total_runs)) OVER (
        PARTITION BY m.season, m.team1
        ORDER BY m.date
    ) AS cumulative_runs
FROM matches m
JOIN deliveries d ON m.id = d.match_id AND d.batting_team = m.team1
GROUP BY m.season, m.date, m.team1
ORDER BY m.season, m.team1, m.date
LIMIT 50;


-- Q25. Running win count per team per season
SELECT
    season,
    winner AS team,
    COUNT(*) AS wins_this_season,
    RANK() OVER (PARTITION BY season ORDER BY COUNT(*) DESC) AS season_rank
FROM matches
WHERE winner IS NOT NULL AND winner != ''
GROUP BY season, winner
ORDER BY season, season_rank;
