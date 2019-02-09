# -*- coding: utf-8 -*-
#########################################################
# SERVICE : OpenWeatherMap.py                           #
#           Service that gives weather information      #
#           from the OpenWeatherMap weather service     #
#########################################################

####################### IMPORTS #########################
from builtins import str
from builtins import range
from builtins import object
import requests, urllib.request, urllib.parse, urllib.error, json
import datetime
import logging

#########################################################

####################### GLOBALS #########################
NO_LOC = -10000
#########################################################

###################### FUNCTIONS ########################

#########################################################

#########################################################
# Class : OpenWeatherMap                                #
#########################################################
class OpenWeatherMap(object):
    baseurl = "http://api.openweathermap.org/data/2.5/"
    def __init__(self, basename, unitsMetric, LocationStr, ApiKey = None):
        self.verbose = True
        self.logger = logging.getLogger('{}.OpenWeatherMap'.format(basename))
        if unitsMetric:
            self.units='metric'
        else:
            self.units='imperial'
        self.ApiKey = ApiKey
        self.LocationStr = LocationStr
        self.lat = NO_LOC
        self.lon = NO_LOC
        try:
            self.GetLocation(LocationStr)
        except:
            pass

    def __del__(self):
        pass

    def GetLocation(self, LocationStr):
        query='find?q={}&type=like&APPID={}'.format(LocationStr, self.ApiKey)
        query_url = "{}{}".format(self.baseurl, query)
        result = requests.get(query_url)
        data = json.loads(result.text)

        try:
            if len(data['list'])>1:
                self.logger.error("Location cannot be found unambiguously, exiting ...")
                return False
            else:
                self.lat=data['list'][0]['coord']['lat']
                self.lon=data['list'][0]['coord']['lon']
                self.logger.info("Obtained location data lat, lon = %f, %f", self.lat, self.lon)
        except:
            return False

        return True

    def Get5dayForecast(self):
        params = {}
        doForecast = True
        if (self.lat == NO_LOC) or (self.lon == NO_LOC):
            doForecast = self.GetLocation(self.LocationStr)
        if doForecast:
            if not self.units:
                self.units='metric'

            try:
                query='forecast?lat={}&lon={}&units={}&APPID={}'.format(self.lat, self.lon, self.units, self.ApiKey)
                query_url = "{}{}".format(self.baseurl, query)
                result = requests.get(query_url)
                data = json.loads(result.text)

                forecast=data['list']
                j=0
                for i in range (0, 5):
                    param = self._CalcDayParams(forecast, i, j)
                    if param:
                        params.update(param)
                        j += 1
                self.logger.info("Queried: 5 day forecast")
            except Exception as e:
                self.logger.exception(e)

        return params

    def Get3hForecast(self):
        params = {}
        doForecast = True
        if (self.lat == NO_LOC) or (self.lon == NO_LOC):
            doForecast = self.GetLocation(self.LocationStr)
        if doForecast:
            if not self.units:
                self.units='metric'

            try:
                query='forecast?lat={}&lon={}&units={}&APPID={}'.format(self.lat, self.lon, self.units, self.ApiKey)
                query_url = "{}{}".format(self.baseurl, query)
                result = requests.get(query_url)
                data = json.loads(result.text)

                data=data['list']
                i=0

                if 'temp_min' in data[i]['main']:
                    params['low'] = int(round(data[i]['main']['temp_min'])) 
                else:
                    params['low'] = 0
                if 'temp_max' in data[i]['main']:
                    params['high'] = int(round(data[i]['main']['temp_max'])) 
                else:
                    params['high'] = 0
                rain = 0
                snow = 0
                if 'rain' in data[i]:
                    if '1h' in data[i]['rain']:
                        rain = data[i]['rain']['1h']
                    elif '3h' in data[i]['rain']:
                        rain = data[i]['rain']['3h']
                if 'snow' in data[i]:
                    if '1h' in data[i]['snow']:
                        snow = data[i]['snow']['1h']
                    elif '3h' in data[i]['snow']:
                        snow = data[i]['snow']['3h']
                params['precipation'] = (rain+snow)
                if 'clouds' in data[i]:
                    params['clouds'] = data[i]['clouds']['all']
                else:
                    params['clouds'] = 0
                if 'speed' in data[i]['wind']:
                    params['windspeed'] = data[i]['wind']['speed']
                else:
                    params['windspeed'] = 0
                if 'deg' in data[i]['wind']:
                    params['windangle'] = data[i]['wind']['deg']
                else:
                    params['windangle'] = 0

                self.logger.info("Queried: 3 hours forecast")
                if self.verbose:    
                    self.logger.debug("Date            : %s",datetime.datetime.fromtimestamp(int(data[i]['dt'])).strftime('%c'))
                    self.logger.debug("High Temperature: %d",params['high'])
                    self.logger.debug("Low Temperature : %d",params['low'])
                    self.logger.debug("Precipation     : %f",params['precipation'])
                    self.logger.debug("Clouds          : %d",params['clouds'])
                    self.logger.debug("Wind speed      : %d",params['windspeed'])
                    self.logger.debug("Wind angle      : %d",params['windangle'])
                    self.logger.debug("-------------------")

            except Exception as e:
                self.logger.exception(e)

        return params

    def GetCurrent(self):
        params = {}
        doForecast = True
        if (self.lat == NO_LOC) or (self.lon == NO_LOC):
            doForecast = self.GetLocation(self.LocationStr)
        if doForecast:
            if not self.units:
                self.units='metric'

            try:
                query='weather?lat={}&lon={}&units={}&APPID={}'.format(self.lat, self.lon, self.units, self.ApiKey)
                query_url = "{}{}".format(self.baseurl, query)
                result = requests.get(query_url)
                data = json.loads(result.text)

                if 'temp' in data['main']:
                    params['current_temp'] = int(round(data['main']['temp']))     
                else:
                    params['current_temp'] = 0 
                rain = 0
                snow = 0
                indata = 0
                if 'rain' in data:
                    indata += 1
                    if '1h' in data['rain']:
                        rain = data['rain']['1h']
                    elif '3h' in data['rain']:
                        rain = data['rain']['3h']
                if 'snow' in data:
                    indata += 1
                    if '1h' in data['snow']:
                        snow = data['snow']['1h']
                    elif '3h' in data['snow']:
                        snow = data['snow']['3h']
                params['current_precipation'] = (rain+snow)
                if indata == 0:
                    self.logger.debug("No rain data in current weather data, try to obtain from 3h forecast")
                    params3h = self.Get3hForecast()
                    if 'precipation' in params3h:
                        params['current_precipation'] = params3h['precipation']
                if 'clouds' in data:
                    params['current_clouds'] = int(round(data['clouds']['all']))
                else:
                    params['current_clouds'] = 0
                if 'speed' in data['wind']:
                    params['current_windspeed'] = int(round(data['wind']['speed']))
                else:
                    params['current_windspeed'] = 0
                if 'deg' in data['wind']:
                    params['current_windangle'] = int(round(data['wind']['deg']))
                else:
                    params['current_windangle'] = 0

                self.logger.info("Queried: Current weather")
                if self.verbose:    
                    self.logger.debug("Date               : %s",datetime.datetime.fromtimestamp(int(data['dt'])).strftime('%c'))
                    self.logger.debug("Current Temperature: %d",params['current_temp'])
                    self.logger.debug("Current Precipation: %f",params['current_precipation'])
                    self.logger.debug("Current Clouds     : %d",params['current_clouds'])
                    self.logger.debug("Current Wind speed : %d",params['current_windspeed'])
                    self.logger.debug("Current Wind angle : %d",params['current_windangle'])
                    self.logger.debug("-------------------")
            except Exception as e:
                self.logger.exception(e)

        return params

    def _CalcDayParams(self, data, day, index):
        param = {}
        avgspeed = 0
        avgdir = 0
        avgcloud = 0
        Day = int(datetime.date.today().strftime("%s")) + day*24*60*60
        NextDay = Day + 24*60*60

        j = 0
        for i in range (0, len(data)):
            if (int(data[i]['dt'])>=Day) and (int(data[i]['dt'])<NextDay):
                j += 1
                if 'temp_min' in data[i]['main']:
                    if 'low'+str(index) in param:
                        if data[i]['main']['temp_min'] < param['low'+str(index)]:
                            param['low'+str(index)] = int(round(data[i]['main']['temp_min']))     
                    else:
                        param['low'+str(index)] = int(round(data[i]['main']['temp_min'])) 
                if 'temp_max' in data[i]['main']:
                    if 'high'+str(index) in param:
                        if data[i]['main']['temp_max'] > param['high'+str(index)]:
                            param['high'+str(index)] = int(round(data[i]['main']['temp_max']))
                    else:
                        param['high'+str(index)] = int(round(data[i]['main']['temp_max'])) 
                rain = 0
                snow = 0
                if 'rain' in data[i]:
                    if '1h' in data[i]['rain']:
                        rain = data[i]['rain']['1h']
                    elif '3h' in data[i]['rain']:
                        rain = data[i]['rain']['3h']
                if 'snow' in data[i]:
                    if '1h' in data[i]['snow']:
                        snow = data[i]['snow']['1h']
                    elif '3h' in data[i]['snow']:
                        snow = data[i]['snow']['3h']
                if 'precipation'+str(index) in param:
                    param['precipation'+str(index)] += (rain+snow)
                else:
                    param['precipation'+str(index)] = (rain+snow)
                if 'clouds' in data[i]:
                    avgcloud += data[i]['clouds']['all']
                    param['clouds'+str(index)] = int(round(avgcloud/j))
                else:
                    if not 'clouds'+str(index) in param: 
                        param['clouds'+str(index)] = 0
                if 'speed' in data[i]['wind']:
                    avgspeed += data[i]['wind']['speed']
                    param['windspeed'+str(index)] = int(round(avgspeed/j))
                else:
                    if not 'windspeed'+str(index) in param: 
                        param['windspeed'+str(index)] = 0
                if 'deg' in data[i]['wind']:
                    avgdir += data[i]['wind']['deg']
                    param['windangle'+str(index)] = int(round(avgdir/j))
                else:
                    if not 'windangle'+str(index) in param: 
                        param['windangle'+str(index)] = 0
        if not 'low'+str(index) in param:
            param['low'+str(index)] = 0
        if not 'high'+str(index) in param:
            param['high'+str(index)] = 0

        if self.verbose:    
            self.logger.debug("index           : %d",index)
            self.logger.debug("Date            : %s",datetime.datetime.fromtimestamp(int(Day)).strftime('%c'))
            self.logger.debug("High Temperature: %d",param['high'+str(index)])
            self.logger.debug("Low Temperature : %d",param['low'+str(index)])
            self.logger.debug("Precipation     : %f",param['precipation'+str(index)])
            self.logger.debug("Clouds          : %d",param['clouds'+str(index)])
            self.logger.debug("Wind speed      : %d",param['windspeed'+str(index)])
            self.logger.debug("Wind angle      : %d",param['windangle'+str(index)])
            self.logger.debug("-------------------")

        return param