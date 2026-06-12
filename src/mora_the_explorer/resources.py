# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x1c\x0d\
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
.py`\x0a\x0aversion = \
1\x0a\x0a[options]\x0ause\
r = \x22mjm\x22\x0agroup \
= \x22gil\x22\x0aspec = \x22\
neo400\x22\x0arepeat_s\
witch = false\x0are\
peat_delay = 5\x0a\x0a\
[options.naming]\
\x0asample_format =\
 \x22{user}-{user2}\
-{sample_id}\x22\x0ame\
asurement_format\
.bruker = \x22{user\
}-{user2}-{sampl\
e_id}_{instrumen\
t}_{submission_t\
ime:%d%m%y}_{tem\
perature}k_{expe\
riment}_{measure\
ment_no}\x22\x0ameasur\
ement_format.agi\
lent = \x22{user}-{\
user2}-{sample_i\
d}_{instrument}_\
{completion_time\
:%d%m%y}_{temper\
ature}k_{experim\
ent}_{measuremen\
t_no}\x22\x0a\x0a\x0a[appear\
ance]\x0astart_butt\
on_colour = \x22#b8\
8cce\x22\x0a\x0a\x0a[paths]\x0a\
# Paths to the s\
erver, different\
 by OS\x0a# Mount p\
oint probably ne\
eds to be change\
d by the user on\
 macOS and Linux\
\x0awindows = \x22//sa\
mba.public.os.ww\
u.de/usershare/p\
rojects/q_nmr-oc\
/nmr\x22\x0adarwin = \x22\
/Volumes/usersha\
re/projects/q_nm\
r-oc/nmr\x22  # dar\
win = macOS\x0alinu\
x = \x22~/usershare\
/projects/q_nmr-\
oc/nmr\x22\x0asrc = \x22m\
ora_the_explorer\
/src/mora-the-ex\
plorer\x22  # The r\
oot directory of\
 the source code\
, relative to th\
e server, refere\
nced when checki\
ng for updates\x0as\
ave = \x22\x22  # The \
location spectra\
 should be copie\
d to - if empty,\
 the user is ask\
ed on launch\x0a\x0a\x0a[\
admin]\x0apattern_s\
eparator = '[\x5cs_\
-]' # Note the s\
ingle quotes! (=\
 literal string)\
\x0aversion = \x222.0.\
0b7\x22\x0aemail = \x22mi\
lner@uni-muenste\
r.de\x22\x0achangelog \
= \x22\x22\x22\x0a- Update f\
or move to new s\
erver\x0a- Big rewr\
ite, codebase is\
 now much more s\
tructured and ma\
intainable\x0a- The\
 search can be s\
et to always che\
ck the current d\
ate which change\
s accordingly\x0a- \
Spectra always s\
orted into subfo\
lders by sample \
(like Agilent sp\
ectra)\x0a- Paths a\
re selected usin\
g the system fil\
e explorer\x0a- Abi\
lity to specify \
the server addre\
ss from the GUI \
(useful on macOS\
 and Linux)\x0a- So\
lvent, instrumen\
t, experiment, t\
emperature metad\
ata extracted on\
 all spectromete\
rs\x0a- Metadata ar\
e saved to the m\
easurement folde\
r in mora.toml\x0a-\
 CLI and Python \
API work entirel\
y independently \
of a GUI\x0a\x22\x22\x22\x0a\x0a\x0a[\
groups]\x0a# Availa\
ble groups, list\
ed in the style \
`group = group_n\
ame`\x0a# `group` i\
s the standard i\
nitialism used f\
or each group's \
experiments and \
data\x0a# institute\
-wide and is use\
d in the search \
for Bruker spect\
ra (as it must b\
e included in\x0a# \
the measurement \
title)\x0a# `group`\
 is the full nam\
e, used for fold\
ers of the group\
 e.g. for the 50\
0-600er\x0afer = \x22f\
ernandez\x22\x0agar = \
\x22garcia\x22\x0agil = \x22\
gilmour\x22\x0aglo = \x22\
glorius\x22\x0ahei = \x22\
hein\x22\x0anae = \x22nae\
sborg\x22\x0arav = \x22ra\
voo\x22\x0astu = \x22stud\
er\x22\x0a\x0a[groups.oth\
er]\x0a# Groups tha\
t should be put \
in a separate ov\
erflow list call\
ed \x22Other\x22 in th\
e app\x0aac = \x22ac\x22\x0a\
biochemie = \x22bio\
chemie\x22\x0aextern =\
 \x22extern\x22\x0aipc = \
\x22ipc\x22\x0akb = \x22kb\x22\x0a\
meet = \x22meet\x22\x0anu\
k = \x22nuk\x22\x0aocf = \
\x22ocf\x22\x0apharmazie \
= \x22pharmazie\x22\x0a\x0a\x0a\
[spectrometers]\x0a\
# Provide the fo\
llowing informat\
ion for each spe\
ctrometer catego\
ry:\x0a#   manufact\
urer: the manufa\
cturer of the sp\
ectrometer(s)\x0a# \
  display_name: \
the text shown n\
ext to the butto\
n in the user in\
terface\x0a#       \
(note that some \
characters need \
escaping, e.g. w\
rite && for &)\x0a#\
   measurement_p\
attern: the expe\
cted fields in t\
he measurement t\
itle\x0a#   date_en\
try: whether the\
 user selects th\
e full date \x22dd \
MMM yyyy\x22 or jus\
t year \x22yyyy\x22\x0a# \
  check_paths: t\
he paths that sh\
ould be searched\
 for new spectra\
\x0a#   archives: i\
f spectra from p\
revious years ca\
n't be found und\
er check_paths, \
the\x0a#       arch\
ive folders are \
checked in addit\
ion\x0a#   include:\
 other spectrome\
ters which shoul\
d be searched at\
 the same time\x0a#\
   restrict_to: \
the list of grou\
ps that should b\
e able to see th\
e spectrometer -\
 if\x0a#       this\
 key is not used\
, the spectromet\
er will be visib\
le to all\x0a#   ad\
min_only: whethe\
r the spectromet\
er should only b\
e chooseable in \
admin mode\x0a#   a\
llow_solvent: wh\
ether to enable \
the folder namin\
g option to incl\
ude the solvent\x0a\
#   single_check\
_only: whether u\
sers may use mul\
tiday and repeat\
 checks for this\
 spec\x0a#\x0a# Variab\
les can be inter\
polated into the\
 entries in `che\
ck_paths` and `a\
rchives`\x0a# by wr\
apping them in c\
urly brackets. T\
he following var\
iables can be us\
ed:\x0a# - group   \
      (the chose\
n group's ID)\x0a# \
- group_name    \
(the chosen grou\
p's name)\x0a# - da\
te\x0a#\x0a# For `date\
`, it may be des\
irable to format\
 it using e.g. `\
{date:%Y}` to ge\
t `2026`\x0a# For t\
he format codes \
see https://docs\
.python.org/3/li\
brary/datetime.h\
tml#strftime-str\
ptime-behavior\x0a\x0a\
# Note that in T\
OML, single quot\
es can be used f\
or a literal str\
ing to avoid\x0a# h\
aving to use bac\
kslash escapes, \
which is very us\
eful for regex p\
atterns\x0a\x0a[spectr\
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
\x00\x00\x01\x9e\xbb8\xe6s\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
