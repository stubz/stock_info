set @a = 0;
set @yyyy = 2008;

select b.gyoshuCode, b.stockGyoshu, round(a.yyyymm/100,0) as yr, avg(a.asset/a.debt) as debtratio, avg((a.asset-a.debt)/a.asset) as equity_ratio, @a:=@a+1 as rank
 from stockZaimu10YearSmryMSN a inner join stockMasterMSN b on a.stockCode = b.stockCode 

where a.debt>0 and round(a.yyyymm/100,0)=@yyyy
group by b.gyoshuCode, b.stockGyoshu, round(a.yyyymm/100,0)
-- order by b.gyoshuCode, yr;
order by avg((a.asset-a.debt)/a.asset) desc;


set @a = 0;
select b.gyoshuCode, b.stockGyoshu, avg(a.asset/a.debt) as debtratio, avg((a.asset-a.debt)/a.asset) as equity_ratio, @a:=@a+1 as rank
 from stockZaimu10YearSmryMSN a inner join stockMasterMSN b on a.stockCode = b.stockCode 
where a.debt>0
group by b.gyoshuCode, b.stockGyoshu
order by avg((a.asset-a.debt)/a.asset) desc;


-- 年別

select b.gyoshuCode, b.stockGyoshu,  truncate(a.yyyymm/100,0) as yr, round(avg(a.asset/a.debt),1) as debtratio, round(avg((a.asset-a.debt)/a.asset),3) as equity_ratio
 from stockZaimu10YearSmryMSN a inner join stockMasterMSN b on a.stockCode = b.stockCode 
where a.debt>0
group by b.gyoshuCode, b.stockGyoshu, truncate(a.yyyymm/100,0)
order by b.gyoshuCode, b.stockGyoshu, truncate(a.yyyymm/100,0);


-- 流動比率
select b.gyoshuCode, b.stockGyoshu, round(avg(a.ryudoshisan/ryudofusai), 1) as current_ratio
from stockZaimuMSN a inner join stockMasterMSN b on a.stockCode = b.stockCode
where a.ryudofusai > 0 and year = 2009
group by b.gyoshuCode, b.stockGyoshu;

-- 自己資本比率
select b.gyoshuCode, b.stockGyoshu, round(avg((a.asset-a.debt)/a.asset),3) as equity_ratio
from stockZaimu10YearSmryMSN a inner join stockMasterMSN b on a.stockCode = b.stockCode
where a.debt > 0 and truncate(a.yyyymm/100,0) = 2009
group by b.gyoshuCode, b.stockGyoshu;

