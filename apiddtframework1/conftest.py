from typing import List


def pytest_collection_modifyitems(items: List["Item"]):
    # item表示每个测试用例，解决用例名称中文显示问题
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode-escape")
        # item.name = item.name.split('-')[0]
        item._nodeid = item._nodeid.encode("utf-8").decode("unicode-escape")
