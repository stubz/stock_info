use stock_db;
drop table if exists stockShihyoHist;
create table stockShihyoHist
(
 validDate  date not null,
 stockCode  varchar(5) not null,
 marketCode varchar(2) not null,
 kabusu     bigint null,
 dps        float null,
 eps				float null,
 bps				float null,
 tangen     int   null,
 primary key(validDate, stockCode, marketCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists stockShihyo;
create table stockShihyo
(
 stockCode  varchar(5) not null,
 marketCode varchar(2) not null,
 kabusu     bigint null,
 dps        float null,
 eps				float null,
 bps				float null,
 tangen     int   null,
 primary key(stockCode, marketCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

