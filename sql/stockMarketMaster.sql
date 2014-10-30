use stock;
drop table if exists stockMarketMaster;
create table stockMarketMaster
(
 marketcd char(1)     not null,
 marketnm varchar(20) not null,
 primary key(marketcd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into stockMarketMaster (marketcd, marketnm)
values ('1','東証1部'),('2','東証2部'),('3','東証マザーズ'),('4','ジャスダック'),('6','大証1部'),('7','大証2部'),('8','ヘラクレス');
