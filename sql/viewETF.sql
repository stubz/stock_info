use stock;

create or replace view priceDailyETFView as
select 
 a.date,
 a.stockcd,
 a.marketcd,
 a.open,
 a.high,
 a.low,
 a.close,
 a.volume
from priceDaily a
inner join stockETFMaster b
on a.stockcd = b.stockcd and a.marketcd = b.marketcd

