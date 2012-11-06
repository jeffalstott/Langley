
pdf('plot.pdf')
par.default <- par()

#library(rms)
library(survival)
library(rmeta)
analysis<-coxph(Surv(Parent_Child_Registration_Interval_Corrected_Days) ~
    (Parent_Gender*Gender)
#    Gender
#    + Parent_Gender
#    + Parent_Child_Age
#    + Age
#    + Parent_Age
#    + Age*Parent_Child_Age
#     + (Parent_Agenumeric*Agenumeric)
    + (Parent_Age*Age)
    + Same_Relationship_to_Parent_as_They_Had_to_Their_Parent
    + Relationship_with_Parent
#    + Heard_Through_Same_Medium_as_Parent
#    + Heard_Through_Medium
    + Parent_Child_Location
    + Parent_Number_of_Children-1
    + Number_of_Children
#    + Has_Children
    + Depth_in_Invite_Chain-1
    + Parent_Join_Time_numeric_days,
    , data=dataf
    , singular.ok=TRUE)

m_var = c(
    "Parent_Number_of_Children",
    "Number_of_Children",
    "Depth_in_Invite_Chain",
    "Parent_Join_Time_numeric_days"
    ) # covariates for martingale

q<-summary(analysis)
n_variables = length(q$coefficients[,1])

print(analysis$call)

d = data.frame(coef=q$coefficients[,1], expcoef=q$conf.int[,1], lower95=q$conf.int[,3], upper95=q$conf.int[,4], se=q$coefficients[,3])

write.csv(d, file='analysis.csv')
xlims=c(log(min(d$lower95, na.rm=TRUE)), log(max(d$upper95, na.rm=TRUE)))
#plot(0:10, type = "n", xaxt="n", yaxt="n", bty="n", xlab = "", ylab = "")

#for (i in 1:n_variables){
#    text(5, i, names(coef(analysis))[i])
#    }

#analysis<-coxph(Surv(Parent_Child_Registration_Interval_Corrected_Days) ~ Gender +Parent_Gender 
#    + Age + Parent_Age + 
#    Relationship_with_Parent +  Heard_Through_Same_Medium_as_Parent, data=dataf)

cox2meta<-function(analysis, range){
    q<-summary(analysis)
    ses<-q$coefficients[range,3]
    ratios<-q$coefficients[range,1]
    labels<-names(q$coefficients[range,1])
    metaplot(ratios, ses, nn=ses, labels=labels, logeffect=TRUE, ps=8)
}

n_per_plot = 4
for (i in 0:floor(n_variables/n_per_plot)){
    range = (1+i*n_per_plot):(n_per_plot+i*n_per_plot)
    if(max(range)>n_variables){
        range = (1+i*n_per_plot):n_variables
    }
    if(min(range)>=n_variables){
        break
    }
    ses<-q$coefficients[range,3]
    ratios<-q$coefficients[range,1]
    labels<-names(q$coefficients[range,1])
    metaplot(ratios, ses, nn=ses, labels=labels, logeffect=TRUE, ps=8)
}

par(par.default)

b <- coef(analysis) # regression coefficients
res <- residuals(analysis, type="martingale")

if (length(m_var!=0)){
X <- as.matrix(dataf[,m_var]) # matrix of covariates

par(mfrow = c(2,ceiling(length(m_var)/2)))
for (j in 1:length(m_var)){# partial-residual plots
    m = m_var[j]
    plot(X[,m], b[m]*X[,m] + res, xlab=m,
    ylab="component + Martingale residual")
    abline(lm(b[m]*X[,m] + res ~ X[,m]), lty=2)
    lines(lowess(X[,m], b[m]*X[,m] + res, iter=0))
}

par(par.default)
}
dfbeta <- residuals(analysis, type="dfbetas")

par(mfrow = c(2,2))
for (j in 1:length(coef(analysis))){
    if (!is.nan(dfbeta[1,j])) {
        #plot(dfbeta[,j], ylab=names(coef(analysis))[j], tcl=-.5)
        #abline(h=0, lty=2)
        hist(dfbeta[,j], xlab="Change in Coefficient (Standard Errors)", ylab="Frequency", main=names(coef(analysis))[j])
    }
    }

par(par.default)

par(mfrow = c(2,2))
zph<-cox.zph(analysis)
for (j in 1:nrow(zph$var)){
    if (!is.na(zph$table[j,3])){
        plot(zph[j])
    }
}
dev.off()
