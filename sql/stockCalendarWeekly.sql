use stock;
drop table if exists calendarWeekly;
create table calendarWeekly
(
 date date not null,
 primary key(date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
