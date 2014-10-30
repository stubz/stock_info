use stock_db;
drop table if exists stockKessan;
create table stockKessan
(
 validDate                 date        not null,
 stockCode                 varchar(5)  not null,
 kessanki                  varchar(12) null,
 kessanHppyoubi            date        null,
 kessanTsukisu             int         null,
 uriage                    float       null,
 eigyoRieki                float       null,
 keijoRieki                float       null,
 toukiRieki                float       null,
 hitokabuToukiRieki        float       null,
 choseiHitokabuRieki       float       null,
 hitokabuJunshisan         float       null,
 soushisan                 float       null,
 jikoshihon                float       null,
 shihonkin                 float       null,
 yurishiFusai              float       null,
 jihoshihonHiritsu         float       null,
 fukumiSoneki              float       null,
 roa                       float       null,
 roe                       float       null,
 soushisanKeijouRiekiritsu float       null,
 primary key (validDate, stockCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
 
