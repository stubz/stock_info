use stock;
/*
 * table of all Monthly data, including those that are already delisted.
 */
drop table if exists priceMonthlyRaw;
create table priceMonthlyRaw
(
 date     date       not null,
 stockcd  char(4)    not null,
 marketcd varchar(2) not null,
 open     float          null,
 high     float          null,
 low      float          null,
 close    float          null,
 volume   bigint unsigned null,
 primary key(date, stockcd, marketcd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
