import requests
import json
import datetime
from configparser import ConfigParser
#os and glob used for determining newest files
import os
import glob
import time
import csv


while 2>1:

    #reads the config file to import settings
    config = ConfigParser()
    config.read('config.ini')

    t0=time.time()

    api_key = "20feac060cca791485e794877771c036"

    lat = "39.7433540223452"
    lon = "-75.54794737315223"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=imperial" % (lat, lon, api_key)
    response = requests.get(url)
    data = json.loads(response.text)

    #print(data)

    weather = [['DCO Wilmington Outdoor Temperature',str(datetime.datetime.now().isoformat()+'-4:00'),str(data['current']['temp']),'degreesFahrenheit']]

    print('\nThe temperature is {}F'.format(weather[0][2]))
    
    timestr = time.strftime("%Y%m%d-%H%M%S")


    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'Output','{} {}.csv'.format(config.get('main', 'Site Name'),timestr)),'w') as f:
        
        wr = csv.writer(f,delimiter="\n")
        output1=[]
        k=0
        #this loop takes the nest list and converts each sub list (ex. output[0]) to a comma separated string as an element in the new output1 list
        #to prevent the csvwriter from including things like apostrophes and brackets in the output file
        while k < len(weather):
            output1.append(",".join(weather[k]))
            k+=1
        wr.writerow(output1)





    
    
    
    #mypath=os.path.dirname(os.path.abspath(__file__))+'/Output/'+'*.csv'
    #latest_file=max(glob.glob(mypath), key=os.path.getmtime) 
    #print(latest_file)
    mypath=os.path.dirname(os.path.abspath(__file__))+'/Output/'+'*.csv'
    list_of_files = glob.glob(mypath)
    sorted_files = sorted(list_of_files, key=os.path.getmtime)
    
    
    
    
    
    x=0

    #grabs the gateway id from the config file for the BuildingOS upload
    gateway = config.get('main', 'gateway')

    while x < len(sorted_files):
        
        if config.get('main', 'remove uploads') == 'True':
            filename = sorted_files[-(x+1)]
            print('There are {} files to be uploaded. Attemping upload of file #{}.'.format(len(sorted_files),x+1))
        else:
            filename = sorted_files[-1]
            x=len(sorted_files)
        
        try:
            response = requests.post(
                'https://rest.buildingos.com/dsv/push?datasource=bos://buildingos-csv/{}'.format(gateway),
                files={'data':open(filename, 'rb')}
            )
        except:
            print('Upload failed. Upload will be reattemped next cycle.')

        print('\nHTTP Response: \n', response.text)            
        # if the option is selected in the config file AND the file upload is successful, the CSV file is deleted
        if config.get('main', 'remove uploads') == 'True':
            if response.text == 'ok':
                os.remove(filename)
                print('Upload successful. Removing uploaded CSV file.')
        x+=1

    t1=time.time()

    total_time=t1-t0

    print("\nWaiting {} seconds until the next weather call.".format(900-total_time))
    time.sleep(900-total_time)