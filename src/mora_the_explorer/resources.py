# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x18\x8c\
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
#\x0a# Possible var\
iable fields in \
`check_paths` an\
d `archives` are\
:\x0a# - <group>   \
      (the chose\
n group's ID)\x0a# \
- <group_name>  \
  (the chosen gr\
oup's name)\x0a# - \
any strftime for\
matting string, \
with % character\
s, enclosed in {\
}\x0a#   - for the \
format codes see\
 https://docs.py\
thon.org/3/libra\
ry/datetime.html\
#strftime-strpti\
me-behavior\x0a\x0a[sp\
ectrometers.arch\
iv]\x0amanufacturer\
 = \x22bruker\x22\x0adisp\
lay_name = \x22Pre-\
2020 archive (Br\
uker)\x22\x0ameasureme\
nt_pattern = '<g\
roup!>\x5c_*<user_n\
ame>?\x5c_*<user!>\x5c\
_*<sample_id>'\x0ad\
ate_entry = \x22dd \
MMM yyyy\x22\x0acheck_\
paths = [\x0a    \x22a\
rchiv/dpx300/{%y\
}-dpx300_{%Y}/{%\
b%d-%Y}\x22,\x0a    \x22a\
rchiv/av300/{%y}\
-av300_{%Y}/{%b%\
d-%Y}\x22,\x0a    \x22arc\
hiv/av400/{%y}-a\
v400_{%Y}/{%b%d-\
%Y}\x22,\x0a    \x22archi\
v/neo400a/{%y}-n\
eo400a_{%Y}/neo4\
00a_{%b%d-%Y}\x22,\x0a\
    \x22archiv/neo4\
00b/{%y}-neo400b\
_{%Y}/neo400b_{%\
b%d-%Y}\x22,\x0a    \x22a\
rchiv/neo400c/{%\
y}-neo400c_{%Y}/\
neo400c_{%b%d-%Y\
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
\x5c_*<user!>\x5c_*<sa\
mple_id>'\x0adate_e\
ntry = \x22dd MMM y\
yyy\x22\x0acheck_paths\
 = [\x0a    \x22av300/\
av1/{%b%d-%Y}\x22,\x0a\
]\x0aarchives = [\x0a \
   \x22av300/av1/{%\
y}-av300_{%Y}/{%\
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
eo400a_{%b%d-%Y}\
\x22,\x0a    \x22neo400/a\
v1/neo400b_{%b%d\
-%Y}\x22,\x0a    \x22neo4\
00/av1/neo400c_{\
%b%d-%Y}\x22,\x0a]\x0aarc\
hives = [\x0a    \x22n\
eo400/av1/{%y}-n\
eo400a_{%Y}/{%b%\
d-%Y}\x22,\x0a    \x22neo\
400/av1/{%y}-neo\
400b_{%Y}/{%b%d-\
%Y}\x22,\x0a    \x22neo40\
0/av1/{%y}-neo40\
0c_{%Y}/{%b%d-%Y\
}\x22,\x0a]\x0ainclude = \
[ \x22av300\x22 ]\x0asing\
le_check_only = \
false\x0a\x0a[spectrom\
eters.hf]\x0amanufa\
cturer = \x22agilen\
t\x22\x0adisplay_name \
= \x22High-field sp\
ectrometers (500\
 && 600 MHz)\x22\x0asa\
mple_pattern = '\
<user!><sample_i\
d>'\x0ameasurement_\
pattern = '<user\
!><sample_id>\x5c_(\
\x5cd{6})\x5c_(\x5cd{3}k)\
\x5c_(.+)_\x5cd\x5c.fid'\x0a\
date_entry = \x22yy\
yy\x22\x0acheck_paths \
= [\x0a    \x22500-600\
er/<group_name>/\
{%Y}\x22,\x0a]\x0aarchive\
s = [\x0a    \x22archi\
v/500-600er/<gro\
up_name>/{%Y}\x22,\x0a\
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
\x00\x00\x01\x9d\xd9\xdd\x87\x97\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
