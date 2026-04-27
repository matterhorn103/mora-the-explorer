# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x02O\
M\
ora the Explorer\
\x0aMatt Milner\x0av2.\
0.0b4\x0aLicense: G\
PLv3\x0a<a href=\x22ma\
ilto:milner@uni-\
muenster.de\x22>Rep\
ort a bug</a>\x0aCh\
anges in version\
 2.0.0:\x0a- Update\
 for move to new\
 server\x0a- Big re\
write, codebase \
is now much more\
 structured and \
maintainable\x0a- I\
nclusion of expe\
riment in folder\
 name is now opt\
ional\x0a- Solvent \
and frequency me\
tadata available\
 on all spectrom\
eters\x0a- Option t\
o include the or\
iginal folder na\
me\x0a- Buttons to \
select paths usi\
ng the system fi\
le explorer\x0a- Fi\
eld to specify t\
he server addres\
s from the GUI (\
useful on macOS \
and Linux)\x0a- CLI\
 and API work en\
tirely independe\
ntly of a GUI\x0a\
\x00\x00\x14a\
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
e user's own\x0a# c\
onfig.toml file,\
 at:\x0a# Windows: \
 %USERPROFILE%\x5cA\
ppData\x5cRoaming\x5cm\
ora_the_explorer\
\x5cconfig.toml\x0a# m\
acOS:    ~/Libra\
ry/Application S\
upport/mora_the_\
explorer/config.\
toml\x0a# Linux:   \
 $XDG_CONFIG_HOM\
E/mora_the_explo\
rer or ~/.config\
/mora_the_explor\
er/config.toml\x0a\x0a\
# Values specifi\
ed in the user v\
ersion of config\
.toml take prece\
dence over those\
\x0a# specified her\
e.\x0a\x0a[options]\x0aus\
er = \x22mjm\x22\x0auser_\
name = \x22\x22\x0agroup \
= \x22gil\x22\x0aspec = \x22\
neo400\x22\x0arepeat_s\
witch = false\x0are\
peat_delay = 5\x0a\x0a\
[options.naming]\
\x0agroup = false\x0au\
ser = true\x0asolve\
nt = false\x0afrequ\
ency = false\x0aexp\
eriment = true\x0ao\
riginal = false\x0a\
\x0a\x0a[appearance]\x0as\
tart_button_colo\
ur = \x22#b88cce\x22\x0a\x0a\
\x0a[paths]\x0a# Paths\
 to the server, \
different by OS\x0a\
# Mount point pr\
obably needs to \
be changed by th\
e user on macOS \
and Linux\x0awindow\
s = \x22//samba.pub\
lic.os.wwu.de/us\
ershare/projects\
/q_nmr-oc/nmr\x22\x0ad\
arwin = \x22/Volume\
s/usershare/proj\
ects/q_nmr-oc/nm\
r\x22  # darwin = m\
acOS\x0alinux = \x22~/\
usershare/projec\
ts/q_nmr-oc/nmr\x22\
\x0aupdate = \x22mora_\
the_explorer\x22  #\
 Where to check \
for app updates,\
 relative to the\
 server\x0asave = \x22\
~/nmr\x22  # The lo\
cation spectra s\
hould be copied \
to\x0a\x0a\x0a[admin]\x0ause\
r_name_is_admin_\
only = true\x0apatt\
ern_separator = \
'[\x5cs_-]'\x0a\x0a\x0a[grou\
ps]\x0a# Available \
groups, listed i\
n the style `gro\
up = group_name`\
\x0a# `group` is th\
e standard initi\
alism used for e\
ach group's expe\
riments and data\
\x0a# institute-wid\
e and is used in\
 the search for \
Bruker spectra (\
as it must be in\
cluded in\x0a# the \
measurement titl\
e)\x0a# `group` is \
the full name, u\
sed for folders \
of the group e.g\
. for the 500-60\
0er\x0afer = \x22ferna\
ndez\x22\x0agar = \x22gar\
cia\x22\x0agil = \x22gilm\
our\x22\x0aglo = \x22glor\
ius\x22\x0ahei = \x22hein\
\x22\x0anae = \x22naesbor\
g\x22\x0arav = \x22ravoo\x22\
\x0astu = \x22studer\x22\x0a\
\x0a[groups.other]\x0a\
# Groups that sh\
ould be put in a\
 separate overfl\
ow list called \x22\
Other\x22 in the ap\
p\x0aac = \x22ac\x22\x0abioc\
hemie = \x22biochem\
ie\x22\x0aextern = \x22ex\
tern\x22\x0aipc = \x22ipc\
\x22\x0akb = \x22kb\x22\x0ameet\
 = \x22meet\x22\x0anuk = \
\x22nuk\x22\x0apharmazie \
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
 spec\x0a#\x0a# Possib\
