getwd()
setwd("/Users/tatata/myWork/stock_info/R_analysis")

library(DBI)
library(RMySQL)

m <- dbDriver("MySQL")
# 接続
con <- dbConnect(m, user="stock", password = "stock", 
				host="localhost", dbname = "stock_db")
rs <- dbSendQuery(con, "select count(*) from orgkabuka")

dbClearResult(rs)


# 切断
# dbDisconnect(con)

# p.82
library(tseries)

ts.plot(sunspots)
acf(sunspots, lag.max=480)
x <- rnorm(1000)
y <- diffinv(x)
z <- diff(y)
adf.test(z)

ts.plot(x)

# p.87
# 日経平均の分析
# 日経225 1001

getStockData<-function(connection, code, market.code, start)
{
	strQuery <- paste("SELECT * FROM orgkabuka WHERE code_c = '",
						code, "' AND mkt_code1 = ", market.code, 
						" AND date_c >= '", start, "'", sep = ""
					)
	res <- dbSendQuery(connection, strQuery)
	data <- fetch(res)
	dbClearResult(res)
	return(data)

}

strQuery <- paste("select * from orgkabuka where code_c = '1001'",
			"and date_c >= '2006-01-04' ", sep="")
rs <- dbSendQuery(con, strQuery)
nikkei <- fetch(rs)
nikkei <- ts(nikkei$close, start=c(2006,1), frequency=248)
summary(nikkei)
sd(nikkei);ts.plot(nikkei, main="日経平均2006")
summary(lm(as.vector(nikkei) ~ seq(1, length(nikkei))))
ts.plot(summary(lm(as.vector(nikkei)~seq(1, length(nikkei))))$resid)
abline(h=0, col=2, lty=2)
title("Residuals of Ordinary Regression")

acf(nikkei, lag.max=100)
pacf(nikkei, lag.max=100)

nikkei.diff <- diff(nikkei)
ts.plot(nikkei.diff, main="Diff of Nikkei heikin")

acf(nikkei.diff, lag.max=100)
pacf(nikkei.diff, lag.max=100)

summary(nikkei.diff);t.test(nikkei.diff)
hist(nikkei.diff, main="diff of nikkei heikin")

kirin <- getStockData(connection=con, market.code = 1, code = "2503", start="2006-01-04")
kirin<-ts(kirin$close, start=c(2006,1), frequency=248)
ts.plot(kirin, main="キリン差分")
acf(kirin, lag.max=100);pacf(kirin, lag.max=100)
kirin.diff<-diff(kirin)
acf(kirin.diff)
pacf(kirin.diff)

#22.3
# 単位こん検定
adf.test(nikkei);adf.test(nikkei.diff)
takeda<-getStockData(connection=con, code="4502", market.code = 1, start="2006-01-04")
takeda<-ts(takeda$close, start=c(2006,1), frequency=248)
ts.plot(takeda, main="武田薬品")
adf.test(takeda);adf.test(diff(takeda))

# 22.3.3
xx <- cumsum(rnorm(100));yy <- cumsum(rnorm(100))
adf.test(xx);adf.test(yy)
par(mfrow=c(1,2))
plot(xx, type="l", main="random walk (xx)");plot(yy, type="l", main="random walk  (yy)")
par(mfrow=c(1,1))
summary(lm(yy~xx))

# 22.4 p.106
nikkei.r <- diff(nikkei)/nikkei[-length(nikkei)]
sd(nikkei.r);t.test(nikkei.r)
acf(nikkei.r);pacf(nikkei.r)

nikkei.log <- log(nikkei);sd(nikkei.log)
ar(nikkei.log)
adf.test(nikkei.log)
ts.plot(nikkei.log)

nikkei.log.diff <- diff(log(nikkei));sd(nikkei.log.diff)
adf.test(nikkei.log.diff)
ts.plot(nikkei.log.diff);abline(h=mean(nikkei.log.diff), lty=2)

summary(nikkei.log);t.test(nikkei.log)
summary(nikkei.log.diff);t.test(nikkei.log.diff)
hist(nikkei.log.diff, breaks=20, main="Diff of log of 日経平均")

