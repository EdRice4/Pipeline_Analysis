library(ape)
library(bGMYC)

args <- as.list(commandArgs(TRUE))
output <- args[1:2]
params <- as.integer(tail(args, length(args) - 2))

outputSVG <- function(result, output) {
    svg(paste0(output, '.svg'))
    plot(result)
    dev.off()
}

readNexus <- function(treesFile) {
    treesFile <- paste0(treesFile, '.trees')
    trees <- read.nexus(file=treesFile)
}

bGMYC <- function(trees, MCMC, burnin, thinning, ...) {
    bgmyc.multiphylo(trees, mcmc=MCMC, burnin=burnin,
                     thinning=thinning, ...)
}

specTableOutput <- function(result, output) {
    output <- paste0(output, '.txt')
    bgmyc.spec(result, output)
}

specHeatmap <- function(result) {
    result.probmat <- spec.probmat(result)
}

trees <- readNexus(output[[1]])
result.multi <- bGMYC(trees, args[[3]], args[[4]], args[[5]], args[[6]],
                      args[[7]], args[[8]], args[[9]], args[[10]])
outputSVG(result.multi, paste0(output[[2]], '_MCMC'))
specTableOutput(result.multi, output[[2]])
result.probmat <- specHeatmap(result.multi)
outputSVG(result.multi, paste0(output[[2]], '_prob'))
