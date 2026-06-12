# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x10\xad\
#\
 See Configurati\
on in README.md \
for details on h\
ow to use this f\
ile.\x0a\x0a# Before b\
undling the app \
with pyinstaller\
 or compiling it\
 with pyside6-de\
ploy,\x0a# this con\
fig file must be\
 transpiled to a\
 QResource, whic\
h is done by run\
ning:\x0a# `uv run \
pyside6-rcc ./sr\
c/mora_the_explo\
rer/resources.qr\
c -o ./src/mora_\
the_explorer/res\
ources.py`\x0a\x0avers\
ion = 1\x0a\x0a[option\
s]\x0auser = \x22mjm\x22\x0a\
group = \x22gil\x22\x0asp\
ec = \x22neo400\x22\x0are\
peat_switch = fa\
lse\x0arepeat_delay\
 = 5\x0a\x0a[options.n\
aming]\x0asample_fo\
rmat = \x22{user}-{\
user2}-{sample_i\
d}\x22\x0ameasurement_\
format.bruker = \
\x22{user}-{user2}-\
{sample_id}_{ins\
trument}_{submis\
sion_time:%d%m%y\
}_{temperature}k\
_{experiment}_{m\
easurement_no}\x22\x0a\
measurement_form\
at.agilent = \x22{u\
ser}-{user2}-{sa\
mple_id}_{instru\
ment}_{completio\
n_time:%d%m%y}_{\
temperature}k_{e\
xperiment}_{meas\
urement_no}\x22\x0a\x0a\x0a[\
appearance]\x0astar\
t_button_colour \
= \x22#b88cce\x22\x0a\x0a\x0a[p\
aths]\x0awindows = \
\x22//samba.public.\
os.wwu.de/usersh\
are/projects/q_n\
mr-oc/nmr\x22\x0adarwi\
n = \x22/Volumes/us\
ershare/projects\
/q_nmr-oc/nmr\x22  \
# darwin = macOS\
\x0alinux = \x22~/user\
share/projects/q\
_nmr-oc/nmr\x22\x0asrc\
 = \x22mora_the_exp\
lorer/src/mora-t\
he-explorer\x22\x0asav\
e = \x22\x22\x0a\x0a\x0a[admin]\
\x0apattern_separat\
or = '[\x5cs_-]' # \
Note the single \
quotes! (= liter\
al string)\x0aversi\
on = \x222.0.0b7\x22\x0ae\
mail = \x22milner@u\
ni-muenster.de\x22\x0a\
changelog = \x22\x22\x22\x0a\
- Update for mov\
e to new server\x0a\
- Big rewrite, c\
odebase is now m\
uch more structu\
red and maintain\
able\x0a- The searc\
h can be set to \
always check the\
 current date wh\
ich changes acco\
rdingly\x0a- Spectr\
a always sorted \
into subfolders \
by sample (like \
Agilent spectra)\
\x0a- Paths are sel\
ected using the \
system file expl\
orer\x0a- Ability t\
o specify the se\
rver address fro\
m the GUI (usefu\
l on macOS and L\
inux)\x0a- Solvent,\
 instrument, exp\
eriment, tempera\
ture metadata ex\
tracted on all s\
pectrometers\x0a- M\
etadata are save\
d to the measure\
ment folder in m\
ora.toml\x0a- CLI a\
nd Python API wo\
rk entirely inde\
pendently of a G\
UI\x0a\x22\x22\x22\x0a\x0a\x0a[groups\
]\x0afer = \x22fernand\
ez\x22\x0agar = \x22garci\
a\x22\x0agil = \x22gilmou\
r\x22\x0aglo = \x22gloriu\
s\x22\x0ahei = \x22hein\x22\x0a\
nae = \x22naesborg\x22\
\x0arav = \x22ravoo\x22\x0as\
tu = \x22studer\x22\x0a\x0a[\
groups.other]\x0aac\
 = \x22ac\x22\x0abiochemi\
e = \x22biochemie\x22\x0a\
extern = \x22extern\
\x22\x0aipc = \x22ipc\x22\x0akb\
 = \x22kb\x22\x0ameet = \x22\
meet\x22\x0anuk = \x22nuk\
\x22\x0aocf = \x22ocf\x22\x0aph\
armazie = \x22pharm\
azie\x22\x0a\x0a\x0a[spectro\
meters]\x0a\x0a[spectr\
ometers.archiv]\x0a\
manufacturer = \x22\
bruker\x22\x0adisplay_\
name = \x22Pre-2020\
 archive (Bruker\
)\x22\x0ameasurement_p\
attern = '<group\
!>\x5c_*<user_name>\
?\x5c_*<user!>\x5c_*<u\
ser2!>?\x5c_*<sampl\
e_id!>' # Note t\
he single quotes\
! (= literal str\
ing)\x0adate_entry \
= \x22dd MMM yyyy\x22\x0a\
check_paths = [\x0a\
    \x22archiv/dpx3\
00/{date:%y}-dpx\
300_{date:%Y}/{d\
ate:%b%d-%Y}\x22,\x0a \
   \x22archiv/av300\
/{date:%y}-av300\
_{date:%Y}/{date\
:%b%d-%Y}\x22,\x0a    \
\x22archiv/av400/{d\
ate:%y}-av400_{d\
ate:%Y}/{date:%b\
%d-%Y}\x22,\x0a    \x22ar\
chiv/neo400a/{da\
te:%y}-neo400a_{\
date:%Y}/neo400a\
_{date:%b%d-%Y}\x22\
,\x0a    \x22archiv/ne\
o400b/{date:%y}-\
neo400b_{date:%Y\
}/neo400b_{date:\
%b%d-%Y}\x22,\x0a    \x22\
archiv/neo400c/{\
date:%y}-neo400c\
_{date:%Y}/neo40\
0c_{date:%b%d-%Y\
}\x22,\x0a]\x0aadmin_only\
 = true\x0asingle_c\
heck_only = fals\
e\x0a\x0a[spectrometer\
s.av300]\x0amanufac\
turer = \x22bruker\x22\
\x0adisplay_name = \
\x22Studer group NM\
R only (300 MHz)\
\x22\x0ameasurement_pa\
ttern = '<group!\
>\x5c_*<user_name>?\
\x5c_*<user!>\x5c_*<us\
er2!>?\x5c_*<sample\
_id!>'\x0adate_entr\
y = \x22dd MMM yyyy\
\x22\x0acheck_paths = \
[\x0a    \x22av300/av1\
/{date:%b%d-%Y}\x22\
,\x0a]\x0aarchives = [\
\x0a    \x22av300/av1/\
{date:%y}-av300_\
{date:%Y}/{date:\
%b%d-%Y}\x22,\x0a]\x0ares\
trict_to = [\x0a   \
 \x22stu\x22,\x0a    \x22nae\
\x22,\x0a]\x0asingle_chec\
k_only = false\x0a\x0a\
[spectrometers.n\
eo400]\x0amanufactu\
rer = \x22bruker\x22\x0ad\
isplay_name = \x22R\
outine NMR (300 \
&& 400 MHz)\x22\x0amea\
surement_pattern\
 = '<group!>\x5c_*<\
user_name>?\x5c_*<u\
ser!>\x5c_*<user2!>\
?\x5c_*<sample_id!>\
'\x0adate_entry = \x22\
dd MMM yyyy\x22\x0ache\
ck_paths = [\x0a   \
 \x22neo400/av1/neo\
400a_{date:%b%d-\
%Y}\x22,\x0a    \x22neo40\
0/av1/neo400b_{d\
ate:%b%d-%Y}\x22,\x0a \
   \x22neo400/av1/n\
eo400c_{date:%b%\
d-%Y}\x22,\x0a]\x0aarchiv\
es = [\x0a    \x22neo4\
00/av1/{date:%y}\
-neo400a_{date:%\
Y}/{date:%b%d-%Y\
}\x22,\x0a    \x22neo400/\
av1/{date:%y}-ne\
o400b_{date:%Y}/\
{date:%b%d-%Y}\x22,\
\x0a    \x22neo400/av1\
/{date:%y}-neo40\
0c_{date:%Y}/{da\
te:%b%d-%Y}\x22,\x0a]\x0a\
include = [ \x22av3\
00\x22 ]\x0asingle_che\
ck_only = false\x0a\
\x0a[spectrometers.\
hf]\x0amanufacturer\
 = \x22agilent\x22\x0adis\
play_name = \x22Hig\
h-field spectrom\
eters (500 && 60\
0 MHz)\x22\x0asample_p\
attern = '<user!\
><user2!>?<sampl\
e_id!>'\x0ameasurem\
ent_pattern = '<\
user!><user2!>?<\
sample_id!>_(\x5cd{\
6})_<temperature\
>k_<experiment>_\
<measurement_no>\
\x5c.fid'\x0adate_entr\
y = \x22yyyy\x22\x0acheck\
_paths = [\x0a    \x22\
500-600er/{group\
_name}/{date:%Y}\
\x22,\x0a]\x0aarchives = \
[\x0a    \x22archiv/50\
0-600er/{group_n\
ame}/{date:%Y}\x22,\
\x0a]\x0asingle_check_\
only = true\x0a\
"

qt_resource_name = b"\
\x00\x0b\
\x0fq\x7f\xbc\
\x00c\
\x00o\x00n\x00f\x00i\x00g\x00.\x00t\x00o\x00m\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x9e\xbb\xb7\x5c\xc1\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
