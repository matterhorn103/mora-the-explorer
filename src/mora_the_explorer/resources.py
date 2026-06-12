# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x10\xef\
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
\x22//wwu/ddfs/Clou\
d/wwu1/q_nmr-oc/\
nmr\x22\x0adarwin = \x22/\
Volumes/usershar\
e/projects/q_nmr\
-oc/nmr\x22  # darw\
in = macOS\x0alinux\
 = \x22~/usershare/\
projects/q_nmr-o\
c/nmr\x22\x0asrc = \x22mo\
ra_the_explorer/\
src/mora-the-exp\
lorer\x22\x0asave = \x22\x22\
\x0a\x0a\x0a[admin]\x0apatte\
rn_separator = '\
[\x5cs_-]' # Note t\
he single quotes\
! (= literal str\
ing)\x0aversion = \x22\
2.0.0\x22\x0aemail = \x22\
milner@uni-muens\
ter.de\x22\x0achangelo\
g = \x22\x22\x22\x0a- Update\
d for move to ne\
w server\x0a- Big r\
ewrite, codebase\
 is now much mor\
e structured and\
 maintainable\x0a- \
Refreshed the UI\
\x0a- Added an opti\
on to check the \
current date (\x22t\
oday\x22), which up\
dates accordingl\
y\x0a- Spectra are \
now always sorte\
d into subfolder\
s by sample (lik\
e Agilent spectr\
a)\x0a- Locations n\
ow selected usin\
g the system fil\
e explorer\x0a- Add\
ed the ability t\
o set the server\
 address from th\
e GUI (useful on\
 macOS and Linux\
)\x0a- Various meta\
data (inc. solve\
nt, instrument, \
temperature) are\
 now extracted o\
n all spectromet\
ers\x0a- Extracted \
metadata are now\
 saved to the me\
asurement folder\
 in mora.toml\x0a- \
CLI and Python A\
PI now work enti\
rely independent\
ly of a GUI\x0a\x22\x22\x22\x0a\
\x0a\x0a[groups]\x0afer =\
 \x22fernandez\x22\x0agar\
 = \x22garcia\x22\x0agil \
= \x22gilmour\x22\x0aglo \
= \x22glorius\x22\x0ahei \
= \x22hein\x22\x0anae = \x22\
naesborg\x22\x0arav = \
\x22ravoo\x22\x0astu = \x22s\
tuder\x22\x0a\x0a[groups.\
other]\x0aac = \x22ac\x22\
\x0abiochemie = \x22bi\
ochemie\x22\x0aextern \
= \x22extern\x22\x0aipc =\
 \x22ipc\x22\x0akb = \x22kb\x22\
\x0ameet = \x22meet\x22\x0an\
uk = \x22nuk\x22\x0aocf =\
 \x22ocf\x22\x0apharmazie\
 = \x22pharmazie\x22\x0a\x0a\
\x0a[spectrometers]\
\x0a\x0a[spectrometers\
.archiv]\x0amanufac\
turer = \x22bruker\x22\
\x0adisplay_name = \
\x22Pre-2020 archiv\
e (Bruker)\x22\x0ameas\
urement_pattern \
= '<group!>\x5c_*<u\
ser_name>?\x5c_*<us\
er!>\x5c_*<user2!>?\
\x5c_*<sample_id!>'\
 # Note the sing\
