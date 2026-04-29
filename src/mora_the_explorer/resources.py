# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x19\xa8\
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
\x0asort = 3  # How\
 to sort when sa\
ving; 0 = origin\
al sorting, 1 = \
measurement (Bru\
ker-style), 2 = \
sample & spec, 3\
 = sample (Agile\
nt-style) \x0a\x0a[opt\
ions.naming]\x0agro\
up = false\x0auser \
= true\x0asolvent =\
 false\x0ainstrumen\
t = false\x0afreque\
ncy = false\x0aexpe\
riment = true\x0aor\
iginal = false\x0a\x0a\
\x0a[appearance]\x0ast\
art_button_colou\
r = \x22#b88cce\x22\x0a\x0a\x0a\
[paths]\x0a# Paths \
to the server, d\
ifferent by OS\x0a#\
 Mount point pro\
bably needs to b\
e changed by the\
 user on macOS a\
nd Linux\x0awindows\
 = \x22//samba.publ\
ic.os.wwu.de/use\
rshare/projects/\
q_nmr-oc/nmr\x22\x0ada\
rwin = \x22/Volumes\
/usershare/proje\
cts/q_nmr-oc/nmr\
\x22  # darwin = ma\
cOS\x0alinux = \x22~/u\
sershare/project\
s/q_nmr-oc/nmr\x22\x0a\
update = \x22mora_t\
he_explorer\x22  # \
Where to check f\
or app updates, \
relative to the \
server\x0asave = \x22~\
/nmr\x22  # The loc\
ation spectra sh\
ould be copied t\
o\x0a\x0a\x0a[admin]\x0auser\
_name_is_admin_o\
nly = true\x0apatte\
rn_separator = '\
[\x5cs_-]'\x0aversion \
= \x222.0.0b5\x22\x0aemai\
l = \x22milner@uni-\
muenster.de\x22\x0acha\
ngelog = \x22\x22\x22\x0a- U\
pdate for move t\
o new server\x0a- B\
ig rewrite, code\
base is now much\
 more structured\
 and maintainabl\
e\x0a- The search c\
an be set to alw\
ays check the cu\
rrent date which\
 changes accordi\
ngly\x0a- Spectra c\
an be sorted int\
o subfolders (li\
ke Agilent spect\
ra) if desired, \
or not at all\x0a- \
Folder name is n\
ow entirely cust\
omizable\x0a- Previ\
ew of the curren\
t folder name st\
yle is shown\x0a- S\
olvent, instrume\
nt, experiment m\
etadata availabl\
e on all spectro\
meters\x0a- Option \
to include the o\
riginal folder n\
ame\x0a- Paths are \
selected using t\
he system file e\
xplorer\x0a- Abilit\
y to specify the\
 server address \
from the GUI (us\
eful on macOS an\
d Linux)\x0a- Metad\
ata are saved to\
 the measurement\
 folder in mora.\
