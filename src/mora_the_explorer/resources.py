# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x1b\xc0\
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
user = \x22mjm\x22\x0agro\
up = \x22gil\x22\x0aspec \
= \x22neo400\x22\x0arepea\
t_switch = false\
\x0arepeat_delay = \
5\x0a\x0a[options.nami\
ng]\x0asample_forma\
t = \x22{user}-{use\
r2}-{sample_id}\x22\
\x0ameasurement_for\
mat.bruker = \x22{u\
ser}-{user2}-{sa\
mple_id}_{instru\
ment}_{submissio\
n_time:%d%m%y}_{\
temperature}k_{e\
xperiment}_{meas\
urement_no}\x22\x0amea\
surement_format.\
agilent = \x22{user\
}-{user2}-{sampl\
e_id}_{instrumen\
t}_{completion_t\
ime:%d%m%y}_{tem\
perature}k_{expe\
riment}_{measure\
ment_no}\x22\x0a\x0a\x0a[app\
earance]\x0astart_b\
utton_colour = \x22\
#b88cce\x22\x0a\x0a\x0a[path\
s]\x0a# Paths to th\
e server, differ\
ent by OS\x0a# Moun\
t point probably\
 needs to be cha\
nged by the user\
 on macOS and Li\
nux\x0awindows = \x22/\
/samba.public.os\
.wwu.de/usershar\
e/projects/q_nmr\
-oc/nmr\x22\x0adarwin \
= \x22/Volumes/user\
share/projects/q\
_nmr-oc/nmr\x22  # \
darwin = macOS\x0al\
inux = \x22~/usersh\
are/projects/q_n\
mr-oc/nmr\x22\x0aupdat\
e = \x22mora_the_ex\
plorer\x22  # Where\
 to check for ap\
p updates, relat\
ive to the serve\
r\x0asave = \x22\x22  # T\
he location spec\
tra should be co\
pied to - if emp\
ty, the user is \
asked on launch\x0a\
\x0a\x0a[admin]\x0apatter\
n_separator = '[\
\x5cs_-]' # Note th\
e single quotes!\
 (= literal stri\
ng)\x0aversion = \x222\
.0.0b6\x22\x0aemail = \
\x22milner@uni-muen\
ster.de\x22\x0achangel\
og = \x22\x22\x22\x0a- Updat\
e for move to ne\
w server\x0a- Big r\
ewrite, codebase\
 is now much mor\
e structured and\
 maintainable\x0a- \
The search can b\
e set to always \
check the curren\
t date which cha\
nges accordingly\
\x0a- Spectra alway\
s sorted into su\
bfolders by samp\
le (like Agilent\
 spectra)\x0a- Path\
s are selected u\
sing the system \
file explorer\x0a- \
Ability to speci\
fy the server ad\
dress from the G\
UI (useful on ma\
cOS and Linux)\x0a-\
 Solvent, instru\
ment, experiment\
, temperature me\
tadata extracted\
 on all spectrom\
eters\x0a- Metadata\
 are saved to th\
e measurement fo\
lder in mora.tom\
l\x0a- CLI and Pyth\
on API work enti\
rely independent\
ly of a GUI\x0a\x22\x22\x22\x0a\
\x0a\x0a[groups]\x0a# Ava\
ilable groups, l\
isted in the sty\
le `group = grou\
p_name`\x0a# `group\
` is the standar\
d initialism use\
d for each group\
's experiments a\
nd data\x0a# instit\
ute-wide and is \
used in the sear\
ch for Bruker sp\
ectra (as it mus\
t be included in\
\x0a# the measureme\
nt title)\x0a# `gro\
up` is the full \
name, used for f\
olders of the gr\
oup e.g. for the\
 500-600er\x0afer =\
 \x22fernandez\x22\x0agar\
 = \x22garcia\x22\x0agil \
= \x22gilmour\x22\x0aglo \
= \x22glorius\x22\x0ahei \
= \x22hein\x22\x0anae = \x22\
naesborg\x22\x0arav = \
\x22ravoo\x22\x0astu = \x22s\
tuder\x22\x0a\x0a[groups.\
other]\x0a# Groups \
that should be p\
ut in a separate\
 overflow list c\
alled \x22Other\x22 in\
 the app\x0aac = \x22a\
c\x22\x0abiochemie = \x22\
biochemie\x22\x0aexter\
n = \x22extern\x22\x0aipc\
 = \x22ipc\x22\x0akb = \x22k\
b\x22\x0ameet = \x22meet\x22\
\x0anuk = \x22nuk\x22\x0aocf\
 = \x22ocf\x22\x0apharmaz\
ie = \x22pharmazie\x22\
\x0a\x0a\x0a[spectrometer\
s]\x0a# Provide the\
 following infor\
mation for each \
spectrometer cat\
egory:\x0a#   manuf\
acturer: the man\
ufacturer of the\
 spectrometer(s)\
\x0a#   display_nam\
e: the text show\
n next to the bu\
tton in the user\
 interface\x0a#    \
   (note that so\
me characters ne\
ed escaping, e.g\
. write && for &\
)\x0a#   measuremen\
t_pattern: the e\
xpected fields i\
n the measuremen\
t title\x0a#   date\
_entry: whether \
the user selects\
 the full date \x22\
dd MMM yyyy\x22 or \
just year \x22yyyy\x22\
\x0a#   check_paths\
: the paths that\
 should be searc\
hed for new spec\
tra\x0a#   archives\
: if spectra fro\
m previous years\
 can't be found \
under check_path\
s, the\x0a#       a\
rchive folders a\
re checked in ad\
dition\x0a#   inclu\
de: other spectr\
ometers which sh\
ould be searched\
 at the same tim\
e\x0a#   restrict_t\
o: the list of g\
roups that shoul\
d be able to see\
 the spectromete\
r - if\x0a#       t\
his key is not u\
sed, the spectro\
meter will be vi\
sible to all\x0a#  \
 admin_only: whe\
ther the spectro\
meter should onl\
y be chooseable \
in admin mode\x0a# \
  allow_solvent:\
 whether to enab\
le the folder na\
ming option to i\
nclude the solve\
nt\x0a#   single_ch\
eck_only: whethe\
r users may use \
multiday and rep\
eat checks for t\
his spec\x0a#\x0a# Var\
iables can be in\
terpolated into \
the entries in `\
check_paths` and\
 `archives`\x0a# by\
 wrapping them i\
n curly brackets\
. The following \
variables can be\
 used:\x0a# - group\
         (the ch\
osen group's ID)\
\x0a# - group_name \
   (the chosen g\
roup's name)\x0a# -\
 date\x0a#\x0a# For `d\
