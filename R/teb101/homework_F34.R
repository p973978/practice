library(dplyr)

setwd('C:/Users/User/Desktop/R/riii/Statistics')
load("cdc.Rdata")
str(cdc)
head(cdc)
names(cdc)
col = c("exerany","hlthplan","smoke100")

cdc[,col] = ifelse(cdc[,col] == 1, 'yes', 'no')
ifelse(cdc$exerany == 1, 'yes', 'no')

# Q1 ���d���p������Ҭ���?
cdc %>%
  group_by(genhlth) %>%
  count(genhlth) %>%
  summarise(health_ratio = (n / nrow(cdc)))

# Q2 �k�k����Ҥ�v
cdc %>%
  filter(smoke100 == 'yes') %>%
  group_by(gender) %>%
  count(gender) %>%
  summarise(smoke_ratio = (n / nrow(cdc)))


# �~���������
install.packages('ggplot2')
library('ggplot2')
g <- ggplot(cdc,aes(x=age))
g+geom_bar(color='black',binwidth = 5)


#BMI boxlot
cdc$BMI = cdc$weight / (cdc$height**2*703)
ggplot(cdc,aes(x= genhlth,y=BMI)) + geom_boxplot()


#�����魫�~�������Y��
install.packages('corrplot')
library(corrplot)
install.packages('DataExplorer')
library(DataExplorer)
install.packages("ggcorrplot")
library(ggcorrplot)

ggcorrplot(corr, hc.order = TRUE,
           lab = TRUE)

corr = cor(cdc[,c("height","weight","age")])

corrplot(corr, type = "upper", order = "hclust", 
         tl.col = "black", tl.srt = 45)

plot_correlation(corr)