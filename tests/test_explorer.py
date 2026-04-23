from datetime import date

from . import mock_explorer


class TestExplorer:
    def test_init(self):
        explorer = mock_explorer()
        assert len(explorer.config.specs) > 0

    def test_single_check_no_copy(self):
        # Check that a single check executes without issue
        explorer = mock_explorer()
        # Use a fictitious user so we don't match anything
        explorer.config.options.user = "aaa"
        reporter = explorer.single_check(date(2023, 10, 16))
        # Nothing should have been found, should only be a single "check finished" message
        assert len(reporter.copied()) == 0
        assert len(reporter.messages()) == 1

    def test_single_check_with_copy(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert len(reporter.copied()) == 1
        assert reporter.copied() == ["mjm-500-1-cdcl3-proton"]
        assert reporter.messages()[0] == "Spectrum found: mjm-500-1-cdcl3-proton"

    def test_400er_checks_300er(self):
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

    def test_with_group(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.group = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["stu-mjm-500-1-cdcl3-proton"]

    def test_no_initials(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.user = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["500-1-cdcl3-proton"]

    def test_no_solvent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.solvent = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["mjm-500-1-proton"]

    def test_no_experiment(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.experiment = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["mjm-500-1"]

    def test_with_freq(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.frequency = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["mjm-500-1-300-proton"]
        # Note that only that specific spectrum has the uxnmr.info file in the mock server setup
        reporter = explorer.single_check(date(2023, 10, 16))
        # Whereas these ones don't, so all have the frequency as unknown
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
        assert reporter.copied() == [
            "mjm-500-1-cdcl3-various",
            "mjm-501-1-dmso-various",
        ]

    def test_agilent_with_freq(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.frequency = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied() == [
            "mjm-500-1-600-various",
            "mjm-501-1-600-various",
        ]
    
    def test_agilent_with_group(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.naming.solvent = False
        explorer.config.options.naming.frequency = True
        explorer.config.options.naming.group = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied() == [
            "studer-mjm-500-1-600-various",
            "studer-mjm-501-1-600-various",
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
        explorer.config.options.naming.experiment = False
        reporter = explorer.single_check(date(2026, 4, 10))
        assert sorted(reporter.copied()) == [
            "akw-004-4",
            "akw-017-3",
            "akw-032-2-1",
            "akw-17-4",
        ]
    
    def test_bruker_missing_title(self):
        # Make sure there's not an issue if there is no measurement title
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.user = "xyz"
        reporter = explorer.single_check(date(2023, 10, 17))
        # No spectra should be found, and there should also be no error
        assert len(reporter.copied()) == 0
