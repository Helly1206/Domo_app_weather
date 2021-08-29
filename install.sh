#!/bin/bash
INSTALL="/usr/bin/install -c"
INSTALL_DATA="$INSTALL -m 644"
INSTALL_PROGRAM="$INSTALL"
INSTALL_FOLDER="cp -r "
NAME="Domotion"
ETCDIR="/etc"
ETCLOC="$ETCDIR/$NAME"
OPTDIR="/opt"
OPTLOC="$OPTDIR/$NAME"
APPS="apps"
APPLOC="$OPTLOC/$APPS"
APPSNAME="DomoApps"
STARTAPP="StartApp"
SERV=".service"
SERVICEDIR="$ETCDIR/systemd/system"
APPSSERVICESCRIPT="$APPSNAME""$SERV"
PRE="app_"
PY=".py"
XML=".xml"
DEBFOLDER="debian"

if [ "$EUID" -ne 0 ]
then
	echo "Please execute as root ('sudo install.sh')"
	exit
fi

APPNAME=$(find ".$APPLOC" -name "$PRE"*"$PY")
APPBASE=$(basename "$APPNAME" "$PY")

if [ -z "$APPNAME" ]
then
	echo "No apps found, folder corrupted"
	exit
else
	echo "App found: $APPBASE"
fi

APPPY="$APPBASE""$PY"
APPXML="$APPBASE""$XML"
APPDIR="$APPBASE""d"
OPTLOC2="$OPTDIR""/Domo_""$APPBASE"
SERVICESCRIPT="Domo_""$APPBASE""$SERV"

if [ "$1" == "-u" ] || [ "$1" == "-U" ]
then
	echo "$APPBASE uninstall script"

	if [ "$#" -gt 1 ]; then
		OPTLOC="$2"
	fi

    APPSLOC="$OPTLOC/$APPS"

	if [ ! -d "$OPTLOC" ]; then
		echo "Domotion installation not found"
		echo "Try: ./install.sh -u <alternative folder name>"
		echo "See also: ./install.sh -h"
		exit
	fi

	if [ ! -d "$APPSLOC" ]; then
		echo "Domotion apps not found"
		echo "This Domotion version is probably not able to deal with apps"
		echo "or the selected installation folder is incorrect"
		exit
	fi

	echo "Uninstalling $APPBASE"
	systemctl stop $APPSSERVICESCRIPT

	echo "Uninstalling $APPXML"
	if [ -e "$APPSLOC/$APPXML" ]; then rm -f "$APPSLOC/$APPXML"; fi
	echo "Uninstalling $APPPY"
	if [ -e "$APPSLOC/$APPPY" ]; then rm -f "$APPSLOC/$APPPY"; fi
	echo "Uninstalling $APPDIR"
	if [ -d "$APPSLOC/$APPDIR" ]; then rm -rf "$APPSLOC/$APPDIR"; fi

	echo "Uninstalling finished, try restarting $APPSNAME service"
	systemctl start $APPSSERVICESCRIPT
elif [ "$1" == "-e" ] || [ "$1" == "-E" ]
then
	echo "$APPBASE uninstall decentralized script"

	if [ "$#" -gt 1 ]; then
		OPTLOC2="$2"
	fi

	if [ ! -d "$OPTLOC2" ]; then
		echo "Domotion installation not found"
		echo "Try: ./install.sh -e <alternative folder name>"
		echo "See also: ./install.sh -h"
		exit
	fi

	echo "Uninstalling daemon $SERVICESCRIPT"
	systemctl stop "$SERVICESCRIPT"
	systemctl disable "$SERVICESCRIPT"
	if [ -e "$SERVICEDIR/$SERVICESCRIPT" ]; then rm -f "$SERVICEDIR/$SERVICESCRIPT"; fi

	echo "Uninstalling $APPBASE"

	if [ -d "$OPTLOC2" ]; then rm -rf "$OPTLOC2"; fi

	echo "Uninstalling finished"

elif [ "$1" == "-h" ] || [ "$1" == "-H" ]
then
	echo "Usage:"
	echo "  <no argument>: install $APPBASE"
	echo "  -u/ -U       : uninstall $APPBASE"
	echo "  -h/ -H       : this help file"
    echo "  -d/ -D       : build debian package"
    echo "  -s/ -S       : build debian standalone package"
	echo "  -l/ -L       : install decentralized (on another location)"
	echo "  -e/ -E       : uninstall decentralized (on another location)"
	echo "  -c/ -C       : Cleanup compiled files in install folder"
	echo "  <folder>     : as second argument, alternative installation folder"
