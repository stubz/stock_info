use stock_db;
drop table if exists stockZaimuMSN;
create table stockZaimuMSN
(
 stockcd           varchar(5) not null, -- $BLCJA%3!<%I(B
 year              char(4)    not null, -- $BG/?t(B
 uriage            int           null, -- $BGd>e9b9g7W(B
 uriagesourieki    int           null, -- $BGd>eAmMx1W(B
 eigyorieki        int           null, -- $B1D6HMx1W(B
 zeikinmaejunrieki int           null, -- $B@G6bEyD4@0A0Ev4|=cMx1W(B
 zeihikigorieki   int           null, -- $B@G0z$-8eMx1W(B
 toukijunrieki     int           null, -- $B0[>o9`L\A0$NEv4|=cMx1W(B
 fusai             int           null, -- $BIi:D9g7W(B
 shihon            int           null, -- $B;qK\9g7W(B
 ryudoshisan       int           null, -- $BN.F0;q;:9g7W(B
 ryudofusai        int           null, -- $BN.F0Ii:D9g7W(B
 shisan            int           null, -- $B;q;:9g7W(B
 shihonkei         int           null, -- $BIi:D!">/?t3t<g;}$AJ,5Z$S;qK\9g7W(B
 chokitoushi       int           null, -- $BD94|Ej;q(B
 uketoritegata     int           null, -- $B<u<h<j7A!J8GDj;q;:!K(B
 sonotakoteishisan int           null, -- $B$=$NB>8GDj;q;:9g7W(B
 futsukabusu       int           null, -- $BIaDL3t<0H/9T?t9g7W(B
 eigyocf           int           null, -- $B1D6H%-%c%C%7%e%U%m!<(B
 toushicf          int           null, -- $BEj;q%-%c%C%7%e%U%m!<(B
 zaimucf           int           null  -- $B:bL3%-%c%C%7%e%U%m!<(B
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

