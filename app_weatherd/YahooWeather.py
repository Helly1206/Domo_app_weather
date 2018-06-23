# -*- coding: utf-8 -*-
#########################################################
# SERVICE : YahooWeather.py                             #
#           Service that gives weather information      #
#           from the yahoo weather service              #
#########################################################

####################### IMPORTS #########################
import requests, urllib, json
import logging

#########################################################

####################### GLOBALS #########################
NO_LOC = -10000
#########################################################

###################### FUNCTIONS ########################

#########################################################

#########################################################
# Class : YahooWeather                                  #
#########################################################
class YahooWeather(object):
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    def __init__(self, basename, unitsMetric, LocationStr, ApiKey = None):
        self.verbose=True
        self.logger = logging.getLogger('{}.YahooWeather'.format(basename))
        if unitsMetric:
            self.units='c'
        else:
            self.units='f'
        self.ApiKey = ApiKey
        self.LocationStr = LocationStr
        self.woeid = NO_LOC
        try:
            self.GetLocation(LocationStr)
        except:
            pass

    def __del__(self):
        pass

    def GetLocation(self, LocationStr):
        woeid_query='select woeid from geo.places(1) where text="{}"'.format(LocationStr)
        yql_url = self.baseurl + urllib.urlencode({'q':woeid_query}) + "&format=json"
        result = requests.get(yql_url)
        data = json.loads(result.text)

        try:
            if data['query']['count']>1:
                self.logger.error("Location cannot be found unambiguously, exiting ...")
                return False
            else:
                self.woeid=data['query']['results']['place']['woeid']
                self.logger.info("Obtained location data woeid = %s", self.woeid)
        except:
            return False

        return True

    def Get5dayForecast(self):
        params = {}
        doForecast = True
        if self.woeid == NO_LOC:
            doForecast = self.GetLocation(self.LocationStr)
        if doForecast:
            if not self.units:
                yql_unit=""
            else:
                yql_unit=" and u='{}'".format(self.units.lower())

            try:
                yql_query = "select item.forecast from weather.forecast where woeid={}{}".format(self.woeid,yql_unit)
                yql_url = self.baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
                result = requests.get(yql_url)
                data = json.loads(result.text)
                forecast=data['query']['results']['channel']

                self.logger.info("Queried: 5 day forecast")
                l = len(forecast)
                if l>5:
                    l=5
                for i in range (0, l):
                    if self.verbose:
                        self.logger.debug("Date            : %s","{} {}".format(forecast[i]['item']['forecast']['day'],forecast[i]['item']['forecast']['date']))
                        self.logger.debug("High Temperature: %d",int(round(float(forecast[i]['item']['forecast']['high']))))
                        self.logger.debug("Low Temperature : %d",int(round(float(forecast[i]['item']['forecast']['low']))))
                        self.logger.debug("Precipation     : %f",self._getPrecipation(forecast[i]['item']['forecast']['text']))
                        self.logger.debug("Clouds          : %d",self._getClouds(forecast[i]['item']['forecast']['text']))
                        self.logger.debug("Wind speed      : %d",'0')
                        self.logger.debug("Wind angle      : %d",'0')
                        self.logger.debug("-------------------")
                    params['high'+str(i)] = int(round(float(forecast[i]['item']['forecast']['high'])))
                    params['low'+str(i)] = int(round(float(forecast[i]['item']['forecast']['low'])))
                    params['precipation'+str(i)] = self._getPrecipation(forecast[i]['item']['forecast']['text'])
                    params['clouds'+str(i)] = self._getClouds(forecast[i]['item']['forecast']['text'])
                    params['windspeed'+str(i)] = 0 # unavailable
                    params['windangle'+str(i)] = 0 # unavailable
            except:
                pass

        return params

    def GetCurrent(self):
        params = {}
        doForecast = True
        if self.woeid == NO_LOC:
            doForecast = self.GetLocation(self.LocationStr)
        if doForecast:
            if not self.units:
                yql_unit=""
            else:
                yql_unit=" and u='{}'".format(self.units.lower())

            try:
                yql_query = "select item.condition,wind from weather.forecast where woeid={}{}".format(self.woeid,yql_unit)
                yql_url = self.baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
                result = requests.get(yql_url)
                data = json.loads(result.text)

                forecast=data['query']['results']['channel']

                self.logger.info("Queried: Current weather")
                if self.verbose:
                    self.logger.debug("Date               : %s","{}".format(forecast['item']['condition']['date']))
                    self.logger.debug("Current Temperature: %d",int(round(float(forecast['item']['condition']['temp']))))
                    self.logger.debug("Current Precipation: %f",self._getPrecipation(forecast['item']['condition']['text']))
                    self.logger.debug("Current Clouds     : %d",self._getClouds(forecast['item']['condition']['text']))
                    self.logger.debug("Current Wind speed : %d",int(round(float(forecast['wind']['direction']))))
                    self.logger.debug("Current Wind angle : %d",int(round(float(forecast['wind']['speed']))))
                    self.logger.debug("-------------------")
                params['current_temp'] = int(round(float(forecast['item']['condition']['temp'])))
                params['current_precipation'] = self._getPrecipation(forecast['item']['condition']['text'])
                params['current_clouds'] = self._getClouds(forecast['item']['condition']['text'])
                params['current_windspeed'] = int(round(float(forecast['wind']['speed'])))
                params['current_windangle'] = int(round(float(forecast['wind']['direction'])))
            except:
                pass

        return params

    def _getPrecipation(self, input):
        # precipation is unavialable, so lets guess from text information
        precip = 0
        p1 = ['drizzle', 'light snow showers', 'blowing snow', 'sleet', 'haze']
        p2 = ['mixed', 'freezing rain', 'snow flurries', 'hail', 'isolated thunderstorms', 'scattered', 'thundershowers', 'snow showers']
        p3 = ['showers', 'snow']
        p4 = ['tornado', 'tropical storm', 'hurricane', 'thunderstorms', 'heavy snow']
        p6 = ['severe thunderstorms']
        if any(x in input.lower() for x in p1):
            precip = 1
        elif any(x in input.lower() for x in p2):
            precip = 2
        elif any(x in input.lower() for x in p3):
            precip = 3
        elif any(x in input.lower() for x in p4):
            precip = 4
        elif any(x in input.lower() for x in p6):
            precip = 6

        return precip

    def _getClouds(self, input):
        # cloud information is unavialable, so lets guess from text information
        clouds = 100
        c20 = ['fair']
        c50 = ['tornado', 'tropical storm', 'hurricane', 'dust', 'smoky', 'blustery', 'windy', 'partly cloudy']
        c80 = ['mostly cloudy', 'scattered thunderstorms']
        c0 = ['not available', 'cold', 'clear', 'sunny', 'hot']
        if any(x in input.lower() for x in c20):
            clouds = 20
        elif any(x in input.lower() for x in c50):
            clouds = 50
        elif any(x in input.lower() for x in c80):
            clouds = 80
        elif any(x in input.lower() for x in c0):
            clouds = 0

        return clouds

