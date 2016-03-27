bgmyc.gibbs.mpi <- function (
                             data, m, burnin=1, thinning=1, py1, py2, pc1, pc2,
                             t1, t2, scale=c(20, 10, 5.00),
                             start=c(1.0, 0.5, 50.0), likelihood, prior
                             )
{

	
	NNodes<-data$tree$Nnode
	p = length(start)
	vth = array(0, dim = c(m, p+1))
	f0 = likelihood(start, data)+prior(start, py1, py2, pc1, pc2, t1, t2) #####################* PRIOR
	arate = array(0, dim = c(1, p))
	th0 = start
	th1 = th0
	mover<-function(index, initial){
		if(index == 1){return(rgamma(1, shape=scale[1], rate=(scale[1]/initial[1])))}
		if(index == 2){return(rgamma(1, shape=scale[2], rate=(scale[2]/initial[2])))}
		if(index == 3){return(round(initial[3] + rnorm(1) * scale[3]))}
	}

	for (i in 1:m) {
		th1<-th0

		for (j in 1:p) {

			th1[j] = mover(j,th0)
			
			if(j<3){
				f1 = likelihood(th1, data)+prior(th1, py1, py2, pc1, pc2, t1, t2) ##############* PRIOR
				u = runif(1) < exp(f1 - f0)*(dgamma(th0[j], shape=scale[j], rate=(scale[j]/th1[j])) / dgamma(th1[j], shape=scale[j], rate=(scale[j]/th0[j])))
			}else{
				if(th1[3]<NNodes && th1[3]>=2){  
					f1 = likelihood(th1, data)+prior(th1, py1, py2, pc1, pc2, t1, t2) ###############*PRIOR
				}else{
					f1=log(0)
				}
				u = runif(1) < exp(f1 - f0)
			}
			
			

			if (u){
				th0[j] = th1[j] 
				f0 = f1 
			}
			else {
				th0[j] = th0[j]
				f0 =f0			
			}
							
			vth[i, j] = th0[j]
			vth[i,p+1] = f0
			arate[j] = arate[j] + u
		}		
	
		# No longer necessary; user won't see comprehensible output
		#if((i==m*0.1)|(i==m*0.2)|(i==m*0.3)|(i==m*0.4)|(i==m*0.5)|(i==m*0.6)|(i==m*0.7)|(i==m*0.8)|(i==m*0.9)|(i==m)){
		#cat((i/m)*100, "%","\n")
		#}
	}
	arate = arate/m
	stuff = list(par = vth[((burnin+1)/thinning):(m/thinning)*thinning,], accept = arate, tree = data$tree, mrca = data$mrca.nodes)
	
	parnames<-c("py", "pc", "th")
    # No longer necessary; user won't see comprehensible output
	#cat("acceptance rates", "\n", parnames, "\n", stuff$accept, "\n")
	
	class(stuff)<-"singlebgmyc"
	return(stuff)
}