le variable fiel\
ds in `check_pat\
hs` and `archive\
s` are:\x0a# - <gro\
up>         (the\
 chosen group's \
ID)\x0a# - <group_n\
ame>    (the cho\
sen group's name\
)\x0a# - any strfti\
me formatting st\
ring, with % cha\
racters, enclose\
d in {}\x0a#   - fo\
r the format cod\
es see https://d\
ocs.python.org/3\
/library/datetim\
e.html#strftime-\
strptime-behavio\
r\x0a\x0a[spectrometer\
s.archiv]\x0amanufa\
cturer = \x22bruker\
\x22\x0adisplay_name =\
 \x22Pre-2020 archi\
ve (Bruker)\x22\x0amea\
surement_pattern\
 = '<group!>\x5c_*<\
user_name>?\x5c_*<u\
ser!>\x5c_*<sample_\
id>'\x0adate_entry \
= \x22dd MMM yyyy\x22\x0a\
check_paths = [\x0a\
    \x22archiv/dpx3\
00/{%y}-dpx300_{\
%Y}/{%b%d-%Y}\x22,\x0a\
    \x22archiv/av30\
0/{%y}-av300_{%Y\
}/{%b%d-%Y}\x22,\x0a  \
  \x22archiv/av400/\
{%y}-av400_{%Y}/\
{%b%d-%Y}\x22,\x0a    \
\x22archiv/neo400a/\
{%y}-neo400a_{%Y\
}/neo400a_{%b%d-\
%Y}\x22,\x0a    \x22archi\
v/neo400/{%y}-ne\
o400b_{%Y}/neo40\
0a_{%b%d-%Y}\x22,\x0a \
   \x22archiv/neo40\
0c/{%y}-neo400c_\
{%Y}/neo400c_{%b\
%d-%Y}\x22,\x0a]\x0aadmin\
_only = true\x0asin\
gle_check_only =\
 false\x0a\x0a[spectro\
meters.av300]\x0ama\
nufacturer = \x22br\
uker\x22\x0adisplay_na\
me = \x22Studer gro\
up NMR only (300\
 MHz)\x22\x0ameasureme\
nt_pattern = '<g\
roup!>\x5c_*<user_n\
ame>?\x5c_*<user!>\x5c\
_*<sample_id>'\x0ad\
ate_entry = \x22dd \
MMM yyyy\x22\x0acheck_\
paths = [\x0a    \x22a\
v300/av1/{%b%d-%\
Y}\x22,\x0a]\x0aarchives \
= [\x0a    \x22av300/a\
v1/{%y}-av300_{%\
Y}/{%b%d-%Y}\x22,\x0a]\
\x0arestrict_to = [\
\x0a    \x22stu\x22,\x0a    \
\x22nae\x22,\x0a]\x0asingle_\
check_only = fal\
se\x0a\x0a[spectromete\
rs.neo400]\x0amanuf\
acturer = \x22bruke\
r\x22\x0adisplay_name \
= \x22Routine NMR (\
300 && 400 MHz)\x22\
\x0ameasurement_pat\
tern = '<group!>\
\x5c_*<user_name>?\x5c\
_*<user!>\x5c_*<sam\
ple_id>'\x0adate_en\
try = \x22dd MMM yy\
yy\x22\x0acheck_paths \
= [\x0a    \x22neo400/\
av1/neo400a_{%b%\
d-%Y}\x22,\x0a    \x22neo\
400/av1/neo400b_\
{%b%d-%Y}\x22,\x0a    \
\x22neo400/av1/neo4\
00c_{%b%d-%Y}\x22,\x0a\
]\x0aarchives = [\x0a \
   \x22neo400/av1/{\
%y}-neo400a_{%Y}\
/{%b%d-%Y}\x22,\x0a   \
 \x22neo400/av1/{%y\
}-neo400b_{%Y}/{\
%b%d-%Y}\x22,\x0a    \x22\
neo400/av1/{%y}-\
neo400c_{%Y}/{%b\
%d-%Y}\x22,\x0a]\x0ainclu\
de = [ \x22av300\x22 ]\
\x0asingle_check_on\
ly = false\x0a\x0a[spe\
ctrometers.hf]\x0am\
anufacturer = \x22a\
gilent\x22\x0adisplay_\
name = \x22High-fie\
ld spectrometers\
 (500 && 600 MHz\
)\x22\x0ameasurement_p\
attern = '<user!\
><sample_id>'\x0ada\
te_entry = \x22yyyy\
\x22\x0acheck_paths = \
[\x0a    \x22500-600er\
/<group_name>/{%\
Y}\x22,\x0a]\x0asingle_ch\
eck_only = true\x0a\
\
"

qt_resource_name = b"\
\x00\x0b\
\x00\xd8\xc8\xb4\
\x00v\
\x00e\x00r\x00s\x00i\x00o\x00n\x00.\x00t\x00x\x00t\
\x00\x0b\
\x0fq\x7f\xbc\
\x00c\
\x00o\x00n\x00f\x00i\x00g\x00.\x00t\x00o\x00m\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x9d\xcc\x05[\xe3\
\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x01\x00\x00\x02S\
\x00\x00\x01\x9d\xcc\x05[\xda\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
