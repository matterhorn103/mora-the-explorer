import datetime

from mora_the_explorer.core import (
    MetadataRules,
    MeasurementMetadata,
    Manufacturer,
)


BRUKER_RULES = MetadataRules(
    {"group": "stu", "user": "mjm"},
    r"<group>\_*<user>\_*(sample_info)",
    ["user", "sample_info", "experiment", "solvent"],
)
AGILENT_RULES = MetadataRules(
    {"user": "mjm"},
    r"<user>(sample_info)",
    ["user", "sample_info", "experiment", "solvent"],
)


class TestRules:

    def test_pattern_processing(self):
        assert BRUKER_RULES.pattern() == (
            r"(?P<group>stu)(?:[\s_-]*)(?P<user>mjm)(?:[\s_-]*)(?P<sample_info>.*)"
        )


class TestMetadata:

    def test_bruker_title_extraction(self):
        title = "stu mjm 213-4 repeat"
        metadata = MeasurementMetadata.from_title(title, BRUKER_RULES)
        assert metadata == MeasurementMetadata(
            group="stu",
            user="mjm",
            sample_info="213-4 repeat",
            title=title,
        )

    def test_bruker_name_gen(self):
        metadata = MeasurementMetadata(group="stu", user="mjm", sample_info="213-4 repeat")
        metadata.manufacturer = Manufacturer.BRUKER
        metadata.date = datetime.date.today()
        name = metadata.generate_folder_name(BRUKER_RULES)
        assert name == "mjm-213-4-repeat"

    def test_agilent_title_extraction(self):
        title = "mjm304-1-ß"
        metadata = MeasurementMetadata.from_title(title, AGILENT_RULES)
        assert metadata == MeasurementMetadata(
            user="mjm",
            sample_info="304-1-ß",
            title=title,
        )

    def test_agilent_name_gen(self):
        metadata = MeasurementMetadata(user="mjm", sample_info="304-1-ß")
        name = metadata.generate_folder_name(AGILENT_RULES)
        assert name == "mjm-304-1-0xdf"
    
    def test_no_rules_mutation(self):
        # This is related to the bug tested by `TestExplorer.test_agilent_inconsistent_match_bug()`
        # Only the first of these four was being properly parsed to give user = "akw",
        # because the pattern was being mutated with each use of the rules
        titles = [
            "akw004-4",
            "akw017-3",
            "akw032-2-1",
            "akw17-4",
        ]
        rules = MetadataRules(
            {"user": "akw"},
            r"<user>",
            ["user", "sample_info", "experiment", "solvent"],
        )
        for title in titles:
            metadata = MeasurementMetadata.from_title(title, rules)
            assert metadata.user == "akw"
