#!/usr/bin/env Rscript

bgmyc.multiphylo.mpi <- function(
                                 multiphylo, mcmc, burnin, thinning, noproc,
                                 py1=0, py2=2, pc1=0, pc2=2, t1=2, t2=51,
                                 scale=c(20, 10, 5), start=c(1, 0.5, 50),
                                 sampler=bgmyc.gibbs.mpi, likelihood=bgmyc.lik,
                                 prior=bgmyc.prior
                                 ) {

    # Get length of data for informative output
    ntre <- length(multiphylo)

    # Generate SOCK cluster
    cl <- makeCluster(noproc)

    # Partition data amongst processors
    trees.split <- clusterSplit(cl, multiphylo)

    # Print informative output for user
    cat("You are running a multi tree analysis on", ntre, "trees.\n")
    cat("These trees each contain", length(multiphylo$tip.label[[1]]), "tips.\n")
    cat("The Yule process rate change parameter has a uniform prior ranging from", py1, "to", py2, ".\n")
    cat("The coalescent process rate change parameter has a uniform prior ranging from", pc1, "to", pc2, ".\n")
    cat("The threshold parameter, which is equal to the number of species, has a uniform prior ranging from", t1, "to", t2, ". The upper bound of this prior should not be more than the number of tips in your trees.\n")
    cat("The MCMC will start with the Yule parameter set to", start[1], ".\n")
    cat("The MCMC will start with the coalescent parameter set to", start[2], ".\n")
    cat("The MCMC will start with the threshold parameter set to", start[3], ". If this number is greater than the number of tips in your tree, an error will result.\n")
    cat("Given your settings for MCMC, burnin and thinning, your analysis will result in", ((mcmc-burnin)/thinning)*ntre, "samples being retained.\n")
    cat("Given your settings for MPI, your analysis will result in:\n")
    for(i in seq_along(trees.split)) {
        cat(length(trees.split[[i]]), "samples being sent to slave", i, "\n ")
    }

    # Optimize function for MPI environment
    bgmyc.mpi <- function(trees, ...) {

        # Initialize empty list for output
        outputlist <- list()

        for (i in 1:length(trees)) {
            data <- bgmyc.dataprep(trees[[i]])
            NNodes <- data$tree$Nnode
            outputlist[[i]] <- sampler(
                                       data, m=mcmc, burnin, thinning, py1,
                                       py2, pc1, pc2, t1, t2, scale, start,
                                       likelihood, prior
                                       )
        }

        class(outputlist) <- "multibgmyc"
        return(outputlist)

    }

    # Prepare environment
    funcs2send <- c(
                    'bgmyc.gibbs.mpi', 'bgmyc.lik', 'bgmyc.prior',
                    'bgmyc.dataprep', 'is.ultrametric', 'is.binary.tree',
                    'branching.times'
                    )
    clusterExport(cl, funcs2send)
    
    # Run that function
    output <- parLapply(
                        cl, trees.split, bgmyc.mpi, mcmc, burnin,
                        thinning, py1, py2, pc1, pc2, t1, t2, scale, start,
                        likelihood, prior
                        )
    
    # Shutdown SOCK cluster
    stopCluster(cl)

    # Collapse output by first level only
    output <- unlist(output, recursive=FALSE)

    # Return output
    return(output)
}