# sde
simu.sde01 <- function(x0=100, a=0.1, b=0.2, n=5, m=300, dt=1/300)
{
	for( i in 1:n)	{
		x<-rnorm(m)
		y<-x0
		for ( j in 1:m){
			y.t <- y[j]
			y <- c(y, y.t+a*y.t*dt+b*y.t*x[j]*sqrt(dt))
		}
		plot(y, type="l", ylim=c(max(0, x0-abs(a)*m),x0+abs(a)*m))
		par(new=TRUE)
	}
	title("Simulation of SDE")
}

simu.sde01(100,0.1,0.2,5,300,1/300)

simu.sde02 <- function(x0=10, a=0.1, b=0.2, n=5, m=300, dt=1/300)
{
	for( i in 1:n)	{
		x<-rnorm(m)
		y<-x0
		for ( j in 1:m){
			y.t <- y[j]
			y <- c(y, y.t+a*y.t*dt+b*y.t*x[j]*sqrt(dt))
		}
		plot(y, type="l", ylim=c(max(0, x0-2*abs(a)*m),x0+2*abs(a)*m))
		par(new=TRUE)
	}
	title("Simulation of SDE without drift parameter")
}
simu.sde02(nikkei.log[1], 0, sd(nikkei.log.diff), 100, length(nikkei), 1/length(nikkei))

# 22.5
nikkei2006<-ts(nikkei[1:248], start=c(2006,1), frequency=248)
ar(nikkei2006, method="ols")
ts.plot(nikkei2006)
ar(nikkei2006, method="mle")
ar(nikkei2006, method="yw")
ar(nikkei2006, method="burg")
nikkei.ar <- ar(nikkei2006, method="ols")
nikkei2006e <- nikkei2006 + nikkei.ar$resid
range.y <- c(min(nikkei2006), max(nikkei2006))
plot(nikkei2006, ylim=range.y)
par(new=TRUE)
plot(nikkei2006e, lty=2, col=2, ylim=range.y, ylab="")
title("Estimation of 2006 by OLD (赤線)")

pred.nikkei.ar <- predict(nikkei.ar, n.ahead=(length(nikkei)-248))
nikkei2007 <- ts(nikkei[249:length(nikkei)], star=c(2007,1), frequency=248)
ts.plot(nikkei2007, ylim=c(min(nikkei),max(nikkei)))
lines(pred.nikkei.ar$pred, lty=2)
lines(pred.nikkei.ar$pred+pred.nikkei.ar$se, lty=3)
lines(pred.nikkei.ar$pred-pred.nikkei.ar$se, lty=3)
title("Prediction of 2007 by OLS")

# ARIMA
arima.table<-function(x, ar.max=3, ma.max=3, diff.max=1)
{
	y <- c()
	for (k in (0:diff.max))
	{
		for(i in (0:ar.max))
		{
			for(j in (0:ma.max))
			{
				a <- try(arima(x, order=c(i,k,j), method="ML"), TRUE)$aic
				if (!is.numeric(a)) a <- 0
				y <- c(y, i, k, j, a)
			}
		}
	}
	y <- data.frame(matrix(y, ncol=4, byrow=TRUE))	names(y) <- c("AR", "DIFF", "MA", "AIC")
	return(y)
}

# takes ages...
# nikkei.aic <- arima.table(nikkei, 8, 8, 1)
head(nikkei.aic)
sortlist<-order(nikkei.aic$AIC)
head(nikkei.aic[sortlist,],n=3)
# (3,0,3)で計算ができていないので、手計算
arima(nikkei, order=c(3,0,3))	# AIC = 6136.18
subset(nikkei.aic[-31,], min(AIC)==AIC)
# (2,1,2) gives min AIC
(nikkei.arima<-arima(nikkei, order=c(2,1,2)))
summary(nikkei.arima)
tsdiag(nikkei.arima)

