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
print(test_data)
variables = get_variables(wb)  # 获取所有的公共变量，也用来存储测试过程中产生的动态变量
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
        var= variables
        print("----------")
        print(var)
        url = regx_sub_data(url, variables)  # 处理url中的动态变量及动态函数调用
        method = case_info[2]  # 接口请求方式
        headers = case_info[3]  # 接口头信息
        if headers != '':
            headers = regx_sub_data(headers, variables)
            headers = eval(headers)  # 将json格式的字符串转换成字典
            kwargs['headers'] = headers

        # 测试数据并不是接口发起时真正的全部参数，需要根据用户填入的要测试的数据和该接口对应的默认数据进行替换以及组合来达到
        # 请求数据
        api_default_param = api_default_params[api_name]  # 获取当前行的接口对应的默认数据
        if api_default_param != '':
            api_default_param = regx_sub_data(api_default_param, variables)
            api_default_param = eval(api_default_param)
        test_params = case_info[4]  # 测试数据
        if test_params != '':
            test_params = regx_sub_data(test_params, variables)
            test_params = eval(test_params)
            # 解析测试数据，通过jsonpath去替换默认参数中的数据
            # 逻辑是遍历测试数据，判断测试数据中是哪种参数类型(data/params/json/files),根据参数类型去替换默认数据的对应的部分
            if 'json' in test_params:
                """
                {
                    "$.entity.name":"联系人${{cur_timestamp()}}",
                }
                """
                for json_path, new_value in test_params['json'].items():
                    api_default_param['json'] = update_value_to_json(api_default_param['json'], json_path, new_value)
            if 'data' in test_params:
                for json_path, new_value in test_params['data'].items():
                    api_default_param['data'] = update_value_to_json(api_default_param['data'], json_path, new_value)
            if 'params' in test_params:
                for json_path, new_value in test_params['params'].items():
                    api_default_param['params'] = update_value_to_json(api_default_param['params'], json_path,
                                                                       new_value)
            if 'files' in test_params:
                for json_path, new_value in test_params['files'].items():
                    api_default_param['files'] = update_value_to_json(api_default_param['files'], json_path, new_value)
        test_params = api_default_param
        # 整合完成测试数据和默认数据之后，将他们分别存储kwargs中
        if 'json' in test_params:
            kwargs['json'] = test_params['json']
        if 'data' in test_params:
            kwargs['data'] = test_params['data']
        if 'params' in test_params:
            kwargs['params'] = test_params['params']
        if 'files' in test_params:
            kwargs['files'] = test_params['files']
        resp = client.send(url=url, method=method, **kwargs)  # 发起请求
        expect_status = case_info[6]  # 期望的响应状态码
        assert resp.status_code == expect_status
        # print(resp.text)
        extract_resp = case_info[5]  # 响应提取
        if extract_resp != '':
            extract_resp = eval(extract_resp)
            """
            {
            "token":"$.Admin-Token"
            }
            """
            for key, value in extract_resp.items():
                # key就是提取后要保存的变量名称
                # value是你要提取的目标字段对应的jsonpath表达式
                res = client.extract_resp(value)
                variables[key] = res

        expect_resp = case_info[7]  # 期望的响应信息
        if expect_resp != '':
            expect_resp = regx_sub_data(expect_resp, variables)
            expect_resp = eval(expect_resp)
            """
            [
                {
                "actual":"$.code",
                "expect":500,
                },
                {
                "actual":"$.msg",
                "expect":"产品编号已存在，请校对后再添加！",
                }
            ]
            """
            for expect_info in expect_resp:
                json_path = expect_info['actual']
                actual_res = client.extract_resp(json_path)
                expect_res = expect_info['expect']
                pytest.assume(actual_res == expect_res, f'期望是{expect_res},实际是{actual_res}')


if __name__ == '__main__':
    pytest.main()  # 该方法会自动扫描当前项目中的pytest.ini，根据其中的配置进行执行
    os.system('allure generate ./report/data -o ./report/html --clean')
    pass