le quotes! (= li\
teral string)\x0ada\
te_entry = \x22dd M\
MM yyyy\x22\x0acheck_p\
aths = [\x0a    \x22ar\
chiv/dpx300/{dat\
e:%y}-dpx300_{da\
te:%Y}/dpx300_{d\
ate:%b%d-%Y}\x22,\x0a \
   \x22archiv/av300\
/{date:%y}-av300\
_{date:%Y}/av300\
_{date:%b%d-%Y}\x22\
,\x0a    \x22archiv/av\
400/{date:%y}-av\
400_{date:%Y}/av\
400_{date:%b%d-%\
Y}\x22,\x0a    \x22archiv\
/neo400a/{date:%\
y}-neo400a_{date\
:%Y}/neo400a_{da\
te:%b%d-%Y}\x22,\x0a  \
  \x22archiv/neo400\
b/{date:%y}-neo4\
00b_{date:%Y}/ne\
o400b_{date:%b%d\
-%Y}\x22,\x0a    \x22arch\
iv/neo400c/{date\
:%y}-neo400c_{da\
te:%Y}/neo400c_{\
date:%b%d-%Y}\x22,\x0a\
]\x0aadmin_only = t\
rue\x0asingle_check\
_only = false\x0a\x0a[\
spectrometers.av\
300]\x0amanufacture\
r = \x22bruker\x22\x0adis\
play_name = \x22Stu\
der group NMR on\
ly (300 MHz)\x22\x0ame\
asurement_patter\
n = '<group!>\x5c_*\
<user!>\x5c_*<user2\
!>?\x5c_*<sample_id\
!>'\x0adate_entry =\
 \x22dd MMM yyyy\x22\x0ac\
heck_paths = [\x0a \
   \x22av300/av1/av\
300_{date:%b%d-%\
Y}\x22,\x0a]\x0aarchives \
= [\x0a    \x22av300/a\
v1/{date:%y}-av3\
00_{date:%Y}/av3\
00_{date:%b%d-%Y\
}\x22,\x0a]\x0arestrict_t\
o = [\x0a    \x22stu\x22,\
\x0a    \x22nae\x22,\x0a]\x0asi\
ngle_check_only \
= false\x0a\x0a[spectr\
ometers.neo400]\x0a\
manufacturer = \x22\
bruker\x22\x0adisplay_\
name = \x22Routine \
NMR (300 && 400 \
MHz)\x22\x0ameasuremen\
t_pattern = '<gr\
oup!>\x5c_*<user!>\x5c\
_*<user2!>?\x5c_*<s\
ample_id!>'\x0adate\
_entry = \x22dd MMM\
 yyyy\x22\x0acheck_pat\
hs = [\x0a    \x22neo4\
00/av1/neo400a_{\
date:%b%d-%Y}\x22,\x0a\
    \x22neo400/av1/\
neo400b_{date:%b\
%d-%Y}\x22,\x0a    \x22ne\
o400/av1/neo400c\
_{date:%b%d-%Y}\x22\
,\x0a]\x0aarchives = [\
\x0a    \x22neo400/av1\
/{date:%y}-neo40\
0a_{date:%Y}/neo\
400a_{date:%b%d-\
%Y}\x22,\x0a    \x22neo40\
0/av1/{date:%y}-\
neo400b_{date:%Y\
}/neo400b_{date:\
%b%d-%Y}\x22,\x0a    \x22\
neo400/av1/{date\
:%y}-neo400c_{da\
te:%Y}/neo400c_{\
date:%b%d-%Y}\x22,\x0a\
]\x0ainclude = [ \x22a\
v300\x22 ]\x0asingle_c\
heck_only = fals\
e\x0a\x0a[spectrometer\
s.hf]\x0amanufactur\
er = \x22agilent\x22\x0ad\
isplay_name = \x22H\
igh-field spectr\
ometers (500 && \
600 MHz)\x22\x0asample\
_pattern = '<use\
r!><user2!>?<sam\
ple_id!>'\x0ameasur\
ement_pattern = \
'<user!><user2!>\
?<sample_id!>_(\x5c\
d{6})_<temperatu\
re>k_<experiment\
>_<measurement_n\
o>\x5c.fid'\x0adate_en\
try = \x22yyyy\x22\x0ache\
ck_paths = [\x0a   \
 \x22500-600er/{gro\
up_name}/{date:%\
Y}\x22,\x0a]\x0aarchives \
= [\x0a    \x22archiv/\
500-600er/{group\
_name}/{date:%Y}\
\x22,\x0a]\x0asingle_chec\
k_only = true\x0a\
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
\x00\x00\x01\x9e\xbc\x09\x06{\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
