library(ape)
library(bGMYC)

args <- as.list(commandArgs(TRUE))
args[3:8] <- as.integer(args[3:8])

outputSVG <- function(result, output) {
    svg(paste0(output, '.svg'))
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
    bgmyc.spec(result, output)
}

specHeatmap <- function(result) {
    result.probmat <- spec.probmat(result)
}

trees <- readNexus(args[[1]])
result.multi <- bGMYC(trees, args[[3]], args[[4]], args[[5]], args[[6]],
                      args[[7]], args[[8]])
outputSVG(result.multi, paste0(args[[2]], '_MCMC'))
specTableOutput(result.multi, ags[[2]])
result.probmat <- specHeatmap(result.multi)
outputSVG(result.multi, paste0(args[[2]], '_prob'))
