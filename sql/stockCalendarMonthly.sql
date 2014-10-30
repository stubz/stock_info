use stock;
drop table if exists calendarMonthly;
create table calendarMonthly
(
 date date not null,
 primary key(date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
