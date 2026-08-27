import psycopg

conn = psycopg.connect(
    dbname="New_examdb",
    user="postgres",
    password="Piyrw12345",
    host='127.0.0.1',
    port=5432
)

cursor = conn.cursor()

def create_table():
    cursor.execute('''
create table if not exists users(
id serial,
tg_id bigint unique,
username varchar(32),
fullname varchar(255) not null,
cr_at timestamp default current_timestamp
);

create table if not exists products( 
id serial primary key,
title varchar(55) not null,
description text,
price int not null,
product_code varchar(50) unique not null,
photo varchar(255)
);

create table if not exists cart(
id serial primary key,
users_tg_id bigint references users(tg_id),
product_id int references products(id), 
quantity int default 1 
);


    create table if not exists orders(
    id serial primary key,
    users_tg_id bigint references users(tg_id),
    product text,
    all_price int,
    status varchar(30) default 'new',
    create_at timestamp default current_timestamp
    );

''')
    
    conn.commit()

def add_user(tg_id,username,fullname):
    try:
        cursor.execute("insert into users(tg_id,username,fullname) values (%s,%s,%s);",
            (int(tg_id),username,fullname),)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

        

def add_product(title,description,price,product_code,photo):
    cursor.execute('insert into products(title,description,price,product_code,photo) values (%s,%s,%s,%s,%s);',
       (title,description,price,product_code,photo),
    )
    conn.commit()

def get_users(admin_id):
    cursor.execute('''select users.tg_id , users.username , count(cart.users_tg_id) as zakaz_count from users 
    left join cart 
    on users.tg_id = cart.users_tg_id
    where users.tg_id != %s
    group by users.tg_id, users.username''',(admin_id,))
    return cursor.fetchall()

def get_products():
    cursor.execute("""select id, title, description, price, product_code, photo from products""")
    return cursor.fetchall()

def update_product(title, description, price, product_code, photo,product_id):
    cursor.execute("""
    update products 
    set title = %s,
    description = %s,
    price = %s,
    product_code = %s,
    photo = %s
    where id = %s""",(title, description, price, product_code, photo,product_id))

    conn.commit()

def delete_product(product_id):
    cursor.execute("""
    delete from products
    where id = %s
    """,(product_id,))

    conn.commit()

def check_user_blocked(user_id):
    try:
        cursor.execute("select blocked from users where tg_id = %s and blocked = 'true';", (user_id,))
        resultat = cursor.fetchone()
        if resultat is not None:
            return True
        return False
    except:
        conn.rollback()
        return False


def set_user_block_status(user_id, status):
    cursor.execute(
        "update users set blocked = %s where tg_id = %s;", (status, user_id))
    conn.commit()

def check_product_code(code):
    cursor.execute(
        "select id, title, description, price, product_code, photo from products where product_code = %s;", 
        (code,)
    )
    return cursor.fetchall()

def add_cart(user_id, product_id):
        cursor.execute(
            "select id, quantity from cart where users_tg_id = %s and product_id = %s;",
            (user_id, product_id)
        )
        item = cursor.fetchone()

        if item:
            cursor.execute(
                "update cart set quantity = quantity + 1 where id = %s;",
                (item[0],)
            )
            return True
        else:
            cursor.execute(
                "insert into cart (users_tg_id, product_id, quantity) values (%s, %s, 1);",
                (user_id, product_id)
            )
            return True
        conn.commit()

def get_user_cart(user_id):
    try:
        cursor.execute('''
            select cart.id, products.title, products.price, cart.quantity
            from cart
            join products on cart.product_id = products.id
            where cart.users_tg_id = %s;
        ''', (user_id,))
        return cursor.fetchall()
    except:
        conn.rollback()
        return []

def delete_cart_item(cart_id):
    try:
        cursor.execute("delete from cart where id = %s;", (cart_id,))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def clear_cart(user_id):
    try:
        cursor.execute("delete from cart where users_tg_id = %s;", (user_id,))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def kol_zakaz(my_id):
    cursor.execute('select count(*) from cart where users_tg_id = %s',(int(my_id),),)
    result = cursor.fetchone()
    return result[0]