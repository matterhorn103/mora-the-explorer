# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x17b\
#\
 This file confi\
gures mora_the_e\
xplorer's *defau\
lt* internal set\
tings and should\
 not be\x0a# change\
d by anyone othe\
r than the NMR d\
epartment.\x0a\x0a# If\
 you are looking\
 for your user c\
onfiguration, it\
 is stored in th\
e user's config.\
toml file, at:\x0a#\
 Windows:  %USER\
PROFILE%\x5cAppData\
\x5cRoaming\x5cmora_th\
e_explorer\x5cconfi\
g.toml\x0a# macOS: \
   ~/Library/App\
lication Support\
/mora_the_explor\
er/config.toml\x0a#\
 Linux:    $XDG_\
CONFIG_HOME/mora\
_the_explorer or\
 ~/.config/mora_\
the_explorer/con\
fig.toml\x0a\x0a# Valu\
es specified in \
the user config.\
toml take preced\
ence over those \
specified here.\x0a\
\x0a# Before bundli\
ng the app with \
pyinstaller or c\
ompiling it with\
 pyside6-deploy,\
\x0a# the config fi\
le must be trans\
piled to a QReso\
urce, which is d\
one by running:\x0a\
# `uv run pyside\
6-rcc ./src/mora\
_the_explorer/re\
sources.qrc -o .\
/src/mora_the_ex\
plorer/resources\
.py`\x0a\x0a[options]\x0a\
user = \x22mjm\x22\x0ause\
r_name = \x22\x22\x0agrou\
p = \x22gil\x22\x0aspec =\
 \x22neo400\x22\x0arepeat\
_switch = false\x0a\
repeat_delay = 5\
\x0a\x0a[options.namin\
g]\x0agroup = false\
\x0auser = true\x0asol\
vent = false\x0afre\
quency = false\x0ae\
xperiment = true\
\x0aoriginal = fals\
e\x0a\x0a\x0a[appearance]\
\x0astart_button_co\
lour = \x22#b88cce\x22\
\x0a\x0a\x0a[paths]\x0a# Pat\
hs to the server\
, different by O\
S\x0a# Mount point \
probably needs t\
o be changed by \
the user on macO\
S and Linux\x0awind\
ows = \x22//samba.p\
ublic.os.wwu.de/\
usershare/projec\
ts/q_nmr-oc/nmr\x22\
\x0adarwin = \x22/Volu\
mes/usershare/pr\
ojects/q_nmr-oc/\
nmr\x22  # darwin =\
 macOS\x0alinux = \x22\
~/usershare/proj\
ects/q_nmr-oc/nm\
r\x22\x0aupdate = \x22mor\
a_the_explorer\x22 \
 # Where to chec\
k for app update\
s, relative to t\
he server\x0asave =\
 \x22~/nmr\x22  # The \
location spectra\
 should be copie\
d to\x0a\x0a\x0a[admin]\x0au\
ser_name_is_admi\
n_only = true\x0apa\
ttern_separator \
= '[\x5cs_-]'\x0aversi\
on = \x222.0.0b4\x22\x0ae\
mail = \x22milner@u\
ni-muenster.de\x22\x0a\
changelog = \x22\x22\x22\x0a\
- Update for mov\
e to new server\x0a\
- Big rewrite, c\
odebase is now m\
uch more structu\
red and maintain\
able\x0a- Inclusion\
 of experiment i\
n folder name is\
 now optional\x0a- \
Solvent and freq\
uency metadata a\
vailable on all \
spectrometers\x0a- \
Option to includ\
e the original f\
older name\x0a- But\
tons to select p\
aths using the s\
ystem file explo\
rer\x0a- Field to s\
pecify the serve\
r address from t\
he GUI (useful o\
n macOS and Linu\
x)\x0a- CLI and API\
 work entirely i\
ndependently of \
a GUI\x0a\x22\x22\x22\x0a\x0a\x0a[gro\
ups]\x0a# Available\
 groups, listed \
in the style `gr\
oup = group_name\
`\x0a# `group` is t\
he standard init\
ialism used for \
each group's exp\
eriments and dat\
a\x0a# institute-wi\
de and is used i\
n the search for\
 Bruker spectra \
(as it must be i\
ncluded in\x0a# the\
 measurement tit\
le)\x0a# `group` is\
 the full name, \
used for folders\
 of the group e.\
g. for the 500-6\
00er\x0afer = \x22fern\
andez\x22\x0agar = \x22ga\
rcia\x22\x0agil = \x22gil\
mour\x22\x0aglo = \x22glo\
rius\x22\x0ahei = \x22hei\
n\x22\x0anae = \x22naesbo\
rg\x22\x0arav = \x22ravoo\
\x22\x0astu = \x22studer\x22\
\x0a\x0a[groups.other]\
\x0a# Groups that s\
hould be put in \
a separate overf\
low list called \
\x22Other\x22 in the a\
pp\x0aac = \x22ac\x22\x0abio\
chemie = \x22bioche\
mie\x22\x0aextern = \x22e\
xtern\x22\x0aipc = \x22ip\
c\x22\x0akb = \x22kb\x22\x0amee\
t = \x22meet\x22\x0anuk =\
 \x22nuk\x22\x0apharmazie\
 = \x22pharmazie\x22\x0a\x0a\
\x0a[spectrometers]\
\x0a# Provide the f\
ollowing informa\
tion for each sp\
ectrometer categ\
ory:\x0a#   manufac\
turer: the manuf\
acturer of the s\
pectrometer(s)\x0a#\
   display_name:\
 the text shown \
next to the butt\
on in the user i\
nterface\x0a#      \
 (note that some\
 characters need\
 escaping, e.g. \
write && for &)\x0a\
#   measurement_\
pattern: the exp\
ected fields in \
the measurement \
title\x0a#   date_e\
ntry: whether th\
e user selects t\
he full date \x22dd\
 MMM yyyy\x22 or ju\
st year \x22yyyy\x22\x0a#\
   check_paths: \
the paths that s\
hould be searche\
d for new spectr\
a\x0a#   archives: \
if spectra from \
previous years c\
an't be found un\
der check_paths,\
 the\x0a#       arc\
hive folders are\
 checked in addi\
tion\x0a#   include\
: other spectrom\
eters which shou\
ld be searched a\
t the same time\x0a\
#   restrict_to:\
 the list of gro\
ups that should \
be able to see t\
he spectrometer \
- if\x0a#       thi\
s key is not use\
d, the spectrome\
ter will be visi\
ble to all\x0a#   a\
dmin_only: wheth\
er the spectrome\
ter should only \
be chooseable in\
 admin mode\x0a#   \
allow_solvent: w\
hether to enable\
 the folder nami\
ng option to inc\
lude the solvent\
\x0a#   single_chec\
k_only: whether \
users may use mu\
ltiday and repea\
t checks for thi\
s spec\x0a#\x0a# Possi\
ble variable fie\
lds in `check_pa\
ths` and `archiv\
es` are:\x0a# - <gr\
oup>         (th\
e chosen group's\
 ID)\x0a# - <group_\
name>    (the ch\
osen group's nam\
e)\x0a# - any strft\
ime formatting s\
tring, with % ch\
aracters, enclos\
ed in {}\x0a#   - f\
or the format co\
des see https://\
docs.python.org/\
3/library/dateti\
me.html#strftime\
-strptime-behavi\
or\x0a\x0a[spectromete\
rs.archiv]\x0amanuf\
acturer = \x22bruke\
r\x22\x0adisplay_name \
= \x22Pre-2020 arch\
ive (Bruker)\x22\x0ame\
asurement_patter\
n = '<group!>\x5c_*\
<user_name>?\x5c_*<\
user!>\x5c_*<sample\
_id>'\x0adate_entry\
 = \x22dd MMM yyyy\x22\
\x0acheck_paths = [\
\x0a    \x22archiv/dpx\
300/{%y}-dpx300_\
{%Y}/{%b%d-%Y}\x22,\
\x0a    \x22archiv/av3\
00/{%y}-av300_{%\
Y}/{%b%d-%Y}\x22,\x0a \
   \x22archiv/av400\
/{%y}-av400_{%Y}\
/{%b%d-%Y}\x22,\x0a   \
 \x22archiv/neo400a\
/{%y}-neo400a_{%\
Y}/neo400a_{%b%d\
-%Y}\x22,\x0a    \x22arch\
iv/neo400/{%y}-n\
eo400b_{%Y}/neo4\
00a_{%b%d-%Y}\x22,\x0a\
    \x22archiv/neo4\
00c/{%y}-neo400c\
_{%Y}/neo400c_{%\
b%d-%Y}\x22,\x0a]\x0aadmi\
n_only = true\x0asi\
ngle_check_only \
= false\x0a\x0a[spectr\
ometers.av300]\x0am\
anufacturer = \x22b\
ruker\x22\x0adisplay_n\
ame = \x22Studer gr\
oup NMR only (30\
0 MHz)\x22\x0ameasurem\
ent_pattern = '<\
group!>\x5c_*<user_\
name>?\x5c_*<user!>\
\x5c_*<sample_id>'\x0a\
date_entry = \x22dd\
 MMM yyyy\x22\x0acheck\
_paths = [\x0a    \x22\
av300/av1/{%b%d-\
%Y}\x22,\x0a]\x0aarchives\
 = [\x0a    \x22av300/\
av1/{%y}-av300_{\
%Y}/{%b%d-%Y}\x22,\x0a\
]\x0arestrict_to = \
[\x0a    \x22stu\x22,\x0a   \
 \x22nae\x22,\x0a]\x0asingle\
_check_only = fa\
lse\x0a\x0a[spectromet\
ers.neo400]\x0amanu\
facturer = \x22bruk\
er\x22\x0adisplay_name\
 = \x22Routine NMR \
(300 && 400 MHz)\
\x22\x0ameasurement_pa\
ttern = '<group!\
>\x5c_*<user_name>?\
\x5c_*<user!>\x5c_*<sa\
mple_id>'\x0adate_e\
ntry = \x22dd MMM y\
yyy\x22\x0acheck_paths\
 = [\x0a    \x22neo400\
/av1/neo400a_{%b\
%d-%Y}\x22,\x0a    \x22ne\
o400/av1/neo400b\
_{%b%d-%Y}\x22,\x0a   \
 \x22neo400/av1/neo\
400c_{%b%d-%Y}\x22,\
\x0a]\x0aarchives = [\x0a\
    \x22neo400/av1/\
{%y}-neo400a_{%Y\
}/{%b%d-%Y}\x22,\x0a  \
  \x22neo400/av1/{%\
y}-neo400b_{%Y}/\
{%b%d-%Y}\x22,\x0a    \
\x22neo400/av1/{%y}\
-neo400c_{%Y}/{%\
b%d-%Y}\x22,\x0a]\x0aincl\
ude = [ \x22av300\x22 \
]\x0asingle_check_o\
nly = false\x0a\x0a[sp\
ectrometers.hf]\x0a\
manufacturer = \x22\
agilent\x22\x0adisplay\
_name = \x22High-fi\
eld spectrometer\
s (500 && 600 MH\
z)\x22\x0ameasurement_\
pattern = '<user\
!><sample_id>'\x0ad\
ate_entry = \x22yyy\
y\x22\x0acheck_paths =\
 [\x0a    \x22500-600e\
r/<group_name>/{\
%Y}\x22,\x0a]\x0asingle_c\
heck_only = true\
\x0a\
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
\x00\x00\x01\x9d\xd1\x92\x99\x91\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
