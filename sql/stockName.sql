use stock_db;
drop table if exists stockName;
create table stockName
(
 stockcd char(4)      not null,
 stocknm varchar(100) not null,
 primary key (stockcd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
 
