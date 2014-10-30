# テクニカル指標計算関数群
# 一目均衡表
Ichimoku <- function(x, sn=26, cn=9, an1=26, an2=52)
{
	# x : stock data
	# s : 基準線計算の日付。デフォルト26日
	# c : 転換線計算の日付。デフォルト9日
	# a1 : 先行スパン１計算の日付。デフォルト26日
	# a2 : 先行スパン２計算の日付。デフォルト52日
	
	# 株価、先行スパン１、先行スパン２を計算して重ねてグラフで表示する
	n <- length(x)
	attributes(x)$tsp <- c(1, n, 1)
	# 平均値計算のための値設定
	st <- ct <- a1 <- a2 <- L <- c()
	st.c <- sn - 1
	ct.c <- cn - 1
	a1.c <- an1
	a2.c <- an2 - 1
	
	# 計算
	for ( i in ct.c:n )
	{
		if ( i > st.c )	{
			st[i] <- (max(x[(i-st.c):i]) + min(x[(i-st.c):i]))*0.5
		}
		if (i > a1.c) {
			L[i-a1.c] <- x[i]
		}
		if (i > a2.c) {
			a2[i+a1.c] <- (max(x[(i-a2.c):i])+min(x[(i-a2.c):i]))*0.5
		}
		ct[i] <- (max(x[(i-ct.c):i])+min(x[(i-ct.c):i]))*0.5
		a1[i+a1.c] <- (st[i] + ct[i])*0.5
	}
	M1 <- max(c(x, a1, a2), na.rm = TRUE)
	M2 <- min(c(x, a1, a2), na.rm = TRUE)
	plot(x, xlim = c(1,n+a1.c), ylim=c(M2,M1))
	par(new=TRUE)
	plot(ts(a1), xlim=c(1, n+a1.c), ylim=c(M2,M1), lty=2, ylab="", col=2)
	par(new=TRUE)
	plot(ts(a2), xlim=c(1, n+a1.c), ylim=c(M2,M1), lty=3, ylab="", col=4)
	title("一目均衡表 (先行スパン1(赤破線)：先行スパン2(青破線))")
	
}

# 異動平均線の計算
Maverage<-function(x, short=10, long=20)
{
	# 株価と移動平均線をグラフで表示
	# 短期＝10日　長期＝20日
	n <- length(x)	
	attributes(x)$tsp <- c(1,n,1)
	st <- lt <- c()
	if ( short > long) {
		stop("short length must be less than long length")
	}
	for ( i in short:n ) {
		if(i>long) {
			lt[i] <- mean(x[(i-long+1):i])
		}
		st[i] <- mean(x[(i-short+1):i])
	}
	M1 <- max(x)
	M2 <- min(x)
	plot(x, xlim=c(1,n), ylim=c(M2,M1))
	par(new=TRUE)
	plot(ts(st), xlim = c(1,n), ylim=c(M2, M1), lty=2,
		ylab="", col=2)
	par(new=TRUE)
	plot(ts(lt), xlim=c(1,n), ylim=c(M2, M1), lty=3,
		ylab="", col=4)
	title("MA (短期(赤破線), 長期(青破線))")
}

# RSI
Rsi <- function(x, ma=14, upper=70, lower=30)
# 株価とRSIをグラフで表示する
{
	# x : a vector of stock data of type ts
	# ma: days used for moving average calculation
	# upper : upper percentile with default value 70%
	# lower : lower percentile with default value 30%
	# RSI = Un/(Un+Dn)
	# where Dn = av. of down rate over ma period
	#       Un = av. of up rate over ma period
	n <- length(x)
	attributes(x)$tsp <- c(1, n, 1)
	yt <- diff(x)
	rt <- yt.pm <- c()
	yt.pm[seq(1, n-1)[yt>0]] <- 1
	yt.pm[seq(1, n-1)[yt<0]] <- -1
	for ( i in (ma:(n-1))){
		uu <- dd <- c()
		for ( j in ((i-ma+1):i)){
			ifelse(yt.pm[j]==1, uu[j]<-yt[j], dd[j]<- -yt[j])
		}
		u <- try(mean(uu, na.rm=TRUE), silent=TRUE)
		d <- try(mean(dd, na.rm=TRUE), silent=TRUE)
		rt[i] <- 100*u/(u+d)
	}
	M1 <- max(x)
	M2 <- min(x)
	par(mfrow=c(2,1))
	plot(x, xlim=c(1,n), ylim=c(M2,M1))
	plot(ts(rt), xlim=c(1,n), ylim=c(0,100), lty=2,col=2,
		xlab="RSI(赤破線), Upper and Lower Lines", ylab="")
	abline(h=50, lty=4, col=3)
	abline(h=upper, lty=4, col=4)
	abline(h=lower, lty=4, col=4)
	
}


