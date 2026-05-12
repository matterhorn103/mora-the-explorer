# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x1b{\
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
r_name = \x22.+\x22\x0agr\
oup = \x22gil\x22\x0aspec\
 = \x22neo400\x22\x0arepe\
at_switch = fals\
e\x0arepeat_delay =\
 5\x0a\x0a[options.nam\
ing]\x0asample_form\
at = \x22{user}-{sa\
mple_id}\x22\x0ameasur\
ement_format.bru\
ker = \x22{user}-{s\
ample_id}_{instr\
ument}_{submissi\
on_time:%d%m%y}_\
{temperature}k_{\
experiment}_{mea\
surement_no}\x22\x0ame\
asurement_format\
.agilent = \x22{use\
r}-{sample_id}_{\
instrument}_{com\
pletion_time:%d%\
m%y}_{temperatur\
e}k_{experiment}\
_{measurement_no\
}\x22\x0a\x0a\x0a[appearance\
]\x0astart_button_c\
olour = \x22#b88cce\
\x22\x0a\x0a\x0a[paths]\x0a# Pa\
ths to the serve\
r, different by \
OS\x0a# Mount point\
 probably needs \
to be changed by\
 the user on mac\
OS and Linux\x0awin\
dows = \x22//samba.\
public.os.wwu.de\
/usershare/proje\
cts/q_nmr-oc/nmr\
\x22\x0adarwin = \x22/Vol\
umes/usershare/p\
rojects/q_nmr-oc\
/nmr\x22  # darwin \
= macOS\x0alinux = \
\x22~/usershare/pro\
jects/q_nmr-oc/n\
mr\x22\x0aupdate = \x22mo\
ra_the_explorer\x22\
  # Where to che\
ck for app updat\
es, relative to \
the server\x0asave \
= \x22~/nmr\x22  # The\
 location spectr\
a should be copi\
ed to\x0a\x0a\x0a[admin]\x0a\
user_name_is_adm\
in_only = true\x0ap\
attern_separator\
 = '[\x5cs_-]' # No\
te the single qu\
otes! (= literal\
 string)\x0aversion\
 = \x222.0.0b5\x22\x0aema\
il = \x22milner@uni\
-muenster.de\x22\x0ach\
angelog = \x22\x22\x22\x0a- \
Update for move \
to new server\x0a- \
Big rewrite, cod\
ebase is now muc\
h more structure\
d and maintainab\
le\x0a- The search \
can be set to al\
ways check the c\
urrent date whic\
h changes accord\
ingly\x0a- Spectra \
always sorted in\
to subfolders by\
 sample (like Ag\
ilent spectra)\x0a-\
 Paths are selec\
ted using the sy\
stem file explor\
er\x0a- Ability to \
specify the serv\
er address from \
the GUI (useful \
on macOS and Lin\
ux)\x0a- Solvent, i\
nstrument, exper\
iment, temperatu\
re metadata extr\
acted on all spe\
ctrometers\x0a- Met\
adata are saved \
to the measureme\
nt folder in mor\
a.toml\x0a- CLI and\
 Python API work\
 entirely indepe\
ndently of a GUI\
\x0a\x22\x22\x22\x0a\x0a\x0a[groups]\x0a\
# Available grou\
ps, listed in th\
e style `group =\
 group_name`\x0a# `\
group` is the st\
andard initialis\
m used for each \
group's experime\
nts and data\x0a# i\
nstitute-wide an\
d is used in the\
 search for Bruk\
er spectra (as i\
t must be includ\
ed in\x0a# the meas\
urement title)\x0a#\
 `group` is the \
full name, used \
for folders of t\
he group e.g. fo\
r the 500-600er\x0a\
fer = \x22fernandez\
\x22\x0agar = \x22garcia\x22\
\x0agil = \x22gilmour\x22\
\x0aglo = \x22glorius\x22\
\x0ahei = \x22hein\x22\x0ana\
e = \x22naesborg\x22\x0ar\
av = \x22ravoo\x22\x0astu\
 = \x22studer\x22\x0a\x0a[gr\
oups.other]\x0a# Gr\
oups that should\
 be put in a sep\
arate overflow l\
ist called \x22Othe\
r\x22 in the app\x0aac\
 = \x22ac\x22\x0abiochemi\
e = \x22biochemie\x22\x0a\
extern = \x22extern\
\x22\x0aipc = \x22ipc\x22\x0akb\
 = \x22kb\x22\x0ameet = \x22\
meet\x22\x0anuk = \x22nuk\
\x22\x0aocf = \x22ocf\x22\x0aph\
armazie = \x22pharm\
azie\x22\x0a\x0a\x0a[spectro\
meters]\x0a# Provid\
e the following \
information for \
each spectromete\
r category:\x0a#   \
manufacturer: th\
e manufacturer o\
f the spectromet\
er(s)\x0a#   displa\
y_name: the text\
 shown next to t\
he button in the\
 user interface\x0a\
#       (note th\
at some characte\
rs need escaping\
, e.g. write && \
for &)\x0a#   measu\
rement_pattern: \
the expected fie\
lds in the measu\
rement title\x0a#  \
 date_entry: whe\
ther the user se\
lects the full d\
ate \x22dd MMM yyyy\
\x22 or just year \x22\
yyyy\x22\x0a#   check_\
paths: the paths\
 that should be \
searched for new\
 spectra\x0a#   arc\
hives: if spectr\
a from previous \
years can't be f\
ound under check\
_paths, the\x0a#   \
    archive fold\
ers are checked \
in addition\x0a#   \
include: other s\
pectrometers whi\
ch should be sea\
rched at the sam\
e time\x0a#   restr\
ict_to: the list\
 of groups that \
should be able t\
o see the spectr\
ometer - if\x0a#   \
    this key is \
not used, the sp\
ectrometer will \
be visible to al\
l\x0a#   admin_only\
: whether the sp\
ectrometer shoul\
d only be choose\
able in admin mo\
de\x0a#   allow_sol\
vent: whether to\
 enable the fold\
er naming option\
 to include the \
solvent\x0a#   sing\
le_check_only: w\
hether users may\
 use multiday an\
d repeat checks \
for this spec\x0a#\x0a\
# Variables can \
be interpolated \
into the entries\
 in `check_paths\
