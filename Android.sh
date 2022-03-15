DOGE="ㅤ\n \n "

LEGEND+="\n░░░░░░░░░█▐▓█░░░░░░░░█▀▄▓▌█░░░░░░"

LEGEND+="\n░░░░░░░░░█▐▓▓████▄▄▄█▀▄▓▓▓▌█░░░░░"

LEGEND+="\n░░░░░░░▄██▐▓▓▓▄▄▄▄▀▀▀▄▓▓▓▓▓▌█░░░░"

LEGEND+="\n░░░░░▄█▀▀▄▓█▓▓▓▓▓▓▓▓▓▓▓▓▀░▓▌█░░░░"

LEGEND+="\n░░░░█▀▄▓▓▓███▓▓▓███▓▓▓▄░░▄▓▐█▌░░░"

LEGEND+="\n░░░█▌▓▓▓▀▀▓▓▓▓███▓▓▓▓▓▓▓▄▀▓▓▐█░░░"

LEGEND+="\n░░▐█▐██▐░▄▓▓▓▓▓▀▄░▀▓▓▓▓▓▓▓▓▓▌█▌░░"

LEGEND+="\n░░█▌███▓▓▓▓▓▓▓▓▐░░▄▓▓███▓▓▓▄▀▐█░░"

LEGEND+="\n░▐█▐█▓▀░░▀▓▓▓▓▓▓▓▓▓██████▓▓▓▓▐█░░"

LEGEND+="\n░▐▌▓▄▌▀░▀░▐▀█▄▓▓██████████▓▓▓▌█▌░"

LEGEND+="\n░▐▌▓▓▓▄▄▀▀▓▓▓▀▓▓▓▓▓▓▓▓█▓█▓█▓▓▌█▌░"

LEGEND+="\n░░█▐▓▓▓▓▓▓▄▄▄▓▓▓▓▓▓█▓█▓█▓█▓▓▓▐█░░"

LEGEND+="\n░░░█▐▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▐█░░░"

LEGEND+="\n "

LEGEND+="\n🐶 ㅤLEGEND ㅤUSERBOT ㅤSETUP ㅤ🐾"

INFOX="📣 Telegram: @LegendUserBot"

INFOX+="\n "

INFOX+="\n💫 DON'T EXIT THE APP WHILE THE PROCESS IS RUNNING!"

INFOX+="\n "

INFOX+="\n💫 Qurulum DAVAM EDƏRKEN PROQRAMDAN AYRILMAYIN!"

HELX="📌 WRITE Y AND ENTER WHEN THE SETUP IS PAUSED AT 50%, 70% AND 75%!"

HELX+="\n "

HELX+="\n📌 QURULUM %50, %70 VE %75'TE DURAKLADIĞINDA Y YAZIP ENTER'LAYIN!"

PACKAGEX="⏳ UPDATING PACKAGES..."

PACKAGEX+="\n "

PACKAGEX+="\n⏳ PAKETLƏRİ GÜNCƏLLƏYİRƏM..."

PYTHOX="⌛ INSTALLING PYTHON..."

PYTHOX+="\n "

PYTHOX+="\n⌛ PYTHON Qururam..."

GIX="⌛ INSTALLING GIT..."

GIX+="\n "

GIX+="\n⌛ GIT Qururam..."

REQUIREX="⌛ INSTALLING REQUIREMENTS..."

REQUIREX+="\n "

REQUIREX+="\n⌛ Tələbləri qururam..."

SPACEX="\n "

clear

echo -e $LEGEND

echo -e $SPACEX

echo -e $HELX

echo -e $SPACEX

echo -e $PACKAGEX

echo -e $SPACEX

pkg update -y

clear

echo -e $LEGEND

echo -e $SPACEX

echo -e $INFOX

echo -e $SPACEX

echo -e $PYTHOX

echo -e $SPACEX

pkg install python -y

pip install --upgrade pip

clear

echo -e $LEGEND

echo -e $SPACEX

echo -e $INFOX

echo -e $SPACEX

echo -e $GIX

echo -e $SPACEX

pkg install git -y

clear

echo -e $LEGEND

echo -e $SPACEX

echo -e $INFOX

echo -e $SPACEX

echo -e $REQUIREX

echo -e $SPACEX

pip install wheel

pip uninstall legendsetup -y

pip install legendsetup

python3 -m legendsetup 
