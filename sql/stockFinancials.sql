use stock_db;
drop table if exists stockFinancialsIndependent;
create table stockFinancialsIndependent
(
 year       char(4)    not null,
 stockCode  varchar(5) not null,
 marketCode varchar(2) not null,
 uriage     long  null,
 eigyorieki long  null,
 keijorieki long  null,
 toukirieki long  null,
 eps				float null,
 adjeps     float null,
 dps        float null,
 bps				float null,
 kabusu     long  null,
 soushisan  long  null, 
 jikoshihon long  null,
 shihonkin  long  null,
 debt       long null,
 kurikoshisonneki long null,
 capital_ratio long null,
 fukumieki  long  null,
 roa        float null,
 roe        float null,
 riekiritsu float null,
 primary key(year, stockCode, marketCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists stockFinancialsConsolidate;
create table stockFinancialsConsolidate
(
 year       char(4)    not null,
 stockCode  varchar(5) not null,
 marketCode varchar(2) not null,
 uriage     long  null,
 eigyorieki long  null,
 keijorieki long  null,
 toukirieki long  null,
 eps				float null,
 adjeps     float null,
 bps				float null,
 soushisan  long  null, 
 jikoshihon long  null,
 shihonkin  long  null,
 debt       long null,
 capital_ratio long null,
 fukumieki  long  null,
 roa        float null,
 roe        float null,
 riekiritsu float null,
 primary key(year, stockCode, marketCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists stockFinancialsInterim;
create table stockFinancialsInterim
(
 year       char(4)    not null,
 stockCode  varchar(5) not null,
 marketCode varchar(2) not null,
 uriage     long  null,
 eigyorieki long  null,
 keijorieki long  null,
 toukirieki long  null,
 eps				float null,
 bps				float null,
 soushisan  long  null, 
 jikoshihon long  null,
 shihonkin  long  null,
 debt       long null,
 capital_ratio long null,
 primary key(year, stockCode, marketCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
