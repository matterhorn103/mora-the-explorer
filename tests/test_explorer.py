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
        assert sorted(reporter.copied()) == ["mjm-500-1-cdcl3-proton"]
        assert reporter.messages()[0] == "Spectrum found: mjm-500-1-cdcl3-proton"

    def test_bruker_multiple_same_sample(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.user = "dna"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.experiment = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # 1H, 13C, and 19F should be found for the same sample (dna-1370-1)
        assert sorted(reporter.copied()) == [
            "dna-1370-1-carbon",
            "dna-1370-1-f19cpd",
            "dna-1370-1-proton",
        ]
        # Now run without the experiment naming option, which means the spectra
        # all get the same theoretical name i.e. we have to disambiguate three spectra
        explorer.config.options.naming.experiment = False
        reporter = explorer.single_check(date(2023, 10, 15))
        assert sorted(reporter.copied()) == [
            "dna-1370-1",
            "dna-1370-1-2",
            "dna-1370-1-3",
        ]

    def test_bruker_400er_checks_300er(self):
        # Check that checking the neo400 also checks the av300
        explorer = mock_explorer()
        explorer.config.options.spec = "neo400"
        reporter = explorer.single_check(date(2023, 10, 15))
        # The spectrum should be found twice but determined to be different spectra,
        # both copied, and automatically numbered as different measurements
        assert sorted(reporter.copied()) == [
            "mjm-500-1-cdcl3-proton",
            "mjm-500-1-cdcl3-proton-2",
        ]

    def test_bruker_with_group(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.group = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert sorted(reporter.copied()) == ["stu-mjm-500-1-cdcl3-proton"]

    def test_bruker_no_initials(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.user = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert sorted(reporter.copied()) == ["500-1-cdcl3-proton"]

    def test_bruker_no_solvent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.solvent = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert sorted(reporter.copied()) == ["mjm-500-1-proton"]

    def test_bruker_no_experiment(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.experiment = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert sorted(reporter.copied()) == ["mjm-500-1"]

    def test_bruker_with_freq(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.frequency = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert sorted(reporter.copied()) == ["mjm-500-1-300mhz-proton"]
        # Note that only that specific spectrum has the uxnmr.info file in the mock server setup
        reporter = explorer.single_check(date(2023, 10, 16))
        # Whereas these ones don't, so all have the frequency as unknown
        print(reporter.copied())
        assert sorted(reporter.copied()) == [
            "mjm-501-1-unknown-proton",
            "mjm-501-2-unknown-carbon",
            "mjm-501-2-unknown-proton",
        ]

    def test_bruker_with_instrument(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.instrument = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert sorted(reporter.copied()) == ["mjm-500-1-av300-proton"]
        # Note that only that specific spectrum has the uxnmr.info file in the mock server setup
        reporter = explorer.single_check(date(2023, 10, 16))
        # Whereas these ones don't, so all have the instrument as unknown
        print(reporter.copied())
        assert sorted(reporter.copied()) == [
            "mjm-501-1-unknown-proton",
            "mjm-501-2-unknown-carbon",
            "mjm-501-2-unknown-proton",
        ]

    def test_agilent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        reporter = explorer.single_check(date(2023, 10, 15))
        # Note that only these two spectra have a populated `procpar` file as required
        # for the metadata extraction, and only the proton spectra have it
        assert sorted(reporter.copied()) == [
            "mjm-500-1-cdcl3-13c",
            "mjm-500-1-cdcl3-1h",
            "mjm-500-1-cdcl3-gcosy",
            "mjm-501-1-dmso-13c",
            "mjm-501-1-dmso-1h",
            "mjm-501-1-dmso-gcosy",
        ]

    def test_agilent_with_freq(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.frequency = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert sorted(reporter.copied()) == [
            "mjm-500-1-600mhz-13c",
            "mjm-500-1-600mhz-1h",
            "mjm-500-1-600mhz-gcosy",
            "mjm-501-1-600mhz-13c",
            "mjm-501-1-600mhz-1h",
            "mjm-501-1-600mhz-gcosy",
        ]
    
    def test_agilent_with_instrument(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.instrument = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert sorted(reporter.copied()) == [
            "mjm-500-1-v600-13c",
            "mjm-500-1-v600-1h",
            "mjm-500-1-v600-gcosy",
            "mjm-501-1-v600-13c",
            "mjm-501-1-v600-1h",
            "mjm-501-1-v600-gcosy",
        ]
    
    def test_agilent_with_group(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.instrument = True
        explorer.config.options.naming.group = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert sorted(reporter.copied()) == [
            "studer-mjm-500-1-v600-13c",
            "studer-mjm-500-1-v600-1h",
            "studer-mjm-500-1-v600-gcosy",
            "studer-mjm-501-1-v600-13c",
            "studer-mjm-501-1-v600-1h",
            "studer-mjm-501-1-v600-gcosy",
        ]

    def test_agilent_inconsistent_match_bug(self):
        # This tests the bug identified by Klaus 2026-04-10
        # The problem arises when individual spectra have an empty `text` file,
        # from which the frequency is extracted
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.user = "akw"
        explorer.config.options.group = "gil"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.frequency = False
        explorer.config.options.naming.experiment = True
        reporter = explorer.single_check(date(2026, 4, 10))
        assert sorted(reporter.copied()) == [
            "akw-004-4-13c",
            "akw-004-4-1h",
            "akw-004-4-gcosy",
            "akw-004-4-ghmbcad",
            "akw-004-4-ghsqcad",
            "akw-017-3-13c-hfdec",
            "akw-017-3-19f-bb-hdec",
            "akw-017-3-1h",
            "akw-017-3-1h-bb-fdec",
            "akw-032-2-1-13c-hfdec",
            "akw-032-2-1-19f-bb-hdec",
            "akw-032-2-1-1h",
            "akw-032-2-1-1h-bb-fdec",
            "akw-032-2-1-gcosy",
            "akw-032-2-1-ghmbcad",
            "akw-032-2-1-ghsqcad",
            "akw-17-4-13c-hfdec",
            "akw-17-4-19f-bb-hdec",
            "akw-17-4-1h",
            "akw-17-4-1h-bb-fdec",
            "akw-17-4-gcosy",
            "akw-17-4-ghmbcad",
            "akw-17-4-ghsqcad",
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
