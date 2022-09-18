#!/usr/bin/env python3

ATCF_KEYS = [
    "basin",
    "cyclone_number",
    "date",
    "technique_number",
    "technique",
    "forecast_period",
    "latitude",
    "longitude",
    "vmax",
    "mslp",
    "development_level",
    "radii_for_record",
    "windcode",
    "rad1",
    "rad2",
    "rad3",
    "rad4",
    "pressure_outer",
    "radius_outer",
    "radius_to_max_winds",
    "gusts",
    "eye_diameter",
    "subregion",
    "max_seas",
    "forecaster_initials",
    "storm_direction",
    "storm_speed",
    "storm_name",
    "system_depth",
    "seas_wave_height",
    "seas_radius_code",
    "seas1",
    "seas2",
    "seas3",
    "seas4",
]


class Database:
    def __init__(self):
        import sys
        import os
        import pymysql
        import boto3

        self.__dbhost = os.environ["DBSERVER"]
        self.__dbpassword = os.environ["DBPASS"]
        self.__dbusername = os.environ["DBUSER"]
        self.__dbname = os.environ["DBNAME"]

        self.__metget_bucket = "metget-data"
        self.__s3 = boto3.resource("s3")
        self.__s3_client = boto3.client("s3")
        self.__bucket = self.__s3.Bucket(self.__metget_bucket)

        try:
            self.__db = pymysql.connect(
                host=self.__dbhost,
                user=self.__dbusername,
                passwd=self.__dbpassword,
                db=self.__dbname,
                connect_timeout=5,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except:
            print("[ERROR]: Could not connect to MySQL database")
            sys.exit(1)

        self.__cursor = self.__db.cursor()
        self.__generate_table()

    def cursor(self):
        return self.__cursor

    def database(self):
        return self.__db

    def __generate_table(self):
        sql = "CREATE TABLE IF NOT EXISTS nhc_besttrack_geojson(id INTEGER PRIMARY KEY "
        "AUTO_INCREMENT, forecastcycle DATETIME NOT NULL, forecasttime DATETIME NOT NULL, "
        "filepath VARCHAR(256) NOT NULL, url VARCHAR(256) NOT NULL, accessed DATETIME NOT NULL);"

    def get_file(self, path: str, output_path: str):
        self.__s3_client.download_file(self.__metget_bucket, path, output_path)


def __generate_file_list(db: Database) -> dict:
    best_track_table = "nhc_btk"
    forecast_track_table = "nhc_fcst"

    best_track_sql = "select * from {:s};".format(best_track_table)
    forecast_track_sql = "select * from {:s}".format(forecast_track_table)
    db.cursor().execute(best_track_sql)
    best_track_data = db.cursor().fetchall()

    db.cursor().execute(forecast_track_sql)
    forecast_track_data = db.cursor().fetchall()

    return {"best_track": best_track_data, "forecast": forecast_track_data}


def __read_nhc_data(filename: str) -> list:
    from datetime import datetime, timedelta
    data = []
    with open(filename, "r") as f:
        for line in f:
            keys = line.rstrip().split(",")
            date = datetime.strptime(keys[2], " %Y%m%d%H")
            hour = int(keys[5])
            full_date = date + timedelta(hours=hour)
            atcf_dict = dict(zip(ATCF_KEYS, keys))
            data.append({"data": atcf_dict, "time": full_date})

    return data


def __position_to_float(position: str):
    direction = position[-1].upper()
    pos = float(position[:-1]) / 10.0
    if direction == "W" or direction == "S":
        return pos * -1.0
    else:
        return pos


def __generate_track(path: str) -> tuple:
    from geojson import Feature, FeatureCollection, Point, LineString
    from datetime import datetime
    KNOT_TO_MPH = 1.15078

    data = __read_nhc_data(path)

    track_points = []
    points = []
    last_time = None
    for d in data:
        if d["time"] == last_time:
            continue
        longitude = __position_to_float(d["data"]["longitude"])
        latitude = __position_to_float(d["data"]["latitude"])
        track_points.append((longitude, latitude))
        points.append(
            Feature(geometry=Point((longitude, latitude)),
                    properties={"time_utc": datetime.strftime(d["time"], "%Y-%m-%dT%H:%M:%S"),
                                "max_wind_speed_mph": round(float(d["data"]["vmax"]) * KNOT_TO_MPH, 2),
                                "minimum_sea_level_pressure_mb": float(d["data"]["mslp"]),
                                "radius_to_max_wind_nmi": float(
                                    d["data"]["radius_to_max_winds"]),
                                "storm_class": d["data"]["development_level"].strip()}))
    storm_track = Feature(geometry=LineString(track_points))
    return FeatureCollection(features=points), storm_track


def add_track_to_database(table: str, db: Database, track_data: dict):
    import os
    import json
    track_file = track_data["filepath"]
    local_path = os.path.basename(track_file)
    print(local_path)
    db.get_file(track_file, local_path)
    point_json, track_json = __generate_track(local_path)
    json_string = json.dumps({"storm_track_points": point_json, "storm_track_line": track_json})
    sql = "update {:s} set geojson = '{:s}' where id = {:d}".format(table, json_string, track_data["id"])
    db.cursor().execute(sql)
    db.database().commit()
    os.remove(local_path)


def generate_tracks(db: Database):
    track_data = __generate_file_list(db)

    for trk in track_data["best_track"]:
        add_track_to_database("nhc_btk", db, trk)

    for trk in track_data["forecast"]:
        add_track_to_database("nhc_fcst", db, trk)


def lambda_handler(event, context):
    db = Database()
    generate_tracks(db)
