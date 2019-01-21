import sqlite3
from geoip import open_database


class Log_Parser:
    
    db_name = 'my_test.db'

    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()
        self.ipdb = open_database('GeoLite2-Country.mmdb') # открытая база данных ip адресов

        self.logs = list()
        self.users = set()
        self.orders = set()
        self.current_categories = dict()

        self.init_design()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def init_design(self):
        with open('my_design.sql') as s:
            self.cur.executescript(s.read())

    def extract_log_lines(self):
        with open('logs.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.split()
                url = line[7][line[7].find('/', 8)+1:]
                self.logs.append((line[2], line[3], line[6], url))

    def parse(self):
        self.extract_log_lines()

        for log in self.logs:
            if log[2] not in self.users:
                self.create_user(log[2])
                self.users.add(log[2])

            self.fill_action(log)

    def create_user(self, ip):
        self.cur.execute("INSERT INTO {0}({1},{2}) VALUES (?, ?);".format('users', 'ip', 'country_code'),
                         (ip, self.country_code_by_ip(ip)))
        self.conn.commit()

    def country_code_by_ip(self, ip):
        res = self.ipdb.lookup(ip)

        country = None
        try:
            country = res.country
        except:
            pass

        return country

    def fill_action(self, log):
        category = None
        if not log[3]:
            action = 'main'
        elif 'cart?' in log[3]:
            action = 'add_to_cart'
            order_id = int(((log[3]).split('&')[2])[8:])
            goods_id = int(((log[3]).split('&')[0])[14:])
            amount = int(((log[3]).split('&')[1])[7:])
            if order_id not in self.orders:
                self.create_order(log[2], order_id)
                self.orders.add(order_id)

            self.create_order_item((order_id, goods_id, amount, self.current_categories[log[2]]))
        elif 'pay?' in log[3]:
            action = 'pay'
        elif 'success_pay' in log[3]:
            action = 'payed'
            order_id = int((log[3])[12:-1])
            self.pay_order(order_id)
        else:
            action = 'category'
            category = str(log[3])
            self.current_categories[log[2]] = category

        self.create_action((str(log[2]), str(log[0]), str(log[1]), action, category))



    def create_action(self, action):
        self.cur.execute('''
            INSERT INTO {0}({1},{2},{3},{4},{5}) VALUES (?, ?, ?, ?, ?);
        '''.format('actions', 'ip', 'date', 'time', 'action_type', 'product_category'), action)

        self.conn.commit()

    def create_order(self, ip, order_id):
        self.cur.execute('''
            INSERT INTO {0}({1},{2}) VALUES (?, ?);
        '''.format('orders', 'id', 'ip'), (order_id, ip))

        self.conn.commit()

    def pay_order(self, order_id):
        self.cur.execute('''
             UPDATE {0} SET {1} = (?) WHERE {2} = (?);
        '''.format('orders', 'is_paid', 'id'), (1, order_id))

        self.conn.commit()

    def create_order_item(self, order_item):
        self.cur.execute('''
                    INSERT INTO {0}({1},{2},{3},{4}) VALUES (?, ?, ?, ?);
                '''.format('order_items', 'order_id', 'product_id', 'amount', 'product_category'), order_item)

        self.conn.commit()




parser = Log_Parser('logs.txt')
parser.parse()
