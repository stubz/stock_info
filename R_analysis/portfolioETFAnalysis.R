setwd("/Users/popopopo/myWork/stock_info/R_analysis")
source("stockDB.R")

# ETF銘柄リストを取得する
etflist <- getETFCodeList()

# 各銘柄を横持ちにしたデータセットを作る
# ループをまわして各銘柄のデータを取得する
etfdata <- NULL
for(i in seq(along=etflist[,1]))
{
	etfdata[[i]] <- getPriceDailyByCodeAll(stockcd=etflist[i,1], marketcd=etflist[i,2])[,"close"]
	colnames(etfdata[[i]]) <- paste("close",".",etflist[i,1],sep="")
}

# 横にくっつける。全銘柄のデータがそろうのが何日か調べておく
# 指定した日付以降のデータがある銘柄だけ対象にする
etf <- NULL
maxdate <- NULL
k<-0
for(i in seq(along=etfdata))
{
	tmpdate <- min(row.names(etfdata[[i]]))
	tmpdate2 <- max(row.names(etfdata[[i]])) 
	if (tmpdate<='2009-12-31' && tmpdate2 > '2009-12-31' ){
		if ( k == 0 ){
			etf <- etfdata[[i]]
		} else {
			etf <- cbind(etf, etfdata[[i]])
		}
		k<-k+1
	}
}

if(0){
etf <- NULL
maxdate <- NULL
for(i in seq(along=etfdata))
{
	# tmpdate <- min(row.names(etfdata[[i]]))
	# tmpdate2 <- max(row.names(etfdata[[i]])) 
	
	if ( i == 1 ){
		etf <- etfdata[[i]]
	} else {
		etf <- cbind(etf, etfdata[[i]])
	}
}
}

# データが全部ある列だけ選ぶ
etf.trunc <- etf[445:dim(etf)[1], ]
etf.ret <- returns(etf.trunc)


##############
# 相関係数がマイナスの組み合わせを探す
cor.low <- -0.1
cor.list <- as.data.frame(matrix(rep(0,5),ncol=5))
etf.cor <- cor(etf.ret)
for( i in 1:dim(etf.cor)[1]){
	for ( j in i:dim(etf.cor)[1])	
		if (etf.cor[i,j] < cor.low) {
				cor.list <- rbind(cor.list, c(i,j,rownames(etf.cor)[i],colnames(etf.cor)[j], round(etf.cor[i,j],3)))
		}
}
cor.list<-cor.list[-1,]; colnames(cor.list)<-c("rownum","colnum","stockcd1","stockcd2","correl")
head(cor.list)
cor.list$cd1 <- as.numeric(substring(cor.list$stockcd1,7,11))
cor.list$cd2 <- as.numeric(substring(cor.list$stockcd2,7,11))

a<-merge(cor.list,etflist[,c(1,3)],by.x="cd1",by.y="stockcd")
b<-merge(a,etflist[,c(1,3)],by.x="cd2",by.y="stockcd")
# corが低い順に並び替え
cor.list2 <- b[,c("cd1","cd2","correl","stocknm.x","stocknm.y")]
cor.list2<-cor.list2[order(cor.list2[,5],decreasing=TRUE),]
head(cor.list2);dim(cor.list2)


##############


# ポートフォリオクラスを設定する
lppSpec <- portfolioSpec()
setNFrontierPoints(lppSpec) <- 25
longFrontier <- portfolioFrontier(etf.ret, lppSpec)
tailoredFrontierPlot(longFrontier,mText="MV Portfolio - Long Only Constraints", risk="Cov")




# global minimum variance
# p.277
globminSpec <- portfolioSpec()
globminPortfolio <- minvariancePortfolio(
	data=etf.ret,
	spec=globminSpec,
	constraints="LongOnly"
	)
print(globminPortfolio)

col <- seqPalette(ncol(etf.ret), "YlGn")
weightsPie(globminPortfolio, box=FALSE, col=col)
mtext(text="Global Minimum Variance MV Portfolio", side=3, line=1.5, font=2, cex=0.7, adj=0)
weightedReturnsPie(globminPortfolio, boox=FALSE, col=col)
mtext(text="Global Minimum Variance MV Portfolio", side=3, line=1.5, font=2, cex=0.7, adj=0)
covRiskBudgetsPie(globminPortfolio, box=FALSE, col=col)
mtext(text="Global Minimum Variance MV Portfolio", side=3, line=1.5, font=2, cex=0.7, adj=0)

# compute tangency portfolio 
tgSpec <- portfolioSpec()
setRiskFreeRate(tgSpec) <- 0
tgPortfolio <- tangencyPortfolio(
		data=etf.ret, spec=tgSpec, constraints="LongOnly")
print(tgPortfolio)








sum(sort(row.names(etf)<='2009-12-31'))
etf[444,1]
sort(row.names(etf))[500:510]

summary(returns(etf, na.rm=TRUE))


for(i in 1:106)
{
	a<-start(etfdata[,i])
	print(paste(i,":",a))
	
}
