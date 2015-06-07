#! /path/to/Rscript --vanilla

library(ape)
library(bGMYC)

args <- as.list(commandArgs(TRUE))
args[3:8] <- as.integer(args[3:8])

outputSVG <- function(result, output) {
    svg(output)
    plot(result)
    dev.off()
}

readNexus <- function(treesFile) {
    treesFile <- paste0(treesFile, '.trees')
    trees <- read.nexus(file=treesFile)
}

bGMYC <- function(trees, MCMC, burnin, thinning, t1, t2, threshold) {
    result.multi <- bgmyc.multiphylo(trees, mcmc=MCMC, burnin=burnin,
                                     thinning=thinning, t1=t1, t2=t2,
                                     start=c(1,1,threshold))
}

specTableOutput <- function(result, output) {
    output <- paste0(output, '.txt')
    bgmyc.spec(resutl, ouput)
}

specHeatmap <- function(result) {
    result.probmat <- spec.probmat(result)
}
