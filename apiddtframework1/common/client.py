import logging

import jsonpath

import requests

session = requests.session()


class RequestsClient:

    def __init__(self):
        self.logger = logging.getLogger(__class__.__name__)

    def send(self, url, method, **kwargs):
        self.logger.info(f'接口地址是:{url}')
        self.logger.info(f'接口请求方式是:{method}')
        for key, value in kwargs.items():
            self.logger.info(f'接口的{key}是:{value}')
        try:
            self.resp = session.request(url=url, method=method, **kwargs)
            self.logger.info(f'接口响应状态码是:{self.resp.status_code}')
            self.logger.info(f'接口响应信息是:{self.resp.text}')
        except BaseException as e:
            self.logger.exception('接口发起异常')
            raise BaseException(f'接口发起异常:{e}')
        return self.resp

    # 针对jsonpath的数据提取封装一个方法
    # 第一个参数指的是你要匹配的数据的jsonpath表达式
    # 第二个指的是你想返回匹配到的第几个，默认是0返回第一个
    def extract_resp(self, json_path, index=0):
        # 注意有的接口是没有返回信息的，返回信息是空的
        text = self.resp.text  # 获取返回信息的字符串形式
        if text != '':
            resp_json = self.resp.json()  # 获取响应信息的json格式
            # 如果能匹配到值，那么res就是个列表
            # 如果匹配不到res就是个False
            res = jsonpath.jsonpath(resp_json, json_path)
            if res:
                if index < 0:
                    # 如果index小于0 ，我认为你要匹配到的所有结果
                    self.logger.info(f'通过{json_path}提取到的结果是:{res}')
                    return res
                else:
                    self.logger.info(f'通过{json_path}提取到的结果是:{res[index]}')
                    return res[index]
            else:
                self.logger.warning(f'通过{json_path}没有提取到结果')
                return res
        else:
            self.logger.exception('接口返回信息为空，无法提取')
            raise BaseException('接口返回信息为空，无法提取')


if __name__ == '__main__':
    client = RequestsClient()
    cs = client.send(url='http://82.156.74.26:9099/login',
                method='post',
                data={'username': '18866668888', 'password': '123456'})
    print(client.extract_resp('Admin-Token'))
