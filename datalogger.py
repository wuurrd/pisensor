# -*- coding: utf-8 -*-
import argparse
import time
import datetime
import sys
import os
from influxdb import InfluxDBClient
from sense_hat import SenseHat

try:
    sense=SenseHat()
except:
    sense = None

# Set required InfluxDB parameters.
# (this could be added to the program args instead of beeing hard coded...)
host = "localhost" #Could also set local ip address
port = 8086
user = "root"
password = "root"

# Sample period (s).
# How frequently we will write sensor data from SenseHat to the database.
sampling_period = 15

def get_args():
    '''This function parses and returns arguments passed in'''
    # Assign description to the help doc
    parser = argparse.ArgumentParser(description='Program writes measurements data from SenseHat to specified influx db.')
    # Add arguments
    parser.add_argument(
        '-db','--database', type=str, help='Database name', required=True)
    parser.add_argument(
        '-sn','--session', type=str, help='Session', required=True)
    now = datetime.datetime.now()
    parser.add_argument(
        '-rn','--run', type=str, help='Run number', required=False,default=now.strftime("%Y%m%d%H%M"))

    # Array of all arguments passed to script
    args=parser.parse_args()
    # Assign args to variables
    dbname=args.database
    runNo=args.run
    session=args.session
    return dbname, session,runNo

def get_data_points():
    # Get the three measurement values from the SenseHat sensors
    temperature = sense.get_temperature()
    pressure = sense.get_pressure()
    humidity = sense.get_humidity()
    # Get a local timestamp
    timestamp=datetime.datetime.utcnow().isoformat()
    print ("{0} {1} Temperature: {2}{3}C Pressure: {4}mb Humidity: {5}%" .format(session,runNo,
    round(temperature,1),u'u00b0'.encode('utf8'),
    round(pressure,3),round(humidity,1)))
    load1, load5, load15 = os.getloadavg()
    diskspace = os.statvfs('/')
    disk = (diskspace.f_bavail * diskspace.f_frsize) / 1024
    # Create Influxdb datapoints (using lineprotocol as of Influxdb >1.1)
    datapoints = [
        {
            "measurement": 'sensors',
            "tags": {"runNum": runNo,
            },
            "time": timestamp,
            "fields": {
                "temperaturevalue": temperature,
                "pressurevalue": pressure,
                "humidityvalue": humidity,
                "load1": load1,
                "load5": load5,
                "load15": load15,
                "disk": disk,
            }
        }
    ]
    return datapoints

def get_os_points():
    # Get the three measurement values from the SenseHat sensors
    # Get a local timestamp
    timestamp=datetime.datetime.utcnow().isoformat()
    round(pressure,3),round(humidity,1)))
    load1, load5, load15 = os.getloadavg()
    diskspace = os.statvfs('/')
    disk = (diskspace.f_bavail * diskspace.f_frsize) / 1024
    # Create Influxdb datapoints (using lineprotocol as of Influxdb >1.1)
    print ("{0} {1} CPU: {2} Memory: {3}" .format(
        session, runNo, load1, disk/1024/1024)

    datapoints = [
        {
            "measurement": 'os',
            "tags": {"runNum": runNo,
            },
            "time": timestamp,
            "fields": {
                "load1": load1,
                "load5": load5,
                "load15": load15,
                "disk": disk,
            }
        }
    ]
    return datapoints


# Match return values from get_arguments()
# and assign to their respective variables
dbname, session, runNo =get_args()
print "Session: ", session
print "Run No: ", runNo
print "DB name: ", dbname

# Initialize the Influxdb client
client = InfluxDBClient(host, port, user, password, dbname)

try:
     while True:
        # Write datapoints to InfluxDB
        if sense != None:
           datapoints=get_data_points()
           bResult=client.write_points(datapoints)
           print("Write points {0} Bresult:{1}".format(datapoints,bResult))
        datapoints2=get_data_points()
        bResult=client.write_points(datapoints)
        print("Write points {0} Bresult:{1}".format(datapoints2, bResult))

        if sense != None:
           sense.show_message("OK")

        # Wait for next sample
        time.sleep(sampling_period)

        # Run until keyboard ctrl-c
except KeyboardInterrupt:
    print ("Program stopped by keyboard interrupt [CTRL_C] by user. ")
