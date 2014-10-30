use stock_db;
drop table if exists stockTurtle;
create table stockTurtle
(
 date                      date        not null,
 stockCode                 varchar(5)  not null,
 marketCode                char(1)     not null,
 TR                        float           null,
 Nvalue                    float           null,
 Low20                     float           null,
 High20                    float           null,
 Low55                     float           null,
 High55                    float           null,
 Low10                     float           null,
 High10                    float           null,
 primary key (date, stockCode, marketCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
 
