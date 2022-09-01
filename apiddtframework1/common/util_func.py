
import hashlib
import time

from faker import Faker

fake = Faker(locale='zh_CN')


def rdm_phone_number():
    return fake.phone_number()

def cur_timestamp():#到毫秒级的时间戳
    return int(time.time() * 1000)

def cur_date():# 2021-12-25
    return fake.date_between_dates()

def cur_date_time():# 2021-12-25 10:07:33
    return fake.date_time_between_dates()

def rdm_date(pattern='%Y-%m-%d'):
    return fake.date(pattern=pattern)

def rdm_date_time():
    return fake.date_time()

def rdm_future_date_time(end_date):
    return fake.future_datetime(end_date=end_date)

def md5(data):
    data = str(data)
    return hashlib.md5(data.encode('UTF-8')).hexdigest()
if __name__ == '__main__':
    print(rdm_phone_number())
    print(rdm_date())
    print(rdm_date_time())
    print(cur_date())
    print(cur_timestamp())
    print(cur_date_time())
    print(rdm_future_date_time('+60d'))
    print(md5('123456'))