--Creates tables for the storage of metget's metadata
CREATE TABLE gfs_ncep(
  id SERIAL PRIMARY KEY, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  url VARCHAR(256) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);
CREATE TABLE gefs_fcst(
  id SERIAL PRIMARY KEY, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  ensemble_member VARCHAR(32) NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  url VARCHAR(256) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);
CREATE TABLE hwrf(
  id SERIAL PRIMARY KEY, 
  stormname VARCHAR(256) NOT NULL, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  url VARCHAR(256) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);
CREATE TABLE nam_ncep(
  id SERIAL PRIMARY KEY, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  url VARCHAR(256) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);
CREATE TABLE nhc_btk(
  id SERIAL PRIMARY KEY, 
  storm_year INTEGER NOT NULL, 
  basin VARCHAR(256) NOT NULL, 
  storm INTEGER NOT NULL, 
  advisory_start TIMESTAMP NOT NULL, 
  advisory_end TIMESTAMP NOT NULL, 
  advisory_duration_hr INT NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  md5 VARCHAR(32) NOT NULL, 
  accessed TIMESTAMP NOT NULL, 
  geometry_data JSON NOT NULL
);
CREATE TABLE nhc_fcst(
  id SERIAL PRIMARY KEY, 
  storm_year INTEGER NOT NULL, 
  basin VARCHAR(256) NOT NULL, 
  storm INTEGER NOT NULL, 
  advisory VARCHAR(256) NOT NULL, 
  advisory_start TIMESTAMP NOT NULL, 
  advisory_end TIMESTAMP NOT NULL, 
  advisory_duration_hr INT NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  md5 VARCHAR(32) NOT NULL, 
  accessed TIMESTAMP NOT NULL, 
  geometry_data JSON NOT NULL
);
CREATE TABLE coamps_tc(
  id SERIAL PRIMARY KEY, 
  stormname VARCHAR(256) NOT NULL, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(512) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);
CREATE TABLE hrrr_ncep(
  id SERIAL PRIMARY KEY, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  url VARCHAR(256) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);
CREATE TABLE hrrr_alaska_ncep(
  id SERIAL PRIMARY KEY, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  url VARCHAR(256) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);
CREATE TABLE wpc_ncep(
  id SERIAL PRIMARY KEY, 
  forecastcycle TIMESTAMP NOT NULL, 
  forecasttime TIMESTAMP NOT NULL, 
  tau INTEGER NOT NULL, 
  filepath VARCHAR(256) NOT NULL, 
  url VARCHAR(256) NOT NULL, 
  accessed TIMESTAMP NOT NULL
);

--Creates tables for the storage of metget's API access
CREATE TABLE apikeys(
  id SERIAL PRIMARY KEY, 
  key CHAR(41) NOT NULL, 
  username VARCHAR(256) NOT NULL, 
  description VARCHAR(256), 
  credit_limit BIGINT NOT NULL,
  enabled BOOLEAN NOT NULL,
  expiration TIMESTAMP,
  permissions JSON
);

--Creates tables for the storage of metget's build requests and status
CREATE TYPE metget_status AS ENUM(
  'queued', 'running', 'error', 'completed'
);
CREATE TABLE requests(
  id SERIAL PRIMARY KEY, 
  request_id VARCHAR(36) NOT NULL, 
  try INTEGER DEFAULT 0 NOT NULL, 
  status metget_status NOT NULL, 
  start_date TIMESTAMP NOT NULL, 
  last_date TIMESTAMP NOT NULL, 
  api_key VARCHAR(128) NOT NULL, 
  credit_usage BIGINT NOT NULL,
  source_ip VARCHAR(128) NOT NULL,, 
  input_data JSON NOT NULL,
  message JSON NOT NULL
);