ate`, it may be \
desirable to for\
mat it using e.g\
. `{date:%Y}` to\
 get `2026`\x0a# Fo\
r the format cod\
es see https://d\
ocs.python.org/3\
/library/datetim\
e.html#strftime-\
strptime-behavio\
r\x0a\x0a# Note that i\
n TOML, single q\
uotes can be use\
d for a literal \
string to avoid\x0a\
# having to use \
backslash escape\
s, which is very\
 useful for rege\
x patterns\x0a\x0a[spe\
ctrometers.archi\
v]\x0amanufacturer \
= \x22bruker\x22\x0adispl\
ay_name = \x22Pre-2\
020 archive (Bru\
ker)\x22\x0ameasuremen\
t_pattern = '<gr\
oup!>\x5c_*<user_na\
me>?\x5c_*<user!>\x5c_\
*<user2!>?\x5c_*<sa\
mple_id!>' # Not\
e the single quo\
tes! (= literal \
string)\x0adate_ent\
ry = \x22dd MMM yyy\
y\x22\x0acheck_paths =\
 [\x0a    \x22archiv/d\
px300/{date:%y}-\
dpx300_{date:%Y}\
/{date:%b%d-%Y}\x22\
,\x0a    \x22archiv/av\
300/{date:%y}-av\
300_{date:%Y}/{d\
ate:%b%d-%Y}\x22,\x0a \
   \x22archiv/av400\
/{date:%y}-av400\
_{date:%Y}/{date\
:%b%d-%Y}\x22,\x0a    \
\x22archiv/neo400a/\
{date:%y}-neo400\
a_{date:%Y}/neo4\
00a_{date:%b%d-%\
Y}\x22,\x0a    \x22archiv\
/neo400b/{date:%\
y}-neo400b_{date\
:%Y}/neo400b_{da\
te:%b%d-%Y}\x22,\x0a  \
  \x22archiv/neo400\
c/{date:%y}-neo4\
00c_{date:%Y}/ne\
o400c_{date:%b%d\
-%Y}\x22,\x0a]\x0aadmin_o\
nly = true\x0asingl\
e_check_only = f\
alse\x0a\x0a[spectrome\
ters.av300]\x0amanu\
facturer = \x22bruk\
er\x22\x0adisplay_name\
 = \x22Studer group\
 NMR only (300 M\
Hz)\x22\x0ameasurement\
_pattern = '<gro\
up!>\x5c_*<user_nam\
e>?\x5c_*<user!>\x5c_*\
<user2!>?\x5c_*<sam\
ple_id!>'\x0adate_e\
ntry = \x22dd MMM y\
yyy\x22\x0acheck_paths\
 = [\x0a    \x22av300/\
av1/{date:%b%d-%\
Y}\x22,\x0a]\x0aarchives \
= [\x0a    \x22av300/a\
v1/{date:%y}-av3\
00_{date:%Y}/{da\
te:%b%d-%Y}\x22,\x0a]\x0a\
restrict_to = [\x0a\
    \x22stu\x22,\x0a    \x22\
nae\x22,\x0a]\x0asingle_c\
heck_only = fals\
e\x0a\x0a[spectrometer\
s.neo400]\x0amanufa\
cturer = \x22bruker\
\x22\x0adisplay_name =\
 \x22Routine NMR (3\
00 && 400 MHz)\x22\x0a\
measurement_patt\
ern = '<group!>\x5c\
_*<user_name>?\x5c_\
*<user!>\x5c_*<user\
2!>?\x5c_*<sample_i\
d!>'\x0adate_entry \
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
er!><user2!>?<sa\
mple_id!>'\x0ameasu\
rement_pattern =\
 '<user!><user2!\
>?<sample_id!>_(\
\x5cd{6})_<temperat\
ure>k_<experimen\
t>_<measurement_\
no>\x5c.fid'\x0adate_e\
ntry = \x22yyyy\x22\x0ach\
eck_paths = [\x0a  \
  \x22500-600er/{gr\
oup_name}/{date:\
%Y}\x22,\x0a]\x0aarchives\
 = [\x0a    \x22archiv\
/500-600er/{grou\
p_name}/{date:%Y\
}\x22,\x0a]\x0asingle_che\
ck_only = true\x0a\
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
\x00\x00\x01\x9e\xab\xb5xe\
"


def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)


def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)


qInitResources()
