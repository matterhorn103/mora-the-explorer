# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x18F\
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
= \x222.0.0b4\x22\x0aemai\
l = \x22milner@uni-\
muenster.de\x22\x0acha\
ngelog = \x22\x22\x22\x0a- U\
pdate for move t\
o new server\x0a- B\
ig rewrite, code\
base is now much\
 more structured\
 and maintainabl\
e\x0a- Inclusion of\
 experiment in f\
older name is no\
w optional\x0a- Sol\
vent and frequen\
cy metadata avai\
lable on all spe\
ctrometers\x0a- Opt\
ion to include t\
he original fold\
er name\x0a- Button\
s to select path\
s using the syst\
em file explorer\
\x0a- Field to spec\
ify the server a\
ddress from the \
GUI (useful on m\
acOS and Linux)\x0a\
- CLI and API wo\
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
uk\x22\x0apharmazie = \
\x22pharmazie\x22\x0a\x0a\x0a[s\
pectrometers]\x0a# \
Provide the foll\
owing informatio\
n for each spect\
rometer category\
:\x0a#   manufactur\
er: the manufact\
urer of the spec\
trometer(s)\x0a#   \
display_name: th\
e text shown nex\
t to the button \
in the user inte\
rface\x0a#       (n\
ote that some ch\
aracters need es\
caping, e.g. wri\
te && for &)\x0a#  \
 measurement_pat\
tern: the expect\
ed fields in the\
 measurement tit\
le\x0a#   date_entr\
y: whether the u\
ser selects the \
full date \x22dd MM\
M yyyy\x22 or just \
year \x22yyyy\x22\x0a#   \
check_paths: the\
 paths that shou\
ld be searched f\
or new spectra\x0a#\
   archives: if \
spectra from pre\
vious years can'\
t be found under\
 check_paths, th\
e\x0a#       archiv\
e folders are ch\
ecked in additio\
n\x0a#   include: o\
ther spectromete\
rs which should \
be searched at t\
he same time\x0a#  \
 restrict_to: th\
e list of groups\
 that should be \
able to see the \
spectrometer - i\
f\x0a#       this k\
ey is not used, \
the spectrometer\
 will be visible\
 to all\x0a#   admi\
n_only: whether \
the spectrometer\
 should only be \
chooseable in ad\
min mode\x0a#   all\
ow_solvent: whet\
her to enable th\
e folder naming \
option to includ\
e the solvent\x0a# \
  single_check_o\
nly: whether use\
rs may use multi\
day and repeat c\
hecks for this s\
pec\x0a#\x0a# Possible\
 variable fields\
 in `check_paths\
` and `archives`\
 are:\x0a# - <group\
>         (the c\
hosen group's ID\
)\x0a# - <group_nam\
e>    (the chose\
n group's name)\x0a\
# - any strftime\
 formatting stri\
ng, with % chara\
cters, enclosed \
in {}\x0a#   - for \
the format codes\
 see https://doc\
s.python.org/3/l\
ibrary/datetime.\
html#strftime-st\
rptime-behavior\x0a\
\x0a[spectrometers.\
archiv]\x0amanufact\
urer = \x22bruker\x22\x0a\
display_name = \x22\
Pre-2020 archive\
 (Bruker)\x22\x0ameasu\
rement_pattern =\
 '<group!>\x5c_*<us\
er_name>?\x5c_*<use\
r!>\x5c_*<sample_id\
>'\x0adate_entry = \
\x22dd MMM yyyy\x22\x0ach\
eck_paths = [\x0a  \
  \x22archiv/dpx300\
/{%y}-dpx300_{%Y\
}/{%b%d-%Y}\x22,\x0a  \
  \x22archiv/av300/\
{%y}-av300_{%Y}/\
{%b%d-%Y}\x22,\x0a    \
\x22archiv/av400/{%\
y}-av400_{%Y}/{%\
b%d-%Y}\x22,\x0a    \x22a\
rchiv/neo400a/{%\
y}-neo400a_{%Y}/\
neo400a_{%b%d-%Y\
}\x22,\x0a    \x22archiv/\
neo400/{%y}-neo4\
00b_{%Y}/neo400a\
_{%b%d-%Y}\x22,\x0a   \
 \x22archiv/neo400c\
/{%y}-neo400c_{%\
Y}/neo400c_{%b%d\
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
<sample_id>'\x0adat\
e_entry = \x22dd MM\
M yyyy\x22\x0acheck_pa\
ths = [\x0a    \x22av3\
00/av1/{%b%d-%Y}\
\x22,\x0a]\x0aarchives = \
[\x0a    \x22av300/av1\
/{%y}-av300_{%Y}\
/{%b%d-%Y}\x22,\x0a]\x0ar\
estrict_to = [\x0a \
   \x22stu\x22,\x0a    \x22n\
ae\x22,\x0a]\x0asingle_ch\
eck_only = false\
\x0a\x0a[spectrometers\
.neo400]\x0amanufac\
turer = \x22bruker\x22\
\x0adisplay_name = \
\x22Routine NMR (30\
0 && 400 MHz)\x22\x0am\
easurement_patte\
rn = '<group!>\x5c_\
*<user_name>?\x5c_*\
<user!>\x5c_*<sampl\
e_id>'\x0adate_entr\
y = \x22dd MMM yyyy\
\x22\x0acheck_paths = \
[\x0a    \x22neo400/av\
1/neo400a_{%b%d-\
%Y}\x22,\x0a    \x22neo40\
0/av1/neo400b_{%\
b%d-%Y}\x22,\x0a    \x22n\
eo400/av1/neo400\
c_{%b%d-%Y}\x22,\x0a]\x0a\
archives = [\x0a   \
 \x22neo400/av1/{%y\
}-neo400a_{%Y}/{\
%b%d-%Y}\x22,\x0a    \x22\
neo400/av1/{%y}-\
neo400b_{%Y}/{%b\
%d-%Y}\x22,\x0a    \x22ne\
o400/av1/{%y}-ne\
o400c_{%Y}/{%b%d\
-%Y}\x22,\x0a]\x0ainclude\
 = [ \x22av300\x22 ]\x0as\
ingle_check_only\
 = false\x0a\x0a[spect\
rometers.hf]\x0aman\
ufacturer = \x22agi\
lent\x22\x0adisplay_na\
me = \x22High-field\
 spectrometers (\
500 && 600 MHz)\x22\
\x0asample_pattern \
= '<user!><sampl\
e_id>'\x0ameasureme\
nt_pattern = '<u\
ser!><sample_id>\
\x5c_(\x5cd{6})\x5c_(\x5cd{3\
}k)\x5c_(.+)_\x5cd\x5c.fi\
d'\x0adate_entry = \
\x22yyyy\x22\x0acheck_pat\
hs = [\x0a    \x22500-\
600er/<group_nam\
e>/{%Y}\x22,\x0a]\x0asing\
le_check_only = \
true\x0a\
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
\x00\x00\x01\x9d\xd7(\x8bv\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
