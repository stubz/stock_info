use stock;
drop table if exists stockETFMaster;
create table stockETFMaster
(
 stockcd  char(4)      not null,
 marketcd varchar(2)   not null,
 marketnm varchar(20)      null,
 stocknm  varchar(50)      null,
 benchmark varchar(50)     null,
 primary key (stockcd, marketcd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
 
load data infile "/Users/popopopo/myWork/stock_info/data/ETFList_unix.csv" into table stockETFMaster
fields terminated by ',' lines terminated by '\n'
ignore 1 lines;
