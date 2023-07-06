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
CREATE TABLE ctcx(
  id SERIAL PRIMARY KEY,
  stormname VARCHAR(256) NOT NULL,
  ensemble_member INTEGER NOT NULL,
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

--Create Brin Indexes on forecastcycle for the various tables
CREATE INDEX gfs_ncep_forecastcycle_idx ON gfs_ncep USING brin (forecastcycle);
CREATE INDEX gefs_fcst_forecastcycle_idx ON gefs_fcst USING brin (forecastcycle);
CREATE INDEX hwrf_forecastcycle_idx ON hwrf USING brin (forecastcycle);
CREATE INDEX nam_ncep_forecastcycle_idx ON nam_ncep USING brin (forecastcycle);
CREATE INDEX coamps_tc_forecastcycle_idx ON coamps_tc USING brin (forecastcycle);
CREATE INDEX ctcx_forecastcycle_idx ON ctcx USING brin (forecastcycle);
CREATE INDEX hrrr_ncep_forecastcycle_idx ON hrrr_ncep USING brin (forecastcycle);
CREATE INDEX hrrr_alaska_ncep_forecastcycle_idx ON hrrr_alaska_ncep USING brin (forecastcycle);
CREATE INDEX wpc_ncep_forecastcycle_idx ON wpc_ncep USING brin (forecastcycle);

---Create Brin Index on basin for nhc_fcst and nhc_btk
CREATE INDEX nhc_fcst_basin_idx ON nhc_fcst USING brin (basin);
CREATE INDEX nhc_btk_basin_idx ON nhc_btk USING brin (basin);
