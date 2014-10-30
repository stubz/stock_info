use stock;

create or replace view viewLatestDate as
(select 'perfDaily' as tablename, max(date) as latestdate from perfDaily)
union
(select 'perfWeekly' as tablename, max(date) as latestdate from perfWeekly)
union
(select 'perfMonthly' as tablename, max(date) as latestdate from perfMonthly)
union
(select 'priceChangeDaily' as tablename, max(date) as latestdate from priceChangeDaily)
union
(select 'priceChangeWeekly' as tablename, max(date) as latestdate from priceChangeWeekly)
union
(select 'priceChangeMonthly' as tablename, max(date) as latestdate from priceChangeMonthly)
union
(select 'priceDaily' as tablename, max(date) as latestdate from priceDaily)
union
(select 'priceWeekly' as tablename, max(date) as latestdate from priceWeekly)
union
(select 'priceMonthly' as tablename, max(date) as latestdate from priceMonthly)

