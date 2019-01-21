import sqlite3

conn = sqlite3.connect('my_test.db')
cur = conn.cursor()

print('1. Посетители из какой страны совершают больше всего действий на сайте')
cur.execute("""
    SELECT country_code, count(*) as cnt
    FROM actions a left join users u on a.ip = u.ip
    GROUP BY country_code
    ORDER BY count(country_code) DESC
    limit 5
""")
print(cur.fetchall())


print('2. Посетители из какой страны чаще всего интересуются товарами из категории "semi_manufactures/"')
cur.execute("""
    SELECT country_code, count(*) as cnt
    FROM actions a left join users u on a.ip = u.ip
    WHERE 
        a.product_category = 'semi_manufactures/'
        and a.action_type = 'category'
    GROUP BY country_code
    ORDER BY count(country_code) DESC
    limit 5
""")
print(cur.fetchall())



print('3. Сколько не оплаченных корзин?')
cur.execute('''
    SELECT count(*) from orders where is_paid = 0
''')
print(cur.fetchone())


print('4. Какое количество пользователей совершали повторные покупки?')
cur.execute('''
    SELECT count(*) from (
        select ip
        from orders 
        where 
            is_paid = 1
        group by ip
        having count(*) > 1
    )
''')
print(cur.fetchone())
