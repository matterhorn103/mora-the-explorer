# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x1b|\
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
g]\x0asample_format\
 = \x22{user}-{samp\
le_id}\x22\x0ameasurem\
ent_format = \x22{u\
ser}-{sample_id}\
_{instrument}_{c\
ompletion_time:%\
d%m%y}_{temperat\
ure}k_{experimen\
t}_{measurement_\
no}\x22\x0a\x0a\x0a[appearan\
ce]\x0astart_button\
_colour = \x22#b88c\
ce\x22\x0a\x0a\x0a[paths]\x0a# \
Paths to the ser\
ver, different b\
y OS\x0a# Mount poi\
nt probably need\
s to be changed \
by the user on m\
acOS and Linux\x0aw\
indows = \x22//samb\
a.public.os.wwu.\
de/usershare/pro\
jects/q_nmr-oc/n\
mr\x22\x0adarwin = \x22/V\
olumes/usershare\
/projects/q_nmr-\
oc/nmr\x22  # darwi\
n = macOS\x0alinux \
= \x22~/usershare/p\
rojects/q_nmr-oc\
/nmr\x22\x0aupdate = \x22\
mora_the_explore\
r\x22  # Where to c\
heck for app upd\
ates, relative t\
o the server\x0asav\
e = \x22~/nmr\x22  # T\
he location spec\
tra should be co\
pied to\x0a\x0a\x0a[admin\
]\x0auser_name_is_a\
dmin_only = true\
\x0apattern_separat\
or = '[\x5cs_-]' # \
Note the single \
quotes! (= liter\
al string)\x0aversi\
on = \x222.0.0b5\x22\x0ae\
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
a can be sorted \
into subfolders \
(like Agilent sp\
ectra) if desire\
d, or not at all\
\x0a- Folder name i\
s now entirely c\
ustomizable\x0a- Pr\
eview of the cur\
rent folder name\
 style is shown\x0a\
- Solvent, instr\
ument, experimen\
t metadata avail\
able on all spec\
trometers\x0a- Opti\
on to include th\
e original folde\
r name\x0a- Paths a\
re selected usin\
g the system fil\
e explorer\x0a- Abi\
lity to specify \
the server addre\
ss from the GUI \
(useful on macOS\
 and Linux)\x0a- Me\
tadata are saved\
 to the measurem\
ent folder in mo\
ra.toml\x0a- CLI an\
d Python API wor\
k entirely indep\
endently of a GU\
I\x0a\x22\x22\x22\x0a\x0a\x0a[groups]\
\x0a# Available gro\
ups, listed in t\
he style `group \
= group_name`\x0a# \
`group` is the s\
tandard initiali\
sm used for each\
 group's experim\
ents and data\x0a# \
institute-wide a\
nd is used in th\
e search for Bru\
ker spectra (as \
it must be inclu\
ded in\x0a# the mea\
surement title)\x0a\
# `group` is the\
 full name, used\
 for folders of \
the group e.g. f\
or the 500-600er\
\x0afer = \x22fernande\
z\x22\x0agar = \x22garcia\
\x22\x0agil = \x22gilmour\
\x22\x0aglo = \x22glorius\
\x22\x0ahei = \x22hein\x22\x0an\
ae = \x22naesborg\x22\x0a\
rav = \x22ravoo\x22\x0ast\
u = \x22studer\x22\x0a\x0a[g\
roups.other]\x0a# G\
roups that shoul\
d be put in a se\
parate overflow \
list called \x22Oth\
er\x22 in the app\x0aa\
c = \x22ac\x22\x0abiochem\
ie = \x22biochemie\x22\
\x0aextern = \x22exter\
n\x22\x0aipc = \x22ipc\x22\x0ak\
b = \x22kb\x22\x0ameet = \
\x22meet\x22\x0anuk = \x22nu\
k\x22\x0aocf = \x22ocf\x22\x0ap\
harmazie = \x22phar\
mazie\x22\x0a\x0a\x0a[spectr\
ometers]\x0a# Provi\
de the following\
 information for\
 each spectromet\
er category:\x0a#  \
 manufacturer: t\
he manufacturer \
of the spectrome\
ter(s)\x0a#   displ\
ay_name: the tex\
t shown next to \
the button in th\
e user interface\
\x0a#       (note t\
hat some charact\
ers need escapin\
g, e.g. write &&\
 for &)\x0a#   meas\
urement_pattern:\
 the expected fi\
elds in the meas\
urement title\x0a# \
  date_entry: wh\
ether the user s\
elects the full \
date \x22dd MMM yyy\
y\x22 or just year \
\x22yyyy\x22\x0a#   check\
_paths: the path\
s that should be\
 searched for ne\
w spectra\x0a#   ar\
chives: if spect\
ra from previous\
 years can't be \
found under chec\
k_paths, the\x0a#  \
     archive fol\
ders are checked\
 in addition\x0a#  \
 include: other \
spectrometers wh\
ich should be se\
arched at the sa\
me time\x0a#   rest\
rict_to: the lis\
t of groups that\
 should be able \
to see the spect\
rometer - if\x0a#  \
     this key is\
 not used, the s\
pectrometer will\
 be visible to a\
