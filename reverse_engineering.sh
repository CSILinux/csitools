#!/usr/bin/env bash

#Reverse Engineering Tools Script

red=`tput setaf 1`
reset=`tput sgr0`

#define choices
opt1="NSA Ghidra"
opt2="Radare2"
opt99="Exit"

timestamp=$(date +%Y-%m-%d:%H:%M)

relmenu=$(zenity  --list  --title "Reverse Engineering:Choose Tool" --text "What tool do you want to use?" --width=400 --height=250 --radiolist  --column "Choose" --column "Option" TRUE "$opt1" FALSE "$opt2" 2> >(grep -v 'GtkDialog' >&2)) 

case $socialmenu in
			
	$opt1 ) #Ghidra
		gnome-terminal -e ghidra
	;;

	$opt2 ) #radare2
		gnome-terminal -e radare2
	;;
	esac
	exit 1
}

