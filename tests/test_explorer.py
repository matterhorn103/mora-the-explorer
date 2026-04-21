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
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert len(reporter.copied()) == 1
        assert reporter.copied() == ["mjm-500-1-proton-cdcl3"]
        assert reporter.messages()[0] == "Spectrum found: mjm-500-1-proton-cdcl3"

    def test_400er_checks_300er(self):
        # Check that checking the neo400 also checks the av300
        explorer = mock_explorer()
        explorer.config.options.spec = "neo400"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # The spectrum should be found twice but determined to be different spectra,
        # both copied, and automatically numbered as different measurements
        assert sorted(reporter.copied()) == [
            "mjm-500-1-proton-cdcl3",
            "mjm-500-1-proton-cdcl3-2",
        ]

    def test_no_initials(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.inc_user = False
        explorer.config.options.inc_solvent = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["500-1-proton-cdcl3"]

    def test_no_solvent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["mjm-500-1-proton"]

    def test_no_experiment(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        explorer.config.options.inc_experiment = False
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["mjm-500-1"]

    def test_with_freq(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        explorer.config.options.inc_frequency = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # A single spectrum, mjm-500-1, should be found
        assert reporter.copied() == ["mjm-500-1-proton-300"]
        # Note that only that specific spectrum has the uxnmr.info file in the mock server setup
        reporter = explorer.single_check(date(2023, 10, 16))
        # Whereas these ones don't, so all have the frequency as unknown
        print(reporter.copied())
        assert sorted(reporter.copied()) == [
            "mjm-501-1-proton-unknown",
            "mjm-501-2-carbon-unknown",
            "mjm-501-2-proton-unknown",
        ]

    def test_agilent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied() == ["mjm-500-1-various-cdcl3"]

    def test_agilent_with_freq(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        explorer.config.options.inc_frequency = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied() == ["mjm-500-1-various-600"]

    def test_agilent_inconsistent_match_bug(self):
        # This tests the bug identified by Klaus 2026-04-10
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.user = "akw"
        explorer.config.options.group = "gil"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        explorer.config.options.inc_frequency = False
        reporter = explorer.single_check(date(2026, 4, 10))
        assert sorted(reporter.copied()) == [
            "akw-004-4",
            "akw-017-3",
            "akw-17-4",
            "akw-032-2-1",
        ]
