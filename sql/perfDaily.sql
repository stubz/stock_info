use stock;
/*
drop table if exists perfDaily;
*/

create table perfDaily
(
 	date        date not null,
	stockcd   varchar(5) not null,
	marketcd  varchar(2) not null,
	ret         float          null,
	logret      float          null,
	ret3mon     float          null,
	volat3mon   float          null,
	ret6mon     float          null,
	volat6mon   float          null,
	ret1year    float          null,
	volat1year  float          null,
	ret3year    float          null,
	volat3year  float          null,
	ret5year    float          null,
	volat5year  float          null,
	primary key ( date, stockcd, marketcd )
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
