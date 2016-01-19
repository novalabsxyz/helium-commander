#!/usr/bin/env python

import pytz
import datetime
import dateutil.parser
import requests

BASE_URL = "https://api.helium.com/v0/"
EPOCH = datetime.datetime(1970,1,1, tzinfo=pytz.utc)

def unix_time_millis(dt):
    return int((dt - EPOCH).total_seconds() * 1000)

def epoch_time_from_iso8601(datestring):
    dt = dateutil.parser.parse(datestring)
    return str(unix_time_millis(dt))

def sensor(api_key):
    url = BASE_URL + 'sensor'
    headers = {'Authorization': api_key}
    req = requests.get(url, headers=headers)
    print req.content

def datasource_history(api_key, datasource_id):
    history = []

    url = BASE_URL + 'datasource/' + datasource_id + '/history?count=1000'
    headers = {'Authorization': api_key}

    # get the first page, which has no `before` parameter
    print("Getting data from Helium...")
    req = requests.get(url, headers=headers)
    res = req.json()
    history+= res
    while len(res) > 1:
        res = []
        last_date = history[-1]['date']
        last_date_epoch = epoch_time_from_iso8601(last_date)
        new_url = url + '&before=' + last_date_epoch
        req = requests.get(new_url, headers=headers)
        res = req.json()
        history+= res

    return history

if __name__ == "__main__":
    import sys, getopt, csv, json
    api_key = ""
    datasource_id = ""
    use_json = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "jk:d:")
    except getopt.GetoptError:
        print 'usage: temperature-history.py -k <api_key> -d <datasource_id>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-k"):
            api_key = arg
        elif opt in ("-d"):
            datasource_id = arg
        elif opt in ("-j"):
            use_json = True
        else:
            print 'usage: temperature-history.py -k <api_key> -d <datasource_id>'
            sys.exit(2)
    if api_key == "":
        print 'Missing API Key'
        sys.exit(2)
    elif datasource_id == "":
        print 'Missing Datasource ID'
        sys.exit(2)

    temp_history = datasource_history(api_key, datasource_id)

    if use_json:
        print("Writing temp.json...")
        with open('temp.json', 'w') as jsonfile:            
            jsonfile.write(json.dumps(temp_history))
    else:
        print("Writing temp.csv...")
        with open('temp.csv', 'w') as csvfile:
            fieldnames = ['timestamp-utc', 'temperature-celsius']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for reading in temp_history:
                row = {'timestamp-utc': reading['date'], 'temperature-celsius': reading['value']}
                writer.writerow(row)