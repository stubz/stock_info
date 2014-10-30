use stock;
/*
drop table if exists priceChangeMonthly;
*/
create table priceChangeMonthly
(
 date     date       not null,
 stockcd  char(4)    not null,
 marketcd varchar(2) not null,
 ret      float       null,
 logret   float          null,
 primary key(date, stockcd, marketcd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
