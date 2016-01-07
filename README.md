# Helium API Examples

```
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Usage:

```
$ export HELIUM_API_KEY="YOUR_API_KEY"
$ # second argument is a datasource id, from:
$ # ex: https://my.helium.com/datasource/4XlUNRMSTVasLpehlybrGQ
$ ./temperature-history.py $HELIUM_API_KEY '4XlUNRMSTVasLpehlybrGQ'
$ head temp.csv
timestamp-utc,temperature-celsius
2016-01-07T18:21:16Z,22.7143
2016-01-07T18:20:15Z,22.7429
2016-01-07T18:19:14Z,22.6857
2016-01-07T18:18:13Z,22.7429
2016-01-07T18:17:12Z,22.7714
2016-01-07T18:16:11Z,22.8
2016-01-07T18:15:10Z,22.8
2016-01-07T18:14:09Z,22.7714
2016-01-07T18:13:08Z,22.7143
```
