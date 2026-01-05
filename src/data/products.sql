create table products (
  id bigint generated always as identity primary key,
  name text not null,
  price numeric(10,2) not null,
  description text,
  image text
);