"""                  precip[mm] clouds[%]
0   tornado                 4   50
1   tropical storm          4   50
2   hurricane               4   50
3   severe thunderstorms    6   100
4   thunderstorms           4   100
5   mixed rain and snow     2   100
6   mixed rain and select   2   100
7   mixed snow and select   2   100
8   freezing drizzle        1   100
9   drizzle                 1   100
10  freezing rain           2   100
11  showers                 3   100
12  showers                 3   100
13  snow flurries           2   100
14  light snow showers      1   100
15  blowing snow            1   100
16  snow                    3   100
17  hail                    2   100
18  sleet                   1   100
19  dust                    0   50
20  foggy                   0   100
21  haze                    1   100
22  smoky                   0   50
23  blustery                0   50 
24  windy                   0   50 
25  cold                    0   0
26  cloudy                  0   100
27  mostly cloudy (night)   0   80
28  mostly cloudy (day)     0   80
29  partly cloudy (night)   0   50
30  partly cloudy (day)     0   50
31  clear (night)           0   0
32  sunny                   0   0
33  fair (night)            0   20
34  fair (day)              0   20  
35  mixed rain and hail     2   100
36  hot                     0   0
37  isolated thunderstorms  2   100
38  scattered thunderstorms 2   80
39  scattered thunderstorms 2   80
40  scattered showers       2   100
41  heavy snow              4   100
42  scattered snow showers  2   100
43  heavy snow              4   100
44  partly cloudy           0   50
45  thundershowers          2   100
46  snow showers            2   100
47  isolated thundershowers 2   100
3200    not available       0   0
"""