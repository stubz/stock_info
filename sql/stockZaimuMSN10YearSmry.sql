use stock;
drop table if exists stockZaimu10YearSmryMSN;
create table stockZaimu10YearSmryMSN
(
 stockcd           varchar(5) not null, -- $BLCJA%3!<%I(B
 yyyymm            int        not null, -- $BG/7n?t(B
 sales             int            null, -- $BGd>e$2(B
 ebit              int            null, -- $B6bMx@G0z$-A0Mx1W(B
 depreciation      int            null, -- $B8:2A=~5Q(B
 earnings          int            null, -- $B=cMx1W(B
 eps               float          null, -- $B#13t$"$?$jMx1W(B
 taxrate           float          null, -- $B@GN((B
 asset             int            null, -- $B;q;:(B (MSN$B$G$ON.F0;q;:$H$J$C$F$$$k$,(BBS$B$NCM$HHf3S$9$k$HA4;q;:$r0UL#$7$F$$$k(B)
 debt              int            null, -- $BIi:D!J(BMSN$B$G$ON.F0Ii:D$H$J$C$F$$$k$,!"Cf?H$OD94|:DL3Ey$b4^$a$?Ii:D9g7W!K(B
 long_term_debt    int            null, -- $BD94|:DL3(B
 shares            float          null  -- $BH/9T:Q3t<0?t(B
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

