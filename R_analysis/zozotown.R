setwd("/Users/popopopo/myWork/stock_info/R_analysis")
source("stockDB.R")

# 3092:スタートトゥデイ
# 9983:ユニクロ
# 7606:UA
# 2607:ABCマート
# 

tracklist <- matrix(c("3092","3",
			"9983","1",
			"7606","1",
			"2607","1"),byrow=TRUE,ncol=2)

tracklistnm <- c("スタートトゥデイ","ユニクロ","UA","ABCマード")
trackdata <- NULL
for(i in seq(along=tracklist[,1]))
{
	trackdata[[i]] <- getPriceDailyByCodeAll(stockcd=tracklist[i,1], 
	marketcd=tracklist[i,2])[,"close"]
	colnames(trackdata[[i]]) <- paste("close",".",tracklist[i,1],sep="")
}




