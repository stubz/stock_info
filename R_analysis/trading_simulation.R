setwd("/Users/tatata/myWork/stock_info/R_analysis")
library(tseries)
library(RMySQL)
source("stock_db_connect.R")
source("technical_statistic_functions.R")
source("simulation_functions.R")

m <- dbDriver("MySQL")
# 接続
con <- dbConnect(m, user="stock", password = "stock", 
				host="localhost", dbname = "stock_db")


# 切断
dbDisconnect(con)

simu.ss(nn=280, z0=100, sigma=2, uu=10, dd=20)