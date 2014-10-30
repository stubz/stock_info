use stock;
drop table if exists stockMasterMSN;
create table stockMasterMSN
(
 stockcd  varchar(5) not null,
 stocknm  varchar(30)    null,
 gyoshucd varchar(2)     null,
 stockGyoshu varchar(20)   null,
 marketnm varchar(20)    null,
 primary key (stockcd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