elif [ "$1" == "-c" ] || [ "$1" == "-C" ]
then
	echo "$APPBASE Deleting compiled files in install folder"
	py3clean .
    rm -f ./*.deb
    rm -rf "$DEBFOLDER"
elif [ "$1" == "-d" ] || [ "$1" == "-D" ]
then
	echo "$APPBASE build debian package"
    rm -rf "$DEBFOLDER"
    cp -R debianapp "$DEBFOLDER"
	py3clean .
	fakeroot debian/rules clean binary
	mv ../*.deb .
elif [ "$1" == "-s" ] || [ "$1" == "-S" ]
then
	echo "$APPBASE build debian standalone package"
    rm -rf "$DEBFOLDER"
    cp -R debiansta "$DEBFOLDER"
	py3clean .
	fakeroot debian/rules clean binary
	mv ../*.deb .
elif [ "$1" == "-l" ] || [ "$1" == "-L" ]
then
	echo "$APPBASE install decentralized script"

	if [ "$#" -gt 1 ]; then
		OPTLOC2="$2"
	fi

	if [ ! -d "$OPTLOC2" ]; then
		mkdir "$OPTLOC2"
		chmod 755 "$OPTLOC2"
	fi

	echo "Installing $APPBASE"

	py3clean .

	if [ -e "$APPSLOC/$APPXML" ]; then rm -f "$APPSLOC/$APPXML"; fi
	echo "Uninstalling $APPPY"
	if [ -e "$APPSLOC/$APPPY" ]; then rm -f "$APPSLOC/$APPPY"; fi
	echo "Uninstalling $APPDIR"
	if [ -d "$APPSLOC/$APPDIR" ]; then rm -rf "$APPSLOC/$APPDIR"; fi
	echo "Installing $APPXML"

	if [ ! -e "./$APPXML" ]; then
		echo "$APPXML not found for this app, skipping"
	else
		if [ ! -d "$ETCLOC" ]; then
			mkdir "$ETCLOC"
			chmod 755 "$ETCLOC"
		fi
		if [ ! -e "$ETCLOC/$APPXML" ]; then
			$INSTALL_DATA ".$ETCLOC/$APPXML" "$ETCLOC/$APPXML"
		fi
	fi

	echo "Installing $APPPY"

	if [ ! -e "./$APPPY" ]; then
		echo "$APPPY not found for this app, skipping"
	else
		$INSTALL_PROGRAM ".$APPLOC/$APPPY" "$OPTLOC2/$APPPY"
	fi

	echo "Installing $APPDIR"

	if [ ! -e "./$APPDIR" ]; then
		echo "$APPDIR not found for this app, skipping"
	else
		$INSTALL_FOLDER ".$APPLOC/$APPDIR" "$OPTLOC2/$APPDIR"
	fi

	echo "Installing $STARTAPP"

	if [ ! -e "./$STARTAPP" ]; then
		echo "$STARTAPP not found for this app, skipping"
	else
		$INSTALL_PROGRAM ".$OPT/$STARTAPP" "$OPTLOC2/$STARTAPP"
	fi

	echo "Installing text files"
	if [ -e "./$CHANGELOG.txt" ]; then
		$INSTALL_PROGRAM "./$CHANGELOG.txt" "$OPTLOC2/$CHANGELOG.txt"
	fi
	if [ -e "./$LICENSE.txt" ]; then
		$INSTALL_PROGRAM "./$LICENSE.txt" "$OPTLOC2/$LICENSE.txt"
	fi
	if [ -e "./$README.txt" ]; then
		$INSTALL_PROGRAM "./$README.txt" "$OPTLOC2/$README.txt"
	fi

	echo "Installing decentralized common folder"
	COMMONLOC="$OPTLOC2""/appcommon"
	if [ ! -d "$COMMONLOC" ]; then
		mkdir "$COMMONLOC"
		chmod 755 "$COMMONLOC"
	fi

	CURLOC=$(pwd)
	cd $COMMONLOC
	wget https://raw.githubusercontent.com/Helly1206/Domotion/master/apps/appcommon/appcommon.py
	wget https://raw.githubusercontent.com/Helly1206/Domotion/master/apps/appcommon/bdaclient.py
	wget https://raw.githubusercontent.com/Helly1206/Domotion/master/apps/appcommon/bdauri.py
	cd $CURLOC

	echo "Installing daemon $APPBASE"
	read -p "Do you want to install an automatic startup service for $APPBASE (Y/n)? " -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Nn]$ ]]
	then
		echo "Skipping install automatic startup service for $APPBASE"
	else
		echo "Install automatic startup service for $APPBASE"
		$INSTALL_DATA ".$SERVICEDIR/$SERVICESCRIPT" "$SERVICEDIR/$SERVICESCRIPT"

		systemctl enable $SERVICESCRIPT
		systemctl start $SERVICESCRIPT
	fi

	echo "Installing finished"

else
	echo "$APPBASE install script"

	if [ "$#" -gt 1 ]; then
		OPTLOC="$2"
	elif [ "$#" -eq 1 ]; then
		OPTLOC="$1"
	fi

	if [ ! -d "$OPTLOC" ]; then
		echo "Domotion installation not found"
		echo "Try: ./install.sh -l <alternative folder name>"
		echo "See also: ./install.sh -h"
		exit
	fi

	APPSLOC="$OPTLOC/$APPS"

	if [ ! -d "$APPSLOC" ]; then
		echo "Domotion apps not found"
		echo "This Domotion version is probably not able to deal with apps"
		echo "or the selected installation folder is incorrect"
		exit
	fi

	echo "Installing $APPBASE"

	py3clean .

	echo "Installing $APPXML"

	if [ ! -e "./$APPXML" ]; then
		echo "$APPXML not found for this app, skipping"
	else
		if [ ! -d "$ETCLOC" ]; then
			mkdir "$ETCLOC"
			chmod 755 "$ETCLOC"
		fi
		if [ ! -e "$ETCLOC/$APPXML" ]; then
			$INSTALL_DATA ".$ETCLOC/$APPXML" "$ETCLOC/$APPXML"
		fi
	fi

	echo "Installing $APPPY"

	if [ ! -e "./$APPPY" ]; then
		echo "$APPPY not found for this app, skipping"
	else
		$INSTALL_PROGRAM ".$APPLOC/$APPPY" "$APPSLOC/$APPPY"
	fi

	echo "Installing $APPDIR"

	if [ ! -e "./$APPDIR" ]; then
		echo "$APPDIR not found for this app, skipping"
	else
		$INSTALL_FOLDER ".$APPLOC/$APPDIR" "$APPSLOC/$APPDIR"
	fi

	echo "Installation finished, try restarting $APPSNAME service to include and start app"
	systemctl stop $APPSSERVICESCRIPT
	systemctl start $APPSSERVICESCRIPT
fi
