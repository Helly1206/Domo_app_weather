# -*- coding: utf-8 -*-
#########################################################
# SERVICE : app_weather.py                              #
#           Python app for getting weather information  #
#           from Yahoo or OpenWeatherMap                #
#           I. Helwegen 2018                            #
#########################################################

####################### IMPORTS #########################
from appcommon import appcommon
from app_weatherd import YahooWeather
from app_weatherd import OpenWeatherMap
from requests import ConnectionError

#########################################################
# Class : appcommon                                     #
# Main function: Do NOT Change name                     #
#########################################################
# DON'T Change this code                                #
#########################################################
class app(appcommon):
    def __init__(self):
        super(app, self).__init__(__file__)

    def __del__(self):
        super(app, self).__del__()

#########################################################
# Implement your code here                              #
#########################################################
    def init(self):
        self.weatherinfo = None
        self.dailyshade = 0
        self.currentshade = 0
    
        self.logger.info("Starting app: app_weather")
        self.appParams=self.ReadAppParams()
        self.logger.debug(self.appParams)
        
        try:
            if self.str2bool(self.appParams['weatheryahoo']):
                self.weatherinfo = YahooWeather(self.getBaseName(), self.str2bool(self.appParams['unitsmetric']), self.appParams['location'], self.appParams['apikey'])
            else:
                self.weatherinfo = OpenWeatherMap(self.getBaseName(), self.str2bool(self.appParams['unitsmetric']), self.appParams['location'], self.appParams['apikey'])
        except KeyError:
            self.logger.error("Error: XML file error")
        except ConnectionError:
            self.logger.error("Error: Obtaining location info, connection error")
        except Exception, e:
            self.logger.exception(e)
        

    def loop(self):
        current = False
        try:
            if (self.update()):
                if self.isIntervalUpdate():
                    current = True
                    params = self.weatherinfo.GetCurrent()
                    self.currentshade = self.CurrentShade(self.appParams, params)
                else:
                    params = self.weatherinfo.Get5dayForecast()
                    self.dailyshade = self.DailyShade(self.appParams, params)
                if params:
                    params['shade']=self.dailyshade or self.currentshade
                    params['fullshade']=(self.dailyshade>1) or (self.currentshade>1)
                    self.logger.debug(params)
                    self._loginfo(params, current)
                    self.setparameters(params)
        except KeyError:
            self.logger.error("Error: XML file error")
        except ConnectionError:
            self.logger.error("Error: Obtaining weather info, connection error; current:%d; retry in 1m", current)
            self.tryAgainIn1Minute(current)
        except Exception, e:
            self.logger.exception(e)

    def exit(self):
        del self.weatherinfo
        self.logger.info("Ready")

    def callback(self, tag, value):
        rtag = None
        rvalue = None
        if tag:
            if not value and params: # set is not allowed, get is
                if tag in params.keys():
                    rtag = tag
                    rvalue = params[tag]
        return rtag, rvalue

#########################################################
# Local methods to implement                            # 
######################################################### 
    def _loginfo(self, params, current):
        if current:
            self.logger.info("T:%d, p:%f, c:%d, w:%d;%d s:%d;%d", params['current_temp'], params['current_precipation'], params['current_clouds'], params['current_windspeed'], params['current_windangle'], self.currentshade, params['shade'])
        else:
            self.logger.info("Tl:%d, Th: %d, p:%f, c:%d, w:%d;%d s:%d;%d", params['low0'], params['high0'], params['precipation0'], params['clouds0'], params['windspeed0'], params['windangle0'], self.dailyshade, params['shade'])

    def _getKey(self, params, key):
        retval = None
        for paramkey in params.keys():
            if key in paramkey:
                retval = paramkey
    
        return retval
    
    def _getShadeParam(self, shadeParams, key, params):
        retval = False
    
        if key == "low":
            if self._getKey(params, key):
                try:
                    retval = (float(params[self._getKey(params, key)]) <= float(shadeParams[key]))
                except:
                    pass
        else:
            if self._getKey(params, key):
                try:
                    retval = (float(params[self._getKey(params, key)]) >= float(shadeParams[key]))
                except:
                    pass
    
        return retval
    
    def _getShade(self, shadeParams, params):
        shade = False
    
        for param in shadeParams.keys():
            if isinstance(shadeParams[param],dict):
                _shade = True
                count = 0
                for subparam in shadeParams[param].keys():
                    _shade = _shade and self._getShadeParam(shadeParams[param], subparam, params)
                    count += 1
                if count > 0:
                    shade = shade or _shade
            else:
                shade = shade or self._getShadeParam(shadeParams, param, params)
    
        return shade
    
    def DailyShade(self, appParams, params):
        shade = 0
        todaysparams = {}
    
        #get only today
        for key in params.keys():
            if key[-1] == '0':
                todaysparams[key] = params[key]
    
        if 'conditionsdaily' in appParams:
            if self._getShade(appParams['conditionsdaily'], todaysparams):
                shade = 1
        if 'conditionsdailyfull' in appParams:
            if self._getShade(appParams['conditionsdaily'], todaysparams):
                shade = 2
    
        return shade
    
    def CurrentShade(self, appParams, params):
        shade = False
        if 'conditionscurrent' in appParams:
            if self._getShade(appParams['conditionscurrent'], params):
                shade = 1
        if 'conditionscurrentfull' in appParams:
            if self._getShade(appParams['conditionscurrent'], params):
                shade = 2
    
        return shade

#########################################################
# Main for local calling                                # 
#########################################################     
# Do NOT Change code to be able to perform autostarting #
#########################################################
if __name__ == "__main__":
    app().ismain()
