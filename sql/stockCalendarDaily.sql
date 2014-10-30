use stock;
drop table if exists calendarDaily;
create table calendarDaily
(
 date date not null,
 primary key(date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
