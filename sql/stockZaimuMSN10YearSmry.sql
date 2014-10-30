use stock;
drop table if exists stockZaimu10YearSmryMSN;
create table stockZaimu10YearSmryMSN
(
 stockcd           varchar(5) not null, -- 銘柄コード
 yyyymm            int        not null, -- 年月数
 sales             int            null, -- 売上げ
 ebit              int            null, -- 金利税引き前利益
 depreciation      int            null, -- 減価償却
 earnings          int            null, -- 純利益
 eps               float          null, -- １株あたり利益
 taxrate           float          null, -- 税率
 asset             int            null, -- 資産 (MSNでは流動資産となっているがBSの値と比較すると全資産を意味している)
 debt              int            null, -- 負債（MSNでは流動負債となっているが、中身は長期債務等も含めた負債合計）
 long_term_debt    int            null, -- 長期債務
 shares            float          null  -- 発行済株式数
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