# RSI2
# 同じグラフに株価とRSIを表示する

Rsi2 <- function(x, ma=14, upper=70, lower=30)
{
	n <- length(x)
	attributes(x)$tsp <- c(1, n, 1)
	yt <- diff(x)
	rt <- yt.pm <- c()

	yt.pm[seq(1, n-1)[yt>0]] <- 1
	yt.pm[seq(1, n-1)[yt<0]] <- -1
	for ( i in (ma:(n-1))){
		uu <- dd <- c()
		for ( j in ((i-ma+1):i)){
			ifelse(yt.pm[j]==1, uu[j]<-yt[j], dd[j]<- -yt[j])
		}
		u <- try(mean(uu, na.rm=TRUE), silent=TRUE)
		d <- try(mean(dd, na.rm=TRUE), silent=TRUE)
		rt[i] <- 100*u/(u+d)
	}
	M1 <- max(x)
	M2 <- min(x)
	MM <- min(M1 - mean(x), mean(x) - M2)
	rt <- (rt-50)*MM/50+mean(x)

	plot(x, xlim=c(1,n), ylim=c(M2,M1))
	par(new=TRUE)
	plot(ts(rt), xlim=c(1,n), ylim=c(M2, M1), lty=2,col=2, ylab="")
	abline(h=50, lty=4, col=3)
	abline(h=mean(x)+(upper-50)/50*MM, lty=4, col=4)
	abline(h=mean(x)+(lower-50)/50*MM, lty=4, col=4)
	title("RSI(赤破線), Upper and Lower Lines")
}


# MACD
# MACDt = Yt - Zt
# where 
# Yt = aXt + (1-a)Yt-1 = aXt + (1-a)(aXt-1+(1-a)Yt-2) ...
#    = a*(sum(1-a)^i*Xt-i)
# Zt = bXt + (1-b)Zt-1
#    = b*(sum(1-b)^i*Xt-i)
#  a = 2/(n+1) and b = 2/(m+1)
#  n = 12, m = 26
# St (signal) = av. of MACD over l (normally 9)
Macd <- function(x, short = 12, long = 26, ma = 9, yrange=500)
{
	n <- length(x)
	attributes(x)$tsp <- c(1, n, 1)
	yt <- yt2 <- zt <- zt2 <- macd <- sig <- c()
	alpha.t <- 2/(short+1)
	beta.t <- 2/(long+1)
	for ( i in 1:n){
		yt[i] <- x[i] * (1-alpha.t)^(n-i)
		zt[i] <- x[i] * (1-beta.t)^(n-i)
	}
	for ( i in 1:n){
		yt2[i] <- sum(yt[seq(1,i)])/(1-alpha.t)^(n-i)
		zt2[i] <- sum(zt[seq(1,i)])/(1-beta.t)^(n-i)
		macd[i] <- alpha.t*yt2[i]-beta.t*zt2[i]
	}
	for ( i in ma:n){
		sig[i] <- sum(macd[(i-ma+1):i])/ma
	}
	M1 <- max(x)
	M2 <- min(x)
	par(mfrow=c(2,1))
	plot(x, xlim=c(1,n), ylim=c(M2, M1))
	plot(ts(macd), xlim=c(1,n), ylim=c(-yrange, yrange), lty=1, col=2, 
				xlab="MACD(red), Signal(blue dotted)", ylab="")
	par(new=TRUE)
	plot(ts(sig), xlim=c(1,n), ylim=c(-yrange, yrange), lty=3, col=4, 
				xlab="", ylab="")
	abline(h=0, lty=4, col=3)
	par(mfrow=c(1,1))
}


# Bollinger Bands
# 株価とボリンジャーバンドをグラフで表示
Bollinger <- function(x, ma=26){
	n <- length(x)
	attributes(x)$tsp <- c(1, n, 1)
	yt <- sig <- c()
	for ( i in ma:n){
		yt[i] <- mean(x[seq(i-ma+1,i)])
		sig[i]<- sqrt(var(x[seq(i-ma+1, i)])*(ma-1)/ma)
	}
	M1 <- max(c(x, yt+2*sig), na.rm=TRUE)
	M2 <- min(c(x, yt-2*sig), na.rm=TRUE)
	plot(x, xlim=c(1,n), ylim=c(M2,M1))
	par(new=TRUE)
	plot(ts(yt+2*sig), xlim=c(1,n), ylim=c(M2,M1),lty=3, ylab="", col=2)
	par(new=TRUE)
	plot(ts(yt), xlim=c(1,n), ylim=c(M2,M1),lty=3, ylab="", col=4)
	par(new=TRUE)
	plot(ts(yt-2*sig), xlim=c(1,n), ylim=c(M2,M1),lty=3, ylab="", col=2)
	title("Bollinger Bands (95%)")
}




