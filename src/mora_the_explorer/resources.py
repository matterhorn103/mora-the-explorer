# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x1a\xed\
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
]\x0a# Available gr\
oups, listed in \
the style `group\
 = group_name`\x0a#\
 `group` is the \
standard initial\
ism used for eac\
h group's experi\
ments and data\x0a#\
 institute-wide \
and is used in t\
he search for Br\
uker spectra (as\
 it must be incl\
uded in\x0a# the me\
asurement title)\
\x0a# `group` is th\
e full name, use\
d for folders of\
 the group e.g. \
for the 500-600e\
r\x0afer = \x22fernand\
ez\x22\x0agar = \x22garci\
a\x22\x0agil = \x22gilmou\
r\x22\x0aglo = \x22gloriu\
s\x22\x0ahei = \x22hein\x22\x0a\
nae = \x22naesborg\x22\
\x0arav = \x22ravoo\x22\x0as\
tu = \x22studer\x22\x0a\x0a[\
groups.other]\x0a# \
Groups that shou\
ld be put in a s\
eparate overflow\
 list called \x22Ot\
her\x22 in the app\x0a\
ac = \x22ac\x22\x0abioche\
mie = \x22biochemie\
\x22\x0aextern = \x22exte\
rn\x22\x0aipc = \x22ipc\x22\x0a\
kb = \x22kb\x22\x0ameet =\
 \x22meet\x22\x0anuk = \x22n\
uk\x22\x0aocf = \x22ocf\x22\x0a\
pharmazie = \x22pha\
rmazie\x22\x0a\x0a\x0a[spect\
rometers]\x0a# Prov\
ide the followin\
g information fo\
r each spectrome\
ter category:\x0a# \
  manufacturer: \
the manufacturer\
 of the spectrom\
eter(s)\x0a#   disp\
lay_name: the te\
xt shown next to\
 the button in t\
he user interfac\
e\x0a#       (note \
that some charac\
ters need escapi\
ng, e.g. write &\
& for &)\x0a#   mea\
surement_pattern\
: the expected f\
ields in the mea\
surement title\x0a#\
   date_entry: w\
hether the user \
selects the full\
 date \x22dd MMM yy\
yy\x22 or just year\
 \x22yyyy\x22\x0a#   chec\
k_paths: the pat\
hs that should b\
e searched for n\
ew spectra\x0a#   a\
rchives: if spec\
tra from previou\
s years can't be\
 found under che\
ck_paths, the\x0a# \
      archive fo\
lders are checke\
d in addition\x0a# \
  include: other\
 spectrometers w\
hich should be s\
earched at the s\
ame time\x0a#   res\
trict_to: the li\
st of groups tha\
t should be able\
 to see the spec\
trometer - if\x0a# \
      this key i\
s not used, the \
spectrometer wil\
l be visible to \
all\x0a#   admin_on\
ly: whether the \
spectrometer sho\
uld only be choo\
seable in admin \
mode\x0a#   allow_s\
olvent: whether \
to enable the fo\
lder naming opti\
on to include th\
e solvent\x0a#   si\
ngle_check_only:\
 whether users m\
ay use multiday \
and repeat check\
s for this spec\x0a\
#\x0a# Variables ca\
n be interpolate\
d into the entri\
es in `check_pat\
hs` and `archive\
s`\x0a# by wrapping\
 them in curly b\
rackets. The fol\
lowing variables\
 can be used:\x0a# \
- group         \
(the chosen grou\
p's ID)\x0a# - grou\
p_name    (the c\
hosen group's na\
me)\x0a# - date\x0a# \x0a\
# For `date`, it\
 may be desirabl\
e to format it u\
sing e.g. `{date\
:%Y}` to get `20\
26`\x0a# For the fo\
rmat codes see h\
ttps://docs.pyth\
on.org/3/library\
/datetime.html#s\
trftime-strptime\
-behavior\x0a\x0a# Not\
e that in TOML, \
single quotes ca\
n be used for a \
literal string t\
o avoid\x0a# having\
 to use backslas\
h escapes, which\
 is very useful \
