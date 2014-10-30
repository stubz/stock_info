use stock_db;
drop table if exists stockZaimuMSN;
create table stockZaimuMSN
(
 stockcd           varchar(5) not null, -- 銘柄コード
 year              char(4)    not null, -- 年数
 uriage            int           null, -- 売上高合計
 uriagesourieki    int           null, -- 売上総利益
 eigyorieki        int           null, -- 営業利益
 zeikinmaejunrieki int           null, -- 税金等調整前当期純利益
 zeihikigorieki   int           null, -- 税引き後利益
 toukijunrieki     int           null, -- 異常項目前の当期純利益
 fusai             int           null, -- 負債合計
 shihon            int           null, -- 資本合計
 ryudoshisan       int           null, -- 流動資産合計
 ryudofusai        int           null, -- 流動負債合計
 shisan            int           null, -- 資産合計
 shihonkei         int           null, -- 負債、少数株主持ち分及び資本合計
 chokitoushi       int           null, -- 長期投資
 uketoritegata     int           null, -- 受取手形（固定資産）
 sonotakoteishisan int           null, -- その他固定資産合計
 futsukabusu       int           null, -- 普通株式発行数合計
 eigyocf           int           null, -- 営業キャッシュフロー
 toushicf          int           null, -- 投資キャッシュフロー
 zaimucf           int           null  -- 財務キャッシュフロー
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

