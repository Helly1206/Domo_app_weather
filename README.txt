app_weather v0.9.0
=========== ======

This is a Domotion app optaining the weather from OpenWeatherMap or Yahoo weather. Weather information can be used in Domotion to control devices.

Install:
--------

Weather app can be installed using: install.sh
Start as: sudo ./install.sh <arguments>
  <no argument>: install app_weather
  -u/ -U       : uninstall app_weather
  -h/ -H       : this help file
  -d/ -D       : install decentralized (on another location, '/opt/Domo_app_weather', when running standalone not on the Domotion system)
  -e/ -E       : uninstall decentralized (on another location)  
  -c/ -C       : Cleanup compiled files in install folder
  <folder>     : as second argument, alternative installation folder (service needs to be adapted manually if used)

Weather app can be installed in the '/opt/Domotion/apps' folder and is totally handled by Domotion. If you require the app to be installed on a different system, it is installed in '/opt/Domo_app_weather' and is started by the service as a stand-alone app. The app connects to Domotion which runs a BDA (Basic Device access) server.

Domotion 1.10 or higher must be installed to be able to install apps and use then with Domotion.

Settings:
---------

Settings are stored in app_weather.xml, by default located at '/etc/Domotion', or alternatively (if no access to '/etc/Domotion') at the home folder.

The following settings can be altered:
<domoapp>
	<app>												--> App specific settings
		<location>New York, US</location> 				--> Location for the weather app to check, try at 'https://www.openweathermap.org' or 'https://www.yahoo.com/news/weather' if it works
		<unitsmetric>True</unitsmetric>					--> If True, then Celcius and metric units, else Farenheit and imperai units.
		<apikey></apikey>								--> apikey for openweathermap, obtain one at: 'https://home.openweathermap.org/users/sign_up' for a free api key
		<weatheryahoo>False</weatheryahoo>				--> If True, the yahoo is used, else openweathermap is used
		<conditionsdaily>								--> Daily conditions to set the shade parameter (parameter is set high if complies)
			<high>24</high>								--> Maximum temperature higher then .. degrees
			<low>-15</low>								--> Minimum temperature lower then .. degrees
		</conditionsdaily>
		<conditionscurrent>								--> Current conditions to set the shade parameter (parameter is set high if complies and not overruled by dailyconditions)
			<temp>24</temp>								--> Current temperature higher then .. degrees
			<condition1>								--> Subcondition, implements and function
				<precipation>1</precipation>			--> Precipation more than 1 ...
				<clouds>70</clouds>						--> Clouds more that 70 %
			</condition1>
		</conditionscurrent>
	</app>
	<common>											--> Common settings for apps
		<verbose>False</verbose>						--> Log verbosity, set to false except for debugging
		<server></server>								--> Domotion IP or name if not on local system
		<port>60004</port>								--> Port on which the BDA server (Domotion) is running
		<url>app_weather</url>							--> URL for BDA server (can be changed if more instances of the app are running)
		<interval>600</interval>						--> Interval for querying current weather
		<times>											--> Time(s) for querying 5 days forecast
			<time1>5:55</time1>							--> Time for querying 5 days forecast
		</times>
		<username></username>							--> Username, or leave empty if running on local system
		<password></password>							--> Password, or leave empty if running on local system
	</common>
</domoapp>

Logging:
--------

Weather app logs to app_weather.log, by default located at '/var/log', or alternatively (if no access to '/var/log') at the home folder.

Controls for Domotion:
----------------------

The following controls are sent to Domotion. They can be captured if required. Add a control/ sensor:
Type= Input from URL
DeviceURL= <myip>/app_weather (if url if xml file is set to a different name, enter this name here)
KeyTAG= current_temp (or whatever parameter you are interested in)
SensorType= Temperature (or anything else)
Poll= False

The following parameters are available:
current_temp
current_precipation
current_clouds
current_windspeed
current_windangle

n = 0..4
highn
lown
precipationn
cloudsn
windspeedn
windanglen

That's all for now ...

Please send Comments and Bugreports to hellyrulez@home.nl
