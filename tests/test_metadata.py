import datetime
import re

from mora_the_explorer.core import (
    MetadataRules,
    MeasurementMetadata,
    Manufacturer,
    VariableSubstitutions,
)

SUBSTITUTIONS = VariableSubstitutions(
    group="stu",
    group_name="studer",
    user="mjm",
    user_name="milner",  # Doesn't matter what this is since we won't require it anyway
    sample_id="",        # Same applies here
)

BRUKER_RULES = MetadataRules(
    SUBSTITUTIONS,
    r'<group!>\_*<user_name>?\_*<user!>\_*<sample_id>',
    ["user", "sample_id", "experiment", "solvent"],
)
AGILENT_RULES = MetadataRules(
    SUBSTITUTIONS,
    r'<user!><sample_id>',
    ["user", "sample_id", "experiment", "solvent"],
)


class TestRules:

    def test_pattern_processing(self):
        processed = BRUKER_RULES.process_pattern(
            r'<group!>\_*<user_name>?\_*<user!>\_*<sample_id>'
        )
        print(processed)
        theoretical = (
            r'(?P<group>stu)(?:[\s_-]*)(?P<user_name>[^\s_-]+)?(?:[\s_-]*)(?P<user>mjm)(?:[\s_-]*)(?P<sample_id>.*)'
        )
        print(theoretical)
        assert processed == theoretical


class TestMetadata:

    def test_bruker_title_extraction(self):
        title = "stu mjm 213-4 repeat"
        metadata = MeasurementMetadata.from_measurement_title(title, BRUKER_RULES)
        assert metadata == MeasurementMetadata(
            group="stu",
            user="mjm",
            sample_id="213-4 repeat",
            title=title,
        )

    def test_bruker_name_gen(self):
        metadata = MeasurementMetadata(group="stu", user="mjm", sample_id="213-4 repeat")
        metadata.manufacturer = Manufacturer.BRUKER
        metadata.date = datetime.date.today()
        name = metadata.generate_folder_name(BRUKER_RULES)
        assert name == "mjm-213-4-repeat"

    def test_agilent_title_extraction(self):
        title = "mjm304-1-ß"
        metadata = MeasurementMetadata.from_measurement_title(title, AGILENT_RULES)
        assert metadata == MeasurementMetadata(
            user="mjm",
            sample_id="304-1-ß",
            title=title,
        )

    def test_agilent_name_gen(self):
        metadata = MeasurementMetadata(user="mjm", sample_id="304-1-ß")
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
            VariableSubstitutions(
                group="",
                group_name="",
                user="akw",
                user_name="",
                sample_id="",
            ),
            r'<user!><sample_id>',
            ["user", "sample_id", "experiment", "solvent"],
        )
        for title in titles:
            metadata = MeasurementMetadata.from_measurement_title(title, rules)
            assert metadata.user == "akw"
