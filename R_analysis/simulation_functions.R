# 22.8

simu.ss <- function(nn=280, z0=100, sigma=2, uu=10, dd=20){
	# 乱数を使った株価売買の単純シミュレーション
	# 記録期間は日次換算で１年分(n=280)
	# 初期株価は100円(z0=100)
	# デイリーの標準偏差は固定で２円(sigma=2)
	# 価格上限割合(%)は固定(例えばuu=10)
	# 価格下限割合(%)は固定(例えばdd=20)
	aa <- tt <- pp <- c()
	while ( length(aa) <= nn ){
		# generate random numbers following normal distribution
		zz <- z0 + cumsum(rnorm(nn, 0, sigma))
		# check data
		# get first hitting time when zz exceeds uu% of z0 and decreases blow dd% of z0
		# sell
		u0 <- try(min(seq(1, nn)[zz>z0*(1+uu/100)]), silent = TRUE)
		# buy
		d0 <- try(min(seq(1, nn)[zz<z0*(1-dd/100)]), silent = TRUE)
		ifelse( u0 == +Inf, ifelse(d0 == +Inf, t0 <- 1, t0 <- d0),
				ifelse(d0 == +Inf, t0 <- u0, t0 <- min(u0, d0)))
		# store data
		aa <- append(aa, zz[seq(1, t0)])
		ifelse(t0 == 1, z0 <- pp[length(pp)], z0 <- zz[t0])
		if ( t0 > 1 ){
			tt <- append(tt, length(aa))
			pp <- append(pp, z0)
		}
	}	# repeat until nn data are generated
	aa <- aa[1:nn]
	plot(ts(aa))
	tt <- tt[ tt < nn ]
	pp <- pp[1:length(tt)]
	abline(v = tt, lty = 2, col=2)
	abline(h = pp, lty = 3, col=2)
	print(tt)
	print(pp)
}

