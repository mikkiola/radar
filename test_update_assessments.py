import update_assessments


def test_map_state_value_valid_passes_through():
    assert update_assessments._map_state_value("Growing") == "Growing"


def test_map_state_value_unrecognized_becomes_invalid():
    assert update_assessments._map_state_value("NotARealState") == "invalid"


def test_map_state_value_missing_is_none():
    assert update_assessments._map_state_value("") is None
