CREATE TABLE matches (
  id INTEGER PRIMARY KEY,
  source_id VARCHAR(240) UNIQUE NOT NULL,
  title VARCHAR(300) NOT NULL,
  team_a VARCHAR(120) NOT NULL,
  team_b VARCHAR(120) NOT NULL,
  short_a VARCHAR(20) NOT NULL,
  short_b VARCHAR(20) NOT NULL,
  venue VARCHAR(240),
  league VARCHAR(120),
  match_format VARCHAR(40),
  starts_at TIMESTAMP,
  captain_a VARCHAR(120),
  captain_b VARCHAR(120),
  weather VARCHAR(80),
  humidity FLOAT,
  is_day_night BOOLEAN,
  home_team VARCHAR(120),
  status VARCHAR(40),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE predictions (
  id INTEGER PRIMARY KEY,
  match_id INTEGER REFERENCES matches(id),
  predicted_winner VARCHAR(120) NOT NULL,
  confidence FLOAT NOT NULL,
  probability_a FLOAT NOT NULL,
  probability_b FLOAT NOT NULL,
  factors TEXT NOT NULL,
  model_version VARCHAR(60),
  telegram_message_id INTEGER,
  telegram_photo_message_id INTEGER,
  pinned BOOLEAN,
  created_at TIMESTAMP
);

CREATE TABLE toss_actuals (
  id INTEGER PRIMARY KEY,
  prediction_id INTEGER REFERENCES predictions(id),
  actual_winner VARCHAR(120) NOT NULL,
  decision VARCHAR(40),
  was_correct BOOLEAN NOT NULL,
  posted_update_message_id INTEGER,
  created_at TIMESTAMP
);

CREATE TABLE venue_stats (
  id INTEGER PRIMARY KEY,
  venue VARCHAR(240) UNIQUE NOT NULL,
  team_a_bias FLOAT,
  day_night_bias FLOAT,
  samples INTEGER
);

CREATE TABLE captain_stats (
  id INTEGER PRIMARY KEY,
  captain VARCHAR(120) UNIQUE NOT NULL,
  toss_win_rate FLOAT,
  samples INTEGER
);
