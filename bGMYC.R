library(ape)
library(bGMYC)
suppressMessages(library(R.utils))

args <- commandArgs(
                trailingOnly=TRUE, asValues=TRUE,
                defaults=c(
                        taxon=NULL,
                        py1=0, py2=2, pc1=0, pc2=2, t1=2, t2=51,
                        scale=c(20, 10, 5), start=c(1, 0.5, 50)
                        ),
                adhoc=TRUE)

outputSVG <- function(result, output) {
    svg(paste0(output, '.svg'))
    plot(result)
    dev.off()
}

readNexus <- function(treesFile) {
    treesFile <- paste0(treesFile, '.trees')
    trees <- read.nexus(file=treesFile)
}

bGMYC <- function(
        trees, MCMC, burnin, thinning, py1, py2, pc1, pc2, t1, t2, scale,
        start) {
    result.multi <- bgmyc.multiphylo(
            trees, mcmc=MCMC, burnin=burnin, thinning=thinning, py1=py1,
            py2=py2, pc1=pc1, pc2=pc2, t1=t1, t2=t2, scale=scale, start=start)
}

specTableOutput <- function(result, output) {
    output <- paste0(output, '.txt')
    bgmyc.spec(result, output)
}

specHeatmap <- function(result) {
    result.probmat <- spec.probmat(result)
}

trees <- readNexus(args$taxon)
result.multi <- bGMYC(
        trees, args$MCMC, args$burnin, args$thinning, args$py1,
        args$py2, args$pc1, args$pc2, args$t1, args$t2,
        c(args$scale1, args$scale2, args$scale3),
        c(args$start1, args$start2, args$start3)
        )
outputSVG(result.multi, paste0(args$taxon, '_MCMC'))
specTableOutput(result.multi, args$taxon)
result.probmat <- specHeatmap(result.multi)
outputSVG(result.multi, paste0(args$taxon, '_prob'))
