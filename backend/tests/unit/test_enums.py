from backend.core.enums import Status


def test_status_values_match_db_values():
    assert Status.SUCCESS == 1
    assert Status.PARTIAL == 2
    assert Status.FAILURE == 3


def test_status_has_only_three_members():
    # 空白は status=0 ではなく「レコードなし」で表すため、Enumには含めない
    assert [status.name for status in Status] == ["SUCCESS", "PARTIAL", "FAILURE"]


def test_status_can_be_created_from_db_value():
    assert Status(1) is Status.SUCCESS
    assert Status(2) is Status.PARTIAL
    assert Status(3) is Status.FAILURE
