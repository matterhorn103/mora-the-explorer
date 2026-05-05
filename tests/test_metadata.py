import datetime

from mora_the_explorer.core import (
    MetadataRules,
    MeasurementMetadata,
    MatchValues,
)

SUBSTITUTIONS = MatchValues(
    group="stu",
    group_name="studer",
    user="mjm",
    user_name="milner",  # Doesn't matter what this is since we won't require it anyway
    sample_id="",        # Same applies here
)

SAMPLE_FORMAT = "{user}-{sample_id}"
MEASUREMENT_FORMAT = "{user}-{sample_id}_{instrument}_{completion_time:%d%m%y}_{temperature}k_{experiment}_{measurement_no}"

BRUKER_RULES = MetadataRules(
    values=SUBSTITUTIONS,
    sample_pattern=None,
    measurement_pattern=r'<group!>\_*<user_name>?\_*<user!>\_*<sample_id>',
    sample_format=SAMPLE_FORMAT,
    measurement_format=MEASUREMENT_FORMAT,
)
AGILENT_RULES = MetadataRules(
    values=SUBSTITUTIONS,
    sample_pattern=r'<user!><sample_id>',
    measurement_pattern=r'<user!><sample_id>\_(\d{6})\_(\d{3}k)\_(.+)_\d\.fid',
    sample_format=SAMPLE_FORMAT,
    measurement_format=MEASUREMENT_FORMAT,
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

    def test_sample_name_gen(self):
        metadata = MeasurementMetadata(group="stu", user="mjm", sample_id="213-4")
        name = metadata.generate_folder_name(SAMPLE_FORMAT)
        assert name == "mjm-213-4"

    def test_sample_name_gen_disallowed_chars(self):
        metadata = MeasurementMetadata(user="mjm", sample_id="304-1-ß repeat")
        name = metadata.generate_folder_name(SAMPLE_FORMAT)
        # Spaces should be normalized to underscores
        # Characters outside of [a-zA-Z0-9-] should be normalized to hexadecimal Unicode code points
        assert name == "mjm-304-1-0xdf_repeat"

    def test_measurement_name_gen(self):
        metadata = MeasurementMetadata(
            completion_time=datetime.datetime(2026, 3, 23),
            sample_id="17-4",
            user="akw",
            user_name=None,
            group="gil",
            group_name="gilmour",
            experiment="1h",
            instrument="neo400a",
            frequency=300.26,
            solvent="CDCl3",
            temperature=299,
            measurement_no=260,
        )
        name = metadata.generate_folder_name(MEASUREMENT_FORMAT)
        assert name == "akw-17-4_neo400a_230326_299k_1h_260"

    def test_bruker_title_extraction(self):
        title = "stu mjm 213-4 repeat"
        metadata = MeasurementMetadata.from_measurement_title(title, BRUKER_RULES)
        assert metadata == MeasurementMetadata(
            group="stu",
            user="mjm",
            sample_id="213-4 repeat",
            title=title,
        )

    def test_agilent_title_extraction(self):
        title = "mjm500-1_151023_299k_1h_1.fid"
        metadata = MeasurementMetadata.from_measurement_title(title, AGILENT_RULES)
        assert metadata == MeasurementMetadata(
            user="mjm",
            sample_id="500-1",
            title=title,
        )
    
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
            MatchValues(
                group="",
                group_name="",
                user="akw",
                user_name="",
                sample_id="",
            ),
            r'<user!><sample_id>',
            r'<user!><sample_id>',
            SAMPLE_FORMAT,
            MEASUREMENT_FORMAT,
        )
        for title in titles:
            metadata = MeasurementMetadata.from_measurement_title(title, rules)
            assert metadata.user == "akw"
