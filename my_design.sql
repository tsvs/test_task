drop table if exists hits;
CREATE TABLE actions (
    id integer PRIMARY KEY,
    ip text NOT NULL,
    date text not null,
    time text not null,
    action_type text not null,
    product_category text,
    FOREIGN KEY (ip) REFERENCES users(ip)
);

drop table if exists orders;
CREATE TABLE orders (
    id integer PRIMARY KEY,
    ip text NOT NULL,
    is_paid integer default 0,
    FOREIGN KEY (ip) REFERENCES users(ip)
);

drop table if exists order_items;
CREATE TABLE order_items (
    id integer PRIMARY KEY,
    order_id integer NOT NULL,
    product_id integer not null,
    amount integer not null,
    product_category text not null,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

drop table if exists users;
create table users (
    ip text primary key not null,
    country_code text
);