for regex patter\
ns\x0a\x0a[spectromete\
rs.archiv]\x0amanuf\
acturer = \x22bruke\
r\x22\x0adisplay_name \
= \x22Pre-2020 arch\
ive (Bruker)\x22\x0ame\
asurement_patter\
n = '<group!>\x5c_*\
<user_name>?\x5c_*<\
user!>\x5c_*<sample\
_id>' # Note the\
 single quotes! \
(= literal strin\
g)\x0adate_entry = \
\x22dd MMM yyyy\x22\x0ach\
eck_paths = [\x0a  \
  \x22archiv/dpx300\
/{date:%y}-dpx30\
0_{date:%Y}/{dat\
e:%b%d-%Y}\x22,\x0a   \
 \x22archiv/av300/{\
date:%y}-av300_{\
date:%Y}/{date:%\
b%d-%Y}\x22,\x0a    \x22a\
rchiv/av400/{dat\
e:%y}-av400_{dat\
e:%Y}/{date:%b%d\
-%Y}\x22,\x0a    \x22arch\
iv/neo400a/{date\
:%y}-neo400a_{da\
te:%Y}/neo400a_{\
date:%b%d-%Y}\x22,\x0a\
    \x22archiv/neo4\
00b/{date:%y}-ne\
o400b_{date:%Y}/\
neo400b_{date:%b\
%d-%Y}\x22,\x0a    \x22ar\
chiv/neo400c/{da\
te:%y}-neo400c_{\
date:%Y}/neo400c\
_{date:%b%d-%Y}\x22\
,\x0a]\x0aadmin_only =\
 true\x0asingle_che\
ck_only = false\x0a\
\x0a[spectrometers.\
av300]\x0amanufactu\
rer = \x22bruker\x22\x0ad\
isplay_name = \x22S\
tuder group NMR \
only (300 MHz)\x22\x0a\
measurement_patt\
ern = '<group!>\x5c\
_*<user_name>?\x5c_\
*<user!>\x5c_*<samp\
le_id>'\x0adate_ent\
ry = \x22dd MMM yyy\
y\x22\x0acheck_paths =\
 [\x0a    \x22av300/av\
1/{date:%b%d-%Y}\
\x22,\x0a]\x0aarchives = \
[\x0a    \x22av300/av1\
/{date:%y}-av300\
_{date:%Y}/{date\
:%b%d-%Y}\x22,\x0a]\x0are\
strict_to = [\x0a  \
  \x22stu\x22,\x0a    \x22na\
e\x22,\x0a]\x0asingle_che\
ck_only = false\x0a\
\x0a[spectrometers.\
neo400]\x0amanufact\
urer = \x22bruker\x22\x0a\
display_name = \x22\
Routine NMR (300\
 && 400 MHz)\x22\x0ame\
asurement_patter\
n = '<group!>\x5c_*\
<user_name>?\x5c_*<\
user!>\x5c_*<sample\
_id>'\x0adate_entry\
 = \x22dd MMM yyyy\x22\
\x0acheck_paths = [\
\x0a    \x22neo400/av1\
/neo400a_{date:%\
b%d-%Y}\x22,\x0a    \x22n\
eo400/av1/neo400\
b_{date:%b%d-%Y}\
\x22,\x0a    \x22neo400/a\
v1/neo400c_{date\
:%b%d-%Y}\x22,\x0a]\x0aar\
chives = [\x0a    \x22\
neo400/av1/{date\
:%y}-neo400a_{da\
te:%Y}/{date:%b%\
d-%Y}\x22,\x0a    \x22neo\
400/av1/{date:%y\
}-neo400b_{date:\
%Y}/{date:%b%d-%\
Y}\x22,\x0a    \x22neo400\
/av1/{date:%y}-n\
eo400c_{date:%Y}\
/{date:%b%d-%Y}\x22\
,\x0a]\x0ainclude = [ \
\x22av300\x22 ]\x0asingle\
_check_only = fa\
lse\x0a\x0a[spectromet\
ers.hf]\x0amanufact\
urer = \x22agilent\x22\
\x0adisplay_name = \
\x22High-field spec\
trometers (500 &\
& 600 MHz)\x22\x0asamp\
le_pattern = '<u\
ser!><sample_id>\
'\x0ameasurement_pa\
ttern = '<user!>\
<sample_id>_(\x5cd{\
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
\x00\x00\x01\x9e\x00^W\x9f\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
