# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 11:21:16 2016

@author: Can
"""


import serial
import os
import requests
import time
import sys

firstFixFlag = False # this will go true after the first GPS fix.
firstFixDate = ""

# Set up serial:
ser = serial.Serial(
    port='/dev/ttyS0',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=1)

# Helper function to take HHMM.SS, Hemisphere and make it decimal:
def degrees_to_decimal(data, hemisphere):
    try:
        decimalPointPosition = data.index('.')
        degrees = float(data[:decimalPointPosition-2])
        minutes = float(data[decimalPointPosition-2:])/60
        output = degrees + minutes
        if hemisphere is 'N' or hemisphere is 'E':
            return output
        if hemisphere is 'S' or hemisphere is 'W':
            return -output
    except:
        return ""

# Helper function to take a $GPRMC sentence, and turn it into a Python dictionary.
# This also calls degrees_to_decimal and stores the decimal values as well.
def parse_GPRMC(data):
    data = data.split(',')
    dict = {
            'fix_time': data[1],
            'validity': data[2],
            'latitude': data[3],
            'latitude_hemisphere' : data[4],
            'longitude' : data[5],
            'longitude_hemisphere' : data[6],
            'speed': data[7],
            'true_course': data[8],
            'fix_date': data[9],
            'variation': data[10],
            'variation_e_w' : data[11],
            'checksum' : data[12]
    }
    dict['decimal_latitude'] = degrees_to_decimal(dict['latitude'], dict['latitude_hemisphere'])
    dict['decimal_longitude'] = degrees_to_decimal(dict['longitude'], dict['longitude_hemisphere'])
    return dict
    
# Function to sender XMLrequest to the server.

def sendrequest(position):
    xml = """<om2m:cin xmlns:om2m="http://www.onem2m.org/xml/protocols">
    <cnf>message</cnf>
    <con>
      &lt;obj&gt;
      &lt;int name=&quot;data&quot; val=&quot;"""
      
    xml3 = """&quot;/&gt;      
     &lt;/obj&gt;
    </con>
</om2m:cin>"""

    headers = {'X-M2M-Origin': 'admin:admin',
               'Content-Type': 'application/xml;ty=4',
} # set what your server accepts
    requests.post('http://127.0.0.1:8080/~/mn-cse/mn-name/MY_GPS/DATA', data=xml + position +xml3, headers=headers)
    return ""    

#print requests.post('http://127.0.0.1:8080/~/in-cse', data=xml, headers=headers).text   
    

# Main program loop:
while True:
    line = ser.readline()
#    line = "$GPRMC,085941.757,V,3854.930,N,07502.499,W,24.9,2.96,180716,,E*48"
    
    if "$GPRMC" in line: # This will exclude other NMEA sentences the GPS unit provides.
        gpsData = parse_GPRMC(line) # Turn a GPRMC sentence into a Python dictionary called gpsData
        if gpsData['validity'] == "A": # If the sentence shows that there's a fix, then we can log the line
            if firstFixFlag is False: # If we haven't found a fix before, then set the filename prefix with GPS date & time.
                firstFixDate = gpsData['fix_date'] + "-" + gpsData['fix_time']
                firstFixFlag = True
            else: # write the data to a simple log file and then the raw data as well
                gpsposittion = str(gpsData['decimal_latitude']) + "," + str(gpsData['decimal_longitude'])
                print (gpsposittion)
                sys.exit()
#                time.sleep(3)
#                sendrequest(gpsposittion)            
 #               with open("/home/pi/gps_experimentation/" + firstFixDate +"-simple-log.txt", "a") as myfile:
 #                   myfile.write(gpsData['fix_date'] + "," + gpsData['fix_time'] + "," + gpsposittion +"\n")
 #               with open("/home/pi/gps_experimentation/" + firstFixDate +"-gprmc-raw-log.txt", "a") as myfile:
 #                   myfile.write(line)