# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x11\x1d\
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
2.0.0\x22\x0achangelog\
 = \x22\x22\x22\x0a- Updated\
 for move to new\
 server\x0a- Big re\
write, codebase \
is now much more\
 structured and \
maintainable\x0a- R\
efreshed the UI\x0a\
- Added an optio\
n to check the c\
urrent date (\x22to\
day\x22), which upd\
ates accordingly\
\x0a- Spectra are n\
ow always sorted\
 into subfolders\
 by sample (like\
 Agilent spectra\
)\x0a- Locations no\
w selected using\
 the system file\
 explorer\x0a- Adde\
d the ability to\
 set the server \
address from the\
 GUI (useful on \
macOS and Linux)\
\x0a- Various metad\
ata (inc. solven\
t, instrument, t\
emperature) are \
now extracted on\
 all spectromete\
rs\x0a- Extracted m\
etadata are now \
saved to the mea\
surement folder \
in mora.toml\x0a- C\
LI and Python AP\
I now work entir\
ely independentl\
y of a GUI\x0a\x22\x22\x22\x0as\
upport_email = \x22\
milner@uni-muens\
ter.de\x22\x0asupport_\
cc = \x22klaube@uni\
-muenster.de\x22\x0a\x0a\x0a\
[groups]\x0afer = \x22\
fernandez\x22\x0agar =\
 \x22garcia\x22\x0agil = \
\x22gilmour\x22\x0aglo = \
\x22glorius\x22\x0ahei = \
\x22hein\x22\x0anae = \x22na\
esborg\x22\x0arav = \x22r\
avoo\x22\x0astu = \x22stu\
der\x22\x0a\x0a[groups.ot\
her]\x0aac = \x22ac\x22\x0ab\
iochemie = \x22bioc\
hemie\x22\x0aextern = \
\x22extern\x22\x0aipc = \x22\
ipc\x22\x0akb = \x22kb\x22\x0am\
eet = \x22meet\x22\x0anuk\
 = \x22nuk\x22\x0aocf = \x22\
ocf\x22\x0apharmazie =\
 \x22pharmazie\x22\x0a\x0a\x0a[\
spectrometers]\x0a\x0a\
[spectrometers.a\
rchiv]\x0amanufactu\
rer = \x22bruker\x22\x0ad\
isplay_name = \x22P\
re-2020 archive \
(Bruker)\x22\x0ameasur\
ement_pattern = \
'<group!>\x5c_*<use\
r_name>?\x5c_*<user\
!>\x5c_*<user2!>?\x5c_\
*<sample_id!>' #\
 Note the single\
 quotes! (= lite\
ral string)\x0adate\
_entry = \x22dd MMM\
 yyyy\x22\x0acheck_pat\
hs = [\x0a    \x22arch\
iv/dpx300/{date:\
%y}-dpx300_{date\
:%Y}/dpx300_{dat\
e:%b%d-%Y}\x22,\x0a   \
 \x22archiv/av300/{\
date:%y}-av300_{\
date:%Y}/av300_{\
date:%b%d-%Y}\x22,\x0a\
    \x22archiv/av40\
0/{date:%y}-av40\
0_{date:%Y}/av40\
0_{date:%b%d-%Y}\
\x22,\x0a    \x22archiv/n\
eo400a/{date:%y}\
-neo400a_{date:%\
Y}/neo400a_{date\
:%b%d-%Y}\x22,\x0a    \
\x22archiv/neo400b/\
{date:%y}-neo400\
b_{date:%Y}/neo4\
00b_{date:%b%d-%\
Y}\x22,\x0a    \x22archiv\
/neo400c/{date:%\
y}-neo400c_{date\
:%Y}/neo400c_{da\
te:%b%d-%Y}\x22,\x0a]\x0a\
admin_only = tru\
e\x0asingle_check_o\
nly = false\x0a\x0a[sp\
ectrometers.av30\
0]\x0amanufacturer \
= \x22bruker\x22\x0adispl\
ay_name = \x22Stude\
r group NMR only\
 (300 MHz)\x22\x0ameas\
urement_pattern \
= '<group!>\x5c_*<u\
ser!>\x5c_*<user2!>\
?\x5c_*<sample_id!>\
'\x0adate_entry = \x22\
dd MMM yyyy\x22\x0ache\
ck_paths = [\x0a   \
 \x22av300/av1/av30\
0_{date:%b%d-%Y}\
\x22,\x0a]\x0aarchives = \
[\x0a    \x22av300/av1\
/{date:%y}-av300\
_{date:%Y}/av300\
_{date:%b%d-%Y}\x22\
,\x0a]\x0arestrict_to \
= [\x0a    \x22stu\x22,\x0a \
   \x22nae\x22,\x0a]\x0asing\
le_check_only = \
false\x0a\x0a[spectrom\
eters.neo400]\x0ama\
nufacturer = \x22br\
uker\x22\x0adisplay_na\
me = \x22Routine NM\
R (300 && 400 MH\
z)\x22\x0ameasurement_\
pattern = '<grou\
p!>\x5c_*<user!>\x5c_*\
<user2!>?\x5c_*<sam\
ple_id!>'\x0adate_e\
ntry = \x22dd MMM y\
yyy\x22\x0acheck_paths\
 = [\x0a    \x22neo400\
/av1/neo400a_{da\
te:%b%d-%Y}\x22,\x0a  \
  \x22neo400/av1/ne\
o400b_{date:%b%d\
-%Y}\x22,\x0a    \x22neo4\
00/av1/neo400c_{\
date:%b%d-%Y}\x22,\x0a\
]\x0aarchives = [\x0a \
   \x22neo400/av1/{\
date:%y}-neo400a\
_{date:%Y}/neo40\
0a_{date:%b%d-%Y\
}\x22,\x0a    \x22neo400/\
av1/{date:%y}-ne\
o400b_{date:%Y}/\
neo400b_{date:%b\
%d-%Y}\x22,\x0a    \x22ne\
o400/av1/{date:%\
y}-neo400c_{date\
:%Y}/neo400c_{da\
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
\x00\x00\x01\x9e\xbc\x12\xc0\xa1\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