# 22.5.5
# simulation by ARIMA model
simu.arima01 <- function(c.ar=c(0.8), dd=0, c.ma=c(0), nn = 100, sdd = 0.1)
{
	ifelse(c.ar == 0, n.ar<-0, n.ar<-length(c.ar))	ifelse(c.ma==0, n.ma<-0, n.ma<-length(c.ma))
	if(n.ar==0 && n.ma==0 && dd==0)
	{	#ARIMA(0,0,0)正規乱数列
		ss<-ts(c(0, arima.sim(list(order=c(0,0,0)), n=nn, sd=sdd)[-1]))
	}
	else if (n.ar==0 && n.ma == 0)
	{
		stop("check the parameters.")
	}
	else if (n.ar == 0) { 
		# MA(q)
		ss <- arima.sim(list(order=c(n.ar, dd, n.ma), ar=c.ar), n=nn, sd=sdd)
	}
	else {
		# ARIMA(p, d, q)
		ss <- arima.sim(list(order=c(n.ar, dd, n.ma), ar=c.ar, ma=c.ma), n=nn, sd=sdd)
	}
	ts(ss)
}

simu.arima01(c.ar=0, dd=0, c.ma=0, nn=10)
simu.arima01(c.ar=0.8, dd=0, c.ma=0.2, nn=10)
simu.arima01(c.ar=c(0.8, 0.1), dd=1, c.ma=0.2, nn=10)

simu.arima02 <- function(x, n.ar=2, dd=0, n.ma=2)
{
	att.x <- attributes(x)$tsp
	num.x <- length(x)
	simu <- arima(x, order=c(n.ar, dd, n.ma), method="ML")
	ss <- x[1] + simu.arima01(c.ar=coef(simu)[1:(n.ar)],
			dd, c.ma=coef(simu)[(n.ar+1):(n.ar+n.ma)], nn=num.x,
			sdd = sqrt(simu$sigma2))
	ss <- ts(ss, star=att.x[1], end=att.x[2], frequency=att.x[3])
	return (ss)
	
}

simu.arima02p <- function(mm=3, xxx, n.ar = 2, dd = 0, n.ma=2)
{
	ss <- simu.arima02(xxx, n.ar, dd, n.ma)
	ss.max <- max(ss); ss.min <- min(ss)
	ss.sd <- sd(ss)
	ylim.low <- max(0, ss.min -ss.sd)
	ylim.high <- ss.max + ss.sd
	plot(xxx, ylim=c(ylim.low, ylim.high))
	par(new=TRUE)
	for ( i in 1:mm){
		ss <- simu.arima02(xxx,n.ar, dd, n.ma)
		plot(ss, lty=3, col=2, ylab="", xlab="", ylim=c(ylim.low, ylim.high))
		par(new=TRUE)
		
		}
	title("Simulation of ARIMA")
}

simu.arima02p(mm=1, xxx=nikkei, n.ar = 4, dd=1, n.ma=5)
spectrum(simu.arima02(xxx=nikkei, n.ar=4, dd=1, n.ma=5), spans=3)

simu.arima02p(mm=3, xxx=nikkei.log, n.ar=7, dd=0, n.ma=5)
spectrum(simu.arima02(xxx=nikkei.log, n.ar=7, dd=0, n.ma=5), spans=3)



# 22.5.6 p.139
daikin <- getStockData(connection=con, code="6367", market.code=1, start="2006-01-04")
daikin <- ts(daikin$close, start=c(2006,1), frequency=248)
daikin.aic <- arima.table(daikin, 4,4,1)
sortlist <- order(daikin.aic$AIC)
head(daikin.aic[sortlist,], n=10)
arima(daikin, order=c(2,0,4), method="ML")
arima(daikin, method="ML")

# GARCH
summary(garch(nikkei, order=c(1,0)))
summary(garch(nikkei, order=c(1,1)))

summary(garch(nikkei.r, order=c(1,1)))
summary(garch(nikkei.r, order=c(1,2)))
summary(garch(nikkei.r, order=c(1,3)))
summary(garch(nikkei.r, order=c(1,4)))

plot(nikkei.r, main="日経日次収益率")
hist(nikkei.r, main="nikkei.r")
acf(nikkei.r^2, main="ACF of squared nikkei.r")

