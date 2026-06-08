from datetime import date

from . import mock_explorer


class TestExplorer:
    def test_init(self):
        explorer = mock_explorer()
        assert len(explorer.config.specs) > 0

    def test_bruker_single_check_no_copy(self):
        # Check that a single check executes without issue
        explorer = mock_explorer()
        # Use a fictitious user so we don't match anything
        explorer.config.options.user = "aaa"
        reporter = explorer.single_check(date(2023, 10, 16))
        # Nothing should have been found, should only be a single "check finished" message
        assert len(reporter.copied()) == 0
        assert len(reporter.messages()) == 1

    def test_bruker_single_check_with_copy(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert len(reporter.copied()) == 1
        assert sorted(reporter.copied()) == ["mjm-500-1_av300_151023_300k_proton_200"]
        assert reporter.messages()[0] == "Spectrum found: mjm-500-1_av300_151023_300k_proton_200"

    def test_bruker_400er_checks_300er(self):
        # Check that checking the neo400 also checks the av300
        explorer = mock_explorer()
        explorer.config.options.spec = "neo400"
        reporter = explorer.single_check(date(2023, 10, 15))
        # The spectrum should be found three times but determined to be different spectra
        # (both because the instrument is different or because the FIDs are different),
        # all copied, and automatically named as different measurements
        assert sorted(reporter.copied()) == [
            "mjm-500-1_av300_151023_300k_proton_200",
            "mjm-500-1_neo400a_151023_300k_proton_200",
            "mjm-500-1_neo400b_151023_300k_proton_200",
        ]

    def test_agilent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        reporter = explorer.single_check(date(2023, 10, 15))
        # Note that only these two sets of spectra have a populated `procpar` file
        # as required for the metadata extraction, and only the proton spectra have it
        assert sorted(reporter.copied()) == [
            "mjm-500-1_v600_151023_299k_13c_1",  # "mjm-500-1-cdcl3-13c",
            "mjm-500-1_v600_151023_299k_1h_1",  # "mjm-500-1-cdcl3-1h",
            "mjm-500-1_v600_151023_299k_gcosy_1",  # "mjm-500-1-cdcl3-gcosy",
            "mjm-501-1_v600_151023_299k_13c_1",  # "mjm-501-1-dmso-13c",
            "mjm-501-1_v600_151023_299k_1h_1",  # "mjm-501-1-dmso-1h",
            "mjm-501-1_v600_151023_299k_gcosy_1",  # "mjm-501-1-dmso-gcosy",
        ]

    def test_agilent_inconsistent_match_bug(self):
        # This tests the bug identified by Klaus 2026-04-10
        # The problem arises when individual spectra have an empty `text` file,
        # from which the frequency is extracted
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.user = "akw"
        explorer.config.options.group = "gil"
        reporter = explorer.single_check(date(2026, 4, 10))
        assert sorted(reporter.copied()) == [
            "akw-004-4_s600_300326_299k_13c_1",
            "akw-004-4_s600_300326_299k_1h_1",
            "akw-004-4_s600_300326_299k_gcosy_1",
            "akw-004-4_s600_300326_299k_ghmbcad_1",
            "akw-004-4_s600_300326_299k_ghsqcad_1",
            "akw-017-3_v500_230326_299k_19f-bb-hdec_1",
            "akw-017-3_v500_230326_299k_1h-bb-fdec_1",
            "akw-017-3_v500_230326_299k_1h_1",
            "akw-017-3_v500_240326_299k_13c-hfdec_1",
            "akw-032-2-1_s600_070426_299k_13c-hfdec_1",
            "akw-032-2-1_s600_070426_299k_19f-bb-hdec_1",
            "akw-032-2-1_s600_070426_299k_1h-bb-fdec_1",
            "akw-032-2-1_s600_070426_299k_1h_1",
            "akw-032-2-1_s600_080426_299k_gcosy_1",
            "akw-032-2-1_s600_080426_299k_ghmbcad_1",
            "akw-032-2-1_s600_080426_299k_ghsqcad_1",
            "akw-17-4_s600_260326_299k_13c-hfdec_1",
            "akw-17-4_s600_260326_299k_19f-bb-hdec_1",
            "akw-17-4_s600_260326_299k_1h-bb-fdec_1",
            "akw-17-4_s600_260326_299k_1h_1",
            "akw-17-4_s600_260326_299k_gcosy_1",
            "akw-17-4_s600_270326_299k_ghmbcad_1",
            "akw-17-4_s600_270326_299k_ghsqcad_1",
        ]

    def test_bruker_missing_title(self):
        # Make sure there's not an issue if there is no measurement title
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.user = "xyz"
        reporter = explorer.single_check(date(2023, 10, 17))
        # No spectra should be found, and there should also be no error
        assert len(reporter.copied()) == 0

    def test_files_and_non_measurements(self):
        # Make sure that if the spectrometer directory contains files as well as
        # measurement subdirectories, or subdirectories that aren't for
        # measurements, everything copes and no error occurs
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        reporter = explorer.single_check(date(2023, 10, 14))
        # No spectra should be found, and there should also be no error
        assert len(reporter.copied()) == 0
