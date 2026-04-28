This directory contains a mock-up of the NMR server with four "spectrometer" directories:

1. "av300"
  - For a single 300 MHz Bruker spectrometer
  - Each day's spectra from the current year are saved under the date e.g. `Oct16-2023`
  - Previous year's spectra are saved in the same dated folders but are collected together into a folder called e.g. `22-av300_2022`

2. "dpx300"
  - Represents an old, no-longer-used 300 MHz Bruker spectrometer
  - Access is admin-only
  - The tree structure is the same as above

3. "neo400"
  - A single folder to which three 400 MHz Bruker spectrometers (neo400a, neo400b, neo400c) are saving
  - The tree structure is similar to the above but each dated folder is prefixed with `neo400[a,b,c]` e.g. `neo400b_Oct16-2023` and the format of the archive folders are e.g. `22-neo400a_2022`

4. "v600"
  - A 600 MHz Agilent spectrometer
  - Spectra are organised first by group (full group name), then by year

Various "fake" spectra have been created to fill out the tree and give us something to test on.

For **Bruker** spectra, the contents of each folder is identical with the exception of:
- `./fid`
- `./pdata/1/parm.txt`
- `./pdata/1/title`

For **Agilent** spectra, the contents of each folder is identical, other than the following changes:
- The measurement folder name and the names of the spectrum folders within have their names changed accordingly
- For each spectrum folder, `./spectrum.fid/fid` and `./spectrum.fid/text` have been changed
- `./dirinfo/macdir/sampleinfo` has been changed

Originally only five groups, three users, and three dates were mocked:

- groups:
  - gil = "gilmour"
  - glo = "glorius"
  - stu = "studer"

- overflow groups:
  - biochemie = "biochemie"
  - pharmazie = "pharmazie"

- users:
  - { user = "mjm", user_name = "milner", group = "stu" }
  - { user = "dna", user_name = "adams", group = "stu" }
  - { user = "stp", user_name = "pratchett", group = "gil" }

- dates:
  - 2023-10-16
  - 2023-10-15
  - 2022-10-15

2023 is treated as the current year, while the 2022 spectra are in the "archive" folders.

However, there are two folders for 2023-10-16 due to there being two spectra with EXPNO 100.

**Note that the original set of spectra has been expanded and the above have been supplemented.**

## Unique FIDs

Each fid file includes an integer from **1 to 92** to make them each unique across the whole mock server (even when the metadata for two spectra are otherwise identical).

## Spectra

### Bruker

Originally, the Bruker spectrometers had this set of fake spectra "measured" on it, some of them with deliberately unusual or incorrect titles:

2022-10-15:
- 60 = stu dna 979-repeat (1H, b)  // Non-standard sample ID
- 110 = stu mjm 382-3 (1H, a)
- 161 = gil stp 1-02 (1H, c)  // "stp" didn't know yet that they should number samples from the same reaction

2023-10-15:
- 30 = stu dna 1370-1 (1H, CD2Cl2, c)
- 31 = stu dna 1370-1 (13C, CD2Cl2, c)
- 90 = gil stp ab-10-1 (1H, b)  // "ab" joined to experiment/sample number
- 200 = stu mjm 500-1 (1H, a)
- 430 = gil stp-ab-10-2 (1H, c)  // "stp" and "ab" and experiment/sample number all joined

2023-10-16:
- 10 = gil stp 2-200-3 (1H, c)  // A student who likes to number their experiments by book
- 100 = stu mjm 501-1 (1H, DMSO, a)  // Solvent other than CDCl3 (others are all chloroform unless noted)
- 110 = stu dna 1455-1 (1H, b)  // Four-digit reaction numbers
- 180 = stu mjm 501-2 (1H, a)
- 181 = stu mjm 501-2 (13C, a)
- 250 = gil stp ab 12-1 (1H, a)  // Praktikant "ab" working with "stp", "ab" is separated

2023-10-16_2
- 100 = stu dna 1452-1 (1H, a)  // Overflow folder for day

The av300 spectrometer has all of the above.

The neo400 spectrometers have all of the above as well, but split amongst the three spectrometers -- which is indicated by the letters in the parentheses.

Since then the following have been added:

- av300/Oct14-2023/not_a_measurement  // A folder without any measurement data or metadata
- av300/Oct14-2023/.placeholder  // A file as opposed to a folder
- av300/Oct17-2023/10  // A measurement with a title file but no title
- av300/Oct15-2023/32 = stu dna 1370-1 (19F, CD2Cl2)  // To give a set of three measurements for the same sample

### Agilent

Note that for some group/year combinations there are folders but no spectra, just a `.placeholder` file (so that it can be checked in with Git).

The following samples are mocked. Note that not all contain a proper `procpar` file yet; those missing one are marked with a !

studer/2022
- mjm382 ! // No sample number

studer/2023
- mjm500-1
- mjm501-1  // Solvent other than chloroform (DMSO)
- dna1455 ! // Proton only

gilmour/2023
- stp2-200 !
- stpab12-1 !

gilmour/2026
// These akw spectra were added specifically because they weren't being found properly
- akw004-4  // HMBC has an empty `text` file
- akw017-3
- akw17-4  // HMBC has an empty `text` file
- akw032-2-1

Most contain 1H, 13C, and COSY experiments.
