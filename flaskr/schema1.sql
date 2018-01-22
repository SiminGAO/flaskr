drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title string not null,
  number integer not null,
  year integer not null
);