ll\x0a#   admin_onl\
y: whether the s\
pectrometer shou\
ld only be choos\
eable in admin m\
ode\x0a#   allow_so\
lvent: whether t\
o enable the fol\
der naming optio\
n to include the\
 solvent\x0a#   sin\
gle_check_only: \
whether users ma\
y use multiday a\
nd repeat checks\
 for this spec\x0a#\
\x0a# Variables can\
 be interpolated\
 into the entrie\
s in `check_path\
s` and `archives\
`\x0a# by wrapping \
them in curly br\
ackets. The foll\
owing variables \
can be used:\x0a# -\
 group         (\
the chosen group\
's ID)\x0a# - group\
_name    (the ch\
osen group's nam\
e)\x0a# - date\x0a# \x0a#\
 For `date`, it \
may be desirable\
 to format it us\
ing e.g. `{date:\
%Y}` to get `202\
6`\x0a# For the for\
mat codes see ht\
tps://docs.pytho\
n.org/3/library/\
datetime.html#st\
rftime-strptime-\
behavior\x0a\x0a# Note\
 that in TOML, s\
ingle quotes can\
 be used for a l\
iteral string to\
 avoid\x0a# having \
to use backslash\
 escapes, which \
is very useful f\
or regex pattern\
s\x0a\x0a[spectrometer\
s.archiv]\x0amanufa\
cturer = \x22bruker\
\x22\x0adisplay_name =\
 \x22Pre-2020 archi\
ve (Bruker)\x22\x0amea\
surement_pattern\
 = '<group!>\x5c_*<\
user_name>?\x5c_*<u\
ser!>\x5c_*<sample_\
id>' # Note the \
single quotes! (\
= literal string\
)\x0adate_entry = \x22\
dd MMM yyyy\x22\x0ache\
ck_paths = [\x0a   \
 \x22archiv/dpx300/\
{date:%y}-dpx300\
_{date:%Y}/{date\
:%b%d-%Y}\x22,\x0a    \
\x22archiv/av300/{d\
ate:%y}-av300_{d\
ate:%Y}/{date:%b\
%d-%Y}\x22,\x0a    \x22ar\
chiv/av400/{date\
:%y}-av400_{date\
:%Y}/{date:%b%d-\
%Y}\x22,\x0a    \x22archi\
v/neo400a/{date:\
%y}-neo400a_{dat\
e:%Y}/neo400a_{d\
ate:%b%d-%Y}\x22,\x0a \
   \x22archiv/neo40\
0b/{date:%y}-neo\
400b_{date:%Y}/n\
eo400b_{date:%b%\
d-%Y}\x22,\x0a    \x22arc\
hiv/neo400c/{dat\
e:%y}-neo400c_{d\
ate:%Y}/neo400c_\
{date:%b%d-%Y}\x22,\
\x0a]\x0aadmin_only = \
true\x0asingle_chec\
k_only = false\x0a\x0a\
[spectrometers.a\
v300]\x0amanufactur\
er = \x22bruker\x22\x0adi\
splay_name = \x22St\
uder group NMR o\
nly (300 MHz)\x22\x0am\
easurement_patte\
rn = '<group!>\x5c_\
*<user_name>?\x5c_*\
<user!>\x5c_*<sampl\
e_id>'\x0adate_entr\
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
ser!>\x5c_*<sample_\
id>'\x0adate_entry \
= \x22dd MMM yyyy\x22\x0a\
check_paths = [\x0a\
    \x22neo400/av1/\
neo400a_{date:%b\
%d-%Y}\x22,\x0a    \x22ne\
o400/av1/neo400b\
_{date:%b%d-%Y}\x22\
,\x0a    \x22neo400/av\
1/neo400c_{date:\
%b%d-%Y}\x22,\x0a]\x0aarc\
hives = [\x0a    \x22n\
eo400/av1/{date:\
%y}-neo400a_{dat\
e:%Y}/{date:%b%d\
-%Y}\x22,\x0a    \x22neo4\
00/av1/{date:%y}\
-neo400b_{date:%\
Y}/{date:%b%d-%Y\
}\x22,\x0a    \x22neo400/\
av1/{date:%y}-ne\
o400c_{date:%Y}/\
{date:%b%d-%Y}\x22,\
\x0a]\x0ainclude = [ \x22\
av300\x22 ]\x0asingle_\
check_only = fal\
se\x0a\x0a[spectromete\
rs.hf]\x0amanufactu\
rer = \x22agilent\x22\x0a\
display_name = \x22\
High-field spect\
rometers (500 &&\
 600 MHz)\x22\x0asampl\
e_pattern = '<us\
er!><sample_id>'\
\x0ameasurement_pat\
tern = '<user!><\
sample_id>_(\x5cd{6\
})_<temperature>\
k_<experiment>_<\
measurement_no>\x5c\
.fid'\x0adate_entry\
 = \x22yyyy\x22\x0acheck_\
paths = [\x0a    \x225\
00-600er/{group_\
name}/{date:%Y}\x22\
,\x0a]\x0aarchives = [\
\x0a    \x22archiv/500\
-600er/{group_na\
me}/{date:%Y}\x22,\x0a\
]\x0asingle_check_o\
nly = true\x0a\
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
\x00\x00\x01\x9e\x00Xs\xd7\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
