import os

import allure
import openpyxl
import pytest

from common.client import RequestsClient
from common.testcase_util import get_all_testcases, get_variables, get_api_default_params, regx_sub_data, \
    update_value_to_json

wb = openpyxl.load_workbook('testcases/CRM系统接口测试用例.xlsx')
# 获取所有的测试用例数据
test_data = get_all_testcases(wb)
# print(test_data)
variables = get_variables(wb)  # 获取所有的公共变量，也用来存储测试过程中产生的动态变量
print(variables)
api_default_params = get_api_default_params(wb)  # 获取所有接口的默认参数数据


@pytest.mark.parametrize('suite_name,case_name,case_info_list', test_data)
def test_run(suite_name, case_name, case_info_list):
    # 创建一个接口调用的对象
    client = RequestsClient()
    allure.dynamic.feature(suite_name)  # 测试报告上会高于测试用例的层级展示
    allure.dynamic.title(case_name)  # 测试报告上表示测试用例的名称
    # case_info_list 是多个接口的数据，是一个列表
    for case_info in case_info_list:
        # case_info 其实也是一个列表，表示excel某一行的测试数据，从接口名称开始往后
        # ['登录', '${host}/login', 'post', '', '', '{\n"token":"$.Admin-Token"\n}', 200, '[\n{\n"actual":"$.code",\n"expect":0\n}\n]']
        kwargs = {'verify': False}  # verify表示忽略https的证书
        api_name = case_info[0]  # 接口名称
        url = case_info[1]  # 接口
        print(url)
        url = regx_sub_data(url, variables)  # 处理url中的动态变量及动态函数调用
        method = case_info[2]  # 接口请求方式
        headers = case_info[3]  # 接口头信息
        print(url)


if __name__ == '__main__':
    pass
    # test_run()
