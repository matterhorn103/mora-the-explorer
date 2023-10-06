"""
Mora the Explorer checks for new NMR spectra at the Organic Chemistry department at the WWU Münster.
Copyright (C) 2023 Matthew J. Milner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import filecmp
import logging
import shutil
from datetime import date, datetime
from pathlib import Path


# Checks that two spectra with the same name are actually identical and not e.g. different
# proton measurements
def identical_spectra(mora_folder, dest_folder):
    # Read original folder path (i.e. the experiment no) of spectrum
    audit_path_mora = mora_folder / "audita.txt"
    try:
        with open(audit_path_mora, encoding="utf-8") as audit_file_mora:
            audit_mora = audit_file_mora.readlines()
            exp_mora = audit_mora[4]
    except FileNotFoundError:
        print(
            "no audita.txt file found in "
            + mora_folder
            + " - presumably measurement was unsuccessful. Spectrum skipped."
        )
        # Return True so that the spectrum on mora is treated as identical and not copied
        return True
    # Do same for existing spectrum in destination
    audit_path_dest = dest_folder / "audita.txt"
    try:
        with open(audit_path_dest, encoding="utf-8") as audit_file_dest:
            audit_dest = audit_file_dest.readlines()
            exp_dest = audit_dest[4]
    # The first spectrum with a given title is always copied, so it is possible that it doesn't
    # have an audit file
    except FileNotFoundError:
        exp_dest = None
    # Compare experiment nos
    if exp_mora == exp_dest:
        return True
    else:
        return False


# Define main checking function for Mora the Explorer
def check_nmr(
    fed_options,
    check_day,
    mora_path,
    spec_paths,
    wild_group,
    prog_bar,
    progress_callback,
):
    logging.info(f"Beginning check of {check_day} with the options:")
    logging.info(fed_options)
    # Initialize list that will be returned as output
    output_list = ["no new spectra"]
    # Confirm destination directory exists
    if Path(fed_options["dest_path"]).exists() is False:
        output_list.append("given destination folder not found!")
        logging.info("given destination folder not found!")
        return output_list
    # Confirm mora can be reached
    if mora_path.exists() is False:
        output_list.append("the mora server could not be reached!")
        logging.info("the mora server could not be reached!")
        return output_list
    # Format paths of spectrometer folders
    spectrometer = fed_options["spec"]
    if spectrometer == "300er":
        # For previous years other than the current
        year = int(check_day[-4:])
        if year != date.today().year:
            primary_check_path = (
                spec_paths[spectrometer] / f"{str(year)[-2:]}-av300_{year}" / check_day
            )
        else:
            primary_check_path = spec_paths[spectrometer] / check_day
        check_path_list = [primary_check_path]
        # Account for different structure in 2019/start of 2020
        if year <= 2020:
            check_path_300er_old = (
                spec_paths[spectrometer] / f"{str(year)[-2:]}-dpx300_{year}" / check_day
            )
            check_path_list.append(check_path_300er_old)
        # Give message if folder for the given date doesn't exist yet
        hit = False
        for path in check_path_list:
            if path.exists() is False:
                logging.info(f"no folder exists at: {path}")
            elif path.exists() is True:
                hit = True
        if hit is not True:
            output_list.append("no folders exist for this date!")
            return output_list
        # If main folder exists, check if other folders are available for same day (generated
        # on mora when two samples are submitted with same exp. no.)
        for num in range(2, 10):
            alt_path = primary_check_path.with_name(primary_check_path.name + "_" + str(num))
            if alt_path.exists() is True:
                check_path_list.append(alt_path)
        logging.info("The following paths will be checked:")
        logging.info(check_path_list)
    elif spectrometer == "400er":
        check_day_a = "neo400a_" + check_day
        check_day_b = "neo400b_" + check_day
        check_day_c = "neo400c_" + check_day
        # For previous years other than the current
        year = int(check_day[-4:])
        if year != date.today().year:
            check_path_a = (
                spec_paths[spectrometer] / f"{str(year)[-2:]}-neo400a_{year}" / check_day_a
            )
            check_path_b = (
                spec_paths[spectrometer] / f"{str(year)[-2:]}-neo400b_{year}" / check_day_b
            )
            check_path_c = (
                spec_paths[spectrometer] / f"{str(year)[-2:]}-neo400c_{year}" / check_day_c
            )
            check_path_300er = spec_paths["300er"] / f"{str(year)[-2:]}-av300_{year}" / check_day
        else:
            check_path_a = spec_paths[spectrometer] / check_day_a
            check_path_b = spec_paths[spectrometer] / check_day_b
            check_path_c = spec_paths[spectrometer] / check_day_c
            check_path_300er = spec_paths["300er"] / check_day
        check_path_list = [check_path_a, check_path_b, check_path_c, check_path_300er]
        # Account for different structure in 2019/start of 2020
        if year <= 2020:
            check_path_400er_old = (
                spec_paths[spectrometer] / f"{str(year)[-2:]}-av400_{year}" / check_day
            )
            check_path_300er_old = spec_paths["300er"] / f"{str(year)[-2:]}-dpx300_{year}" / check_day
            check_path_list.extend([check_path_400er_old, check_path_300er_old])
        # Give message if folder for the given date doesn't exist yet
        hit = False
        for path in check_path_list:
            if path.exists() is False:
                logging.info(f"no folder exists at: {path}")
            elif path.exists() is True:
                hit = True
        if hit is not True:
            output_list.append("no folders exist for this date!")
            return output_list
        # Add any extra folders for this date beyond the expected four to check list
        unchanging_check_path_list = check_path_list
        for entry in unchanging_check_path_list:
            for num in range(2, 20):
                alt_path = entry.with_name(entry.name + "_" + str(num))
                if alt_path.exists() is True:
                    check_path_list.append(alt_path)
        logging.info("The following paths will be checked:")
        logging.info(check_path_list)
    elif spectrometer == "hf":
        # Code to check folders of all groups when the nmr group is chosen and the wild group
        # option is invoked
        if wild_group is True:
            check_list = []
            # Slightly complicated bit of code here but it just goes through all folders in
            # 500-600er folder
            logging.info("The following paths will be checked:")
            logging.info(spec_paths[spectrometer].parent.iterdir())
            for group_folder in spec_paths[spectrometer].parent.iterdir():
                if group_folder.is_dir() and (group_folder.name[0] != "."):
                    try:
                        for spectrum_folder in list((group_folder / check_day).iterdir()):
                            check_list.append(spectrum_folder)
                    except FileNotFoundError:
                        logging.info(f"No spectra in {group_folder}")
                        continue
        # Normal behaviour for all other users
        else:
            logging.info("The following paths will be checked:")
            logging.info(spec_paths[spectrometer] / check_day)
            # Try to get list of spectrum folders in folder for requested spectrometer, group
            # and date
            # Display message to user if it doesn't exist yet
            try:
                check_list = list((spec_paths[spectrometer] / check_day).iterdir())
            except FileNotFoundError:
                output_list.append("no folder exists for this date!")
                logging.info("no folder exists for this date!")
                return output_list
    # Now process needs to be slightly different depending on the spectrometer, as the directory
    # structures are different
    if spectrometer == "300er" or spectrometer == "400er":
        # Initialize progress bar
        try:
            if spectrometer == "300er":
                prog_bar.setMaximum(100)
            elif spectrometer == "400er":
                prog_bar.setMaximum(100 * len(check_path_list))
        except:
            # This stops python from hanging when the program is closed
            exit()
        prog_state = 0
        progress_callback.emit(prog_state)
        # Loop through each folder in check_path_list (usually only one for 300er, several for
        # 400er as separate ones are generated for each spectrometer)
        for check_path in check_path_list:
            try:
                check_list = list(check_path.iterdir())
            except FileNotFoundError:
                continue
            # Loop through list of spectra in spectrometer folder
            logging.info("The following spectra were checked for potential matches:")
            for folder in check_list:
                logging.info(folder)
                # Extract title and experiment details from title file in spectrum folder
                title_file_path = folder / "pdata" / "1" / "title"
                try:
                    with open(title_file_path, encoding="utf-8") as title_file:
                        title_contents = title_file.readlines()
                    title = title_contents[0]
                    details = title_contents[1]
                except FileNotFoundError:
                    output_list.append(f"{folder} had no title file!")
                    logging.info("No title file found")
                    continue
                split_title = title.split()
                split_details = details.split()
                logging.info("    " + str(split_title))
                logging.info("    " + str(split_details))
                # Look for search string in extracted title, then copy matching spectra
                # Confirm that the title is even long enough to avoid IndexErrors
                if len(split_title) < 2:
                    logging.info("Title doesn't have enough parts")
                    continue
                # Add nmr to front of spectrum title so that the group initials get matched to
                # the "initials" provided by the user, allowing Klaus to download all spectra
                # from a specific group
                if (fed_options["group"] == "nmr") and (split_title[0] != "nmr"):
                    split_title.insert(0, "nmr")
                # Check if spectrum is a match for search term, including the wild option for the
                # nmr group
                if split_title[1][0:3] == fed_options["initials"] or (
                    (wild_group is True) and (split_title[2][0:3] == fed_options["initials"])
                ):
                # Or alternatively, just check if any of the title components match the initials
                # (normally to be avoided to prevent false positives)
                # if fed_options["initials"] in split_title:
                    logging.info("Spectrum matches search query!")
                    # Formatting options specifically for nmr group, include everything - even
                    # date and spec via parent folder name
                    if fed_options["group"] == "nmr":
                        new_folder_name = (
                            ("-".join(split_title[1:]))
                            + "-"
                            + ("-".join(split_details[:2]))
                            + "_"
                            + check_path.name
                            + "_"
                            + folder.name
                        )
                    # Otherwise format spectrum name according to user's choices
                    else:
                        # Format in the style of NMRCheck if requested i.e. using underscores,
                        # including initials and spectrometer and date and exp no
                        if fed_options["nmrcheck_style"] is True:
                            if len(split_title) > 2:
                                hyphenated_title = (
                                    "_".join(split_title[1:])
                                    + "_"
                                    + check_path.name
                                    + "_"
                                    + folder.name
                                )
                            else:
                                hyphenated_title = (
                                    "_".join(split_title)
                                    + "_"
                                    + check_path.name
                                    + "_"
                                    + folder.name
                                )
                        # Length checks above and below are to account for the possibility that
                        # the user might have forgotten to separate with spaces
                        # Principle applied is that if the information being dropped isn't 100%
                        # definitely what we think it is (i.e. the group name), play it safe and
                        # don't drop it
                        # Now the formatting for most cases (NMRCheck style is legacy)
                        elif len(split_title) > 2:
                            if fed_options["inc_init"] is True:
                                hyphenated_title = "-".join(split_title[1:])
                            else:
                                hyphenated_title = "-".join(split_title[2:])
                        else:
                            hyphenated_title = "-".join(split_title)
                        # Append experiment type e.g. proton to end of name, and solvent if
                        # requested
                        if fed_options["inc_solv"] is True:
                            new_folder_name = (
                                hyphenated_title + "-" + split_details[0] + "-" + split_details[1]
                            )
                        else:
                            new_folder_name = hyphenated_title + "-" + split_details[0]
                    new_folder_path = Path(fed_options["dest_path"]) / new_folder_name
                    # Check that spectrum hasn't been copied before
                    if new_folder_path.exists() is True:
                        logging.info("Spectrum with this name already exists in destination")
                        # Check that the spectra are actually identical and not e.g. different
                        # proton measurements
                        # If confirmed to be unique spectra, need to extend spectrum name with
                        # -2, -3 etc. to avoid conflict with spectra already in dest
                        identical_spectrum_found = False
                        if identical_spectra(folder, new_folder_path) is False:
                            new_folder_name = new_folder_path.name + "-2"
                            new_folder_path = new_folder_path.parent / new_folder_name
                            # While loop that will eventually settle on a new unique name
                            while new_folder_path.exists() is True:
                                # Do whole procedure again as long as name has a match in the
                                # destination
                                if identical_spectra(folder, new_folder_path) is True:
                                    identical_spectrum_found = True
                                new_folder_name = (
                                    new_folder_path.name[:-2]
                                    + "-"
                                    + str(int(new_folder_path.name[-1]) + 1)
                                )
                                new_folder_path = new_folder_path.parent / new_folder_name
                            if identical_spectrum_found is not True:
                                logging.info("but the spectrum itself has not been copied before.")
                                logging.info(f"Copying with the new name: {new_folder_path.stem}")
                                try:
                                    shutil.copytree(folder, new_folder_path)
                                except PermissionError:
                                    output_list.append(
                                        "you do not have permission to write to the given folder"
                                    )
                                    logging.info("No write permission for destination")
                                    return output_list
                                text_to_add = "spectrum found: " + new_folder_name
                                output_list.append(text_to_add)
                    # Otherwise there is no existing spectrum in the destination so
                    # straightforward copy
                    else:
                        try:
                            shutil.copytree(folder, new_folder_path)
                        except PermissionError:
                            output_list.append(
                                "you do not have permission to write to the given folder"
                            )
                            return output_list
                        text_to_add = "spectrum found: " + new_folder_name
                        logging.info(f"Spectrum saved to {new_folder_path}")
                        output_list.append(text_to_add)
                # Update progress bar
                prog_state += 100 / len(check_list)
                progress_callback.emit(round(prog_state))
    elif spectrometer == "hf":
        # Initialize progress bar
        max_progress = len(check_list)
        prog_bar.setMaximum(max_progress)
        prog_state = 0
        progress_callback.emit(prog_state)
        # Look for spectra
        logging.info("The following spectra were checked for potential matches:")
        for folder in check_list:
            logging.info(folder)
            # Check for initials at start of folder name, as folders are given the name of
            # the sample on 500 and 600 MHz spectrometers
            if folder.name[:3] == fed_options["initials"]:
                logging.info("Spectrum matches search query!")
                # Find out magnet strength, set to initial false value as flag
                magnet_freq = "x"
                contents_list = list(folder.iterdir())
                while magnet_freq == "x":
                    for cont_folder in contents_list:
                        text_file_path = cont_folder / "text"
                        if text_file_path.exists() is True:
                            with open(text_file_path, encoding="utf-8") as spectrum_text:
                                spectrum_info = spectrum_text.readlines()
                                line_with_freq_split = spectrum_info[3].split(",")
                                magnet_freq = line_with_freq_split[0]
                if fed_options["group"] == "nmr":
                    new_folder_name = (
                        folder.parent.parent.name
                        + "_"
                        + folder.parent.name
                        + "_"
                        + folder.name
                        + "_"
                        + magnet_freq
                    )
                elif fed_options["nmrcheck_style"] is True:
                    new_folder_name = (
                        fed_options["initials"] + "_" + folder.name[3:] + "_" + magnet_freq
                    )
                elif fed_options["inc_init"] is True:
                    new_folder_name = (
                        fed_options["initials"] + "-" + folder.name[3:] + "_" + magnet_freq
                    )
                else:
                    new_folder_name = folder.name[3:] + "_" + magnet_freq
                new_folder_path = Path(fed_options["dest_path"]) / new_folder_name
                # Check that spectrum hasn't been copied before
                # Begin by setting check number to >0 so that if nothing has ever been copied
                # the spectrum gets copied
                new_spectra = True
                partial_copy = False
                if new_folder_path.exists() is True:
                    logging.info("Spectrum already exists in destination")
                    comparison = filecmp.dircmp(folder, new_folder_path)
                    if len(comparison.left_only) == 0:
                        new_spectra = False
                    elif len(comparison.left_only) > 0:
                        partial_copy = True
                        logging.info("but only a partial copy")
                # Only copy if new spectra in folder
                if new_spectra is True:
                    if partial_copy is True:
                        for cont_folder in contents_list:
                            new_spectrum_path = new_folder_path / cont_folder.name
                            if new_spectrum_path.exists() is False:
                                try:
                                    shutil.copytree(cont_folder, new_spectrum_path)
                                except PermissionError:
                                    output_list.append(
                                        "you do not have permission to write to the given folder"
                                    )
                                    return output_list
                        text_to_add = "spectra found: " + new_folder_name
                        output_list.append(text_to_add)
                    else:
                        try:
                            shutil.copytree(folder, new_folder_path)
                        except PermissionError:
                            output_list.append(
                                "you do not have permission to write to the given folder"
                            )
                            return output_list
                        text_to_add = "spectra found: " + new_folder_name
                        output_list.append(text_to_add)
                    logging.info(f"Spectrum saved to {new_folder_path}")
                # Make progress bar move noticeably while checking/copying users' spectra
                # so it doesn't look like it has crashed
                max_progress += 20
                prog_bar.setMaximum(max_progress)
                prog_state += 20
                progress_callback.emit(prog_state)
            # Update progress bar
            prog_state += 1
            progress_callback.emit(prog_state)
    now = datetime.now().strftime("%H:%M:%S")
    completed_statement = f"check of {check_day} completed at " + now
    output_list.append(completed_statement)
    logging.info(completed_statement)
    return output_list
