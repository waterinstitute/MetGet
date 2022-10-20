def lambda_handler(event, context):
    import json
    import os
    import pymysql

    dbhost = os.environ["DBSERVER"]
    dbpassword = os.environ["DBPASS"]
    dbusername = os.environ["DBUSER"]
    dbname = os.environ["DBNAME"]

    nhc_best_track_table = "nhc_btk"
    nhc_forecast_track_table = "nhc_fcst"

    db = pymysql.connect(
        host=dbhost,
        user=dbusername,
        passwd=dbpassword,
        db=dbname,
        connect_timeout=5,
    )

    query_parameters = event["queryStringParameters"]
    basin = query_parameters["basin"]
    year = query_parameters["year"]
    storm = int(query_parameters["storm"])
    type = query_parameters["type"]

    track_data = {"basin": basin, "year": year, "storm": storm}
    if type == "forecast":
        advisory = "{:03d}".format(int(query_parameters["advisory"]))
        track_data["advisory"] = advisory
    else:
        advisory = None

    cursor = db.cursor()

    status = 400
    sql = None
    if type == "best":
        sql = "select geojson from {:s} where basin = '{:s}' and storm = '{:d}' and storm_year = {:s}".format(
            nhc_best_track_table, basin, storm, year)
    elif type == "forecast":
        sql = "select geojson from {:s} where basin = '{:s}' and storm = '{:d}' and storm_year = {:s} and advisory = '{:s}'".format(
            nhc_forecast_track_table, basin, storm, year, advisory)

    if sql:
        cursor.execute(sql)
        data = cursor.fetchall()
        if not data:
            geojson = {"error": "Invalid query specified. No results"}
        elif len(data) > 1:
            geojson = {"error": "Invalid query specified. Too many results"}
        else:
            geojson = json.loads(data[0][0])
            status = 200
    else:
        geojson = {"error": "Invalid track type specified"}

    track_data["geojson"] = geojson

    db.close()

    return_data = {
        'statusCode': status,
        'headers': { 
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(track_data)
    }

    return return_data