` and `archives`\
\x0a# by wrapping t\
hem in curly bra\
ckets. The follo\
wing variables c\
an be used:\x0a# - \
group         (t\
he chosen group'\
s ID)\x0a# - group_\
name    (the cho\
sen group's name\
)\x0a# - date\x0a# \x0a# \
For `date`, it m\
ay be desirable \
to format it usi\
ng e.g. `{date:%\
Y}` to get `2026\
`\x0a# For the form\
at codes see htt\
ps://docs.python\
.org/3/library/d\
atetime.html#str\
ftime-strptime-b\
ehavior\x0a\x0a# Note \
that in TOML, si\
ngle quotes can \
be used for a li\
teral string to \
avoid\x0a# having t\
o use backslash \
escapes, which i\
s very useful fo\
r regex patterns\
\x0a\x0a[spectrometers\
.archiv]\x0amanufac\
turer = \x22bruker\x22\
\x0adisplay_name = \
\x22Pre-2020 archiv\
e (Bruker)\x22\x0ameas\
urement_pattern \
= '<group!>\x5c_*<u\
ser_name>?\x5c_*<us\
er!>\x5c_*<sample_i\
d>' # Note the s\
ingle quotes! (=\
 literal string)\
\x0adate_entry = \x22d\
d MMM yyyy\x22\x0achec\
k_paths = [\x0a    \
\x22archiv/dpx300/{\
date:%y}-dpx300_\
{date:%Y}/{date:\
%b%d-%Y}\x22,\x0a    \x22\
archiv/av300/{da\
te:%y}-av300_{da\
te:%Y}/{date:%b%\
d-%Y}\x22,\x0a    \x22arc\
hiv/av400/{date:\
%y}-av400_{date:\
%Y}/{date:%b%d-%\
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
<user_name>?\x5c_*<\
user!>\x5c_*<sample\
_id>'\x0adate_entry\
 = \x22dd MMM yyyy\x22\
\x0acheck_paths = [\
\x0a    \x22av300/av1/\
{date:%b%d-%Y}\x22,\
\x0a]\x0aarchives = [\x0a\
    \x22av300/av1/{\
date:%y}-av300_{\
date:%Y}/{date:%\
b%d-%Y}\x22,\x0a]\x0arest\
rict_to = [\x0a    \
\x22stu\x22,\x0a    \x22nae\x22\
,\x0a]\x0asingle_check\
_only = false\x0a\x0a[\
spectrometers.ne\
o400]\x0amanufactur\
er = \x22bruker\x22\x0adi\
splay_name = \x22Ro\
utine NMR (300 &\
& 400 MHz)\x22\x0ameas\
urement_pattern \
= '<group!>\x5c_*<u\
ser_name>?\x5c_*<us\
er!>\x5c_*<sample_i\
d>'\x0adate_entry =\
 \x22dd MMM yyyy\x22\x0ac\
heck_paths = [\x0a \
   \x22neo400/av1/n\
eo400a_{date:%b%\
d-%Y}\x22,\x0a    \x22neo\
400/av1/neo400b_\
{date:%b%d-%Y}\x22,\
\x0a    \x22neo400/av1\
/neo400c_{date:%\
b%d-%Y}\x22,\x0a]\x0aarch\
ives = [\x0a    \x22ne\
o400/av1/{date:%\
y}-neo400a_{date\
:%Y}/{date:%b%d-\
%Y}\x22,\x0a    \x22neo40\
0/av1/{date:%y}-\
neo400b_{date:%Y\
}/{date:%b%d-%Y}\
\x22,\x0a    \x22neo400/a\
v1/{date:%y}-neo\
400c_{date:%Y}/{\
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
r!><sample_id>'\x0a\
measurement_patt\
ern = '<user!><s\
ample_id>_(\x5cd{6}\
)_<temperature>k\
_<experiment>_<m\
easurement_no>\x5c.\
fid'\x0adate_entry \
= \x22yyyy\x22\x0acheck_p\
aths = [\x0a    \x2250\
0-600er/{group_n\
ame}/{date:%Y}\x22,\
\x0a]\x0aarchives = [\x0a\
    \x22archiv/500-\
600er/{group_nam\
e}/{date:%Y}\x22,\x0a]\
\x0asingle_check_on\
ly = true\x0a\
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
\x00\x00\x01\x9e\x1c\xd0W\x80\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
