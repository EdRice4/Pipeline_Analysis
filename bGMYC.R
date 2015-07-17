library(ape)
library(bGMYC)
suppressMessages(library(R.utils))

args <- commandArgs(
                trailingOnly=TRUE, asValues=TRUE,
                defaults=c(
                        py1=0, py2=2, pc1=0, pc2=2, t1=2, t2=51,
                        scale=c(20, 10, 5), start=c(1, 0.5, 50)
                        ),
                adhoc=TRUE
                )

outputSVG <- function(result, output) {
    svg(paste0(output, '.svg'))
    plot(result)
    dev.off()
}

readNexus <- function(treesFile) {
    treesFile <- paste0(treesFile, '.trees')
    trees <- read.nexus(file=treesFile)
}

specTableOutput <- function(result, output) {
    output <- paste0(output, '.txt')
    bgmyc.spec(result, output)
}

specHeatmap <- function(result) {
    result.probmat <- spec.probmat(result)
}

trees <- readNexus(args$taxon)
result.multi <- bgmyc.multiphylo(
        trees, mcmc=args$mcmc, burnin=args$burnin, thinning=args$thinning,
        py1=args$py1, py2=args$py2, pc1=args$pc1, pc2=args$pc2,
        t1=args$t1, t2=args$t2, start=c(args$start1, args$start2, args$start3),
        scale=c(args$scale1, args$scale2, args$scale3)
        )
outputSVG(result.multi, paste0(args$id, '_MCMC'))
specTableOutput(result.multi, args$id)
result.probmat <- specHeatmap(result.multi)
outputSVG(result.multi, paste0(args$id, '_prob'))