toml\x0a- CLI and P\
ython API work e\
ntirely independ\
ently of a GUI\x0a\x22\
\x22\x22\x0a\x0a\x0a[groups]\x0a# \
Available groups\
, listed in the \
style `group = g\
roup_name`\x0a# `gr\
oup` is the stan\
dard initialism \
used for each gr\
oup's experiment\
s and data\x0a# ins\
titute-wide and \
is used in the s\
earch for Bruker\
 spectra (as it \
must be included\
 in\x0a# the measur\
ement title)\x0a# `\
group` is the fu\
ll name, used fo\
r folders of the\
 group e.g. for \
the 500-600er\x0afe\
r = \x22fernandez\x22\x0a\
gar = \x22garcia\x22\x0ag\
il = \x22gilmour\x22\x0ag\
lo = \x22glorius\x22\x0ah\
ei = \x22hein\x22\x0anae \
= \x22naesborg\x22\x0arav\
 = \x22ravoo\x22\x0astu =\
 \x22studer\x22\x0a\x0a[grou\
ps.other]\x0a# Grou\
ps that should b\
e put in a separ\
ate overflow lis\
t called \x22Other\x22\
 in the app\x0aac =\
 \x22ac\x22\x0abiochemie \
= \x22biochemie\x22\x0aex\
tern = \x22extern\x22\x0a\
ipc = \x22ipc\x22\x0akb =\
 \x22kb\x22\x0ameet = \x22me\
et\x22\x0anuk = \x22nuk\x22\x0a\
ocf = \x22ocf\x22\x0aphar\
mazie = \x22pharmaz\
ie\x22\x0a\x0a\x0a[spectrome\
ters]\x0a# Provide \
the following in\
formation for ea\
ch spectrometer \
category:\x0a#   ma\
nufacturer: the \
manufacturer of \
the spectrometer\
(s)\x0a#   display_\
name: the text s\
hown next to the\
 button in the u\
ser interface\x0a# \
      (note that\
 some characters\
 need escaping, \
e.g. write && fo\
r &)\x0a#   measure\
ment_pattern: th\
e expected field\
s in the measure\
ment title\x0a#   d\
ate_entry: wheth\
er the user sele\
cts the full dat\
e \x22dd MMM yyyy\x22 \
or just year \x22yy\
yy\x22\x0a#   check_pa\
ths: the paths t\
hat should be se\
arched for new s\
pectra\x0a#   archi\
ves: if spectra \
from previous ye\
ars can't be fou\
nd under check_p\
aths, the\x0a#     \
  archive folder\
s are checked in\
 addition\x0a#   in\
clude: other spe\
ctrometers which\
 should be searc\
hed at the same \
time\x0a#   restric\
t_to: the list o\
f groups that sh\
ould be able to \
see the spectrom\
eter - if\x0a#     \
  this key is no\
t used, the spec\
trometer will be\
 visible to all\x0a\
#   admin_only: \
whether the spec\
trometer should \
only be chooseab\
le in admin mode\
\x0a#   allow_solve\
nt: whether to e\
nable the folder\
 naming option t\
o include the so\
lvent\x0a#   single\
_check_only: whe\
ther users may u\
se multiday and \
repeat checks fo\
r this spec\x0a#\x0a# \
Possible variabl\
e fields in `che\
ck_paths` and `a\
rchives` are:\x0a# \
- <group>       \
  (the chosen gr\
oup's ID)\x0a# - <g\
roup_name>    (t\
he chosen group'\
s name)\x0a# - any \
strftime formatt\
ing string, with\
 % characters, e\
nclosed in {}\x0a# \
  - for the form\
at codes see htt\
ps://docs.python\
.org/3/library/d\
atetime.html#str\
ftime-strptime-b\
ehavior\x0a\x0a[spectr\
ometers.archiv]\x0a\
manufacturer = \x22\
bruker\x22\x0adisplay_\
name = \x22Pre-2020\
 archive (Bruker\
)\x22\x0ameasurement_p\
attern = '<group\
!>\x5c_*<user_name>\
?\x5c_*<user!>\x5c_*<s\
ample_id>'\x0adate_\
entry = \x22dd MMM \
yyyy\x22\x0acheck_path\
s = [\x0a    \x22archi\
v/dpx300/{%y}-dp\
x300_{%Y}/{%b%d-\
%Y}\x22,\x0a    \x22archi\
v/av300/{%y}-av3\
00_{%Y}/{%b%d-%Y\
}\x22,\x0a    \x22archiv/\
av400/{%y}-av400\
_{%Y}/{%b%d-%Y}\x22\
,\x0a    \x22archiv/ne\
o400a/{%y}-neo40\
0a_{%Y}/neo400a_\
{%b%d-%Y}\x22,\x0a    \
\x22archiv/neo400b/\
{%y}-neo400b_{%Y\
}/neo400b_{%b%d-\
%Y}\x22,\x0a    \x22archi\
v/neo400c/{%y}-n\
eo400c_{%Y}/neo4\
00c_{%b%d-%Y}\x22,\x0a\
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
<user_name>?\x5c_*<\
user!>\x5c_*<sample\
_id>'\x0adate_entry\
 = \x22dd MMM yyyy\x22\
\x0acheck_paths = [\
\x0a    \x22av300/av1/\
{%b%d-%Y}\x22,\x0a]\x0aar\
chives = [\x0a    \x22\
av300/av1/{%y}-a\
v300_{%Y}/{%b%d-\
%Y}\x22,\x0a]\x0arestrict\
_to = [\x0a    \x22stu\
\x22,\x0a    \x22nae\x22,\x0a]\x0a\
single_check_onl\
y = false\x0a\x0a[spec\
trometers.neo400\
]\x0amanufacturer =\
 \x22bruker\x22\x0adispla\
y_name = \x22Routin\
e NMR (300 && 40\
0 MHz)\x22\x0ameasurem\
ent_pattern = '<\
group!>\x5c_*<user_\
name>?\x5c_*<user!>\
\x5c_*<sample_id>'\x0a\
date_entry = \x22dd\
 MMM yyyy\x22\x0acheck\
_paths = [\x0a    \x22\
neo400/av1/neo40\
0a_{%b%d-%Y}\x22,\x0a \
   \x22neo400/av1/n\
eo400b_{%b%d-%Y}\
\x22,\x0a    \x22neo400/a\
v1/neo400c_{%b%d\
-%Y}\x22,\x0a]\x0aarchive\
s = [\x0a    \x22neo40\
0/av1/{%y}-neo40\
0a_{%Y}/{%b%d-%Y\
}\x22,\x0a    \x22neo400/\
av1/{%y}-neo400b\
_{%Y}/{%b%d-%Y}\x22\
,\x0a    \x22neo400/av\
1/{%y}-neo400c_{\
%Y}/{%b%d-%Y}\x22,\x0a\
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
r!><sample_id>'\x0a\
measurement_patt\
ern = '<user!><s\
ample_id>\x5c_(\x5cd{6\
})\x5c_(\x5cd{3}k)\x5c_(.\
+)_\x5cd\x5c.fid'\x0adate\
_entry = \x22yyyy\x22\x0a\
check_paths = [\x0a\
    \x22500-600er/<\
group_name>/{%Y}\
\x22,\x0a]\x0aarchives = \
[\x0a    \x22archiv/50\
0-600er/<group_n\
ame>/{%Y}\x22,\x0a]\x0asi\
ngle_check_only \
= true\x0a\
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
\x00\x00\x01\x9d\xd9\xe6\xe0\x1c\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
