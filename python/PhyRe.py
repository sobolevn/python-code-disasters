#!/usr/bin/python

"""
CODENAME:     PhyRe
DESCRIPTION:  

Copyright (c) 2009 Ronald R. Ferrucci, Federico Plazzi, and Marco Passamonti..



Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""

import sys

samplefile = sys.argv[1];      del sys.argv[1]
popfile = sys.argv[1];      del sys.argv[1]
#outfile= sys.argv[1];      del sys.argv[1]

#outfile = samplefile
#output = open(outfile, 'w')

#efile = open('error.log','w')
#sys.stderr = efile

#output = open('output','w')
#out.write(allelesfile)
#out.close()
###-----------------options-------------------------###

"""p = permutations for confidence intervals, d1 and d2 are range for number of 
species for funnel plot. parameter: m = AvTD, v = VarTD, e = euler, b = AvTD and VarTd. 
ci = confidence intervals b = batch file. l = user-defined path lengths
"""

p = 1000; d1 = 10; d2 = 70; ci = 'y'; b = 'n'; l = 'n'
batch = b; pathlengths = l; missing = 'n'
#parameter = 'm'; 

from optparse import OptionParser
parser = OptionParser()

d1= int(sys.argv[1]);      del sys.argv[1]
d2= int(sys.argv[1]);      del sys.argv[1]

parser.add_option('-o')
parser.add_option('-p',type = 'int')
parser.add_option('-c')
parser.add_option('-b')
parser.add_option('-l')
parser.add_option('-m')


(options,args) = parser.parse_args()

if options.m: missing = options.m
else: missing = 'n'

if options.o: 
	out = options.o
else: 
	out = samplefile.split('.')[0]


if options.p: p = options.p
else: p = 1000

if options.c: ci = options.c
else: ci = 'y'
	
if options.b: batch = options.b
else: batch = 'n'

if options.l: pathlengths = options.l
else: pathlengths = 'n'



sample = {}; population = {}



output = out + '.out'



o = open(output,'a')

saveout = sys.stdout
sys.stdout = open(output, 'w')

from re import *

#def Taxon():
if batch == 'y':
    Files = []
else:
    Files = [samplefile]

Index = {}; Taxon = {}; coef = {}; Taxon = {}; taxon = []

pathLengths= {}

for i in open(samplefile):
    """
    if match('Taxon:', i):
        x = i.split()
        x.remove('Taxon:')
        #x = [string.lower() for string in x]  

        for i in x:
            taxon.append(i)
            j = x.index(i)
            Index[i] = j + 1
        continue

    elif match('Coefficients:', i):
        x = i.split()
        x.remove('Coefficients:')
        x = map(eval, x)
        
        for t in taxon:
            i = taxon.index(t)
            coef[t] = sum(x[i:])
            pathLengths[t] = x[i]

        continue
    """
    
    if batch == 'y':
        j = i.strip()
        Files.append(j)
    else:
        break

duplicates = []

for i in open(popfile):
    if match('Taxon:', i):
        x = i.split()
        x.remove('Taxon:')
        #x = [string.lower() for string in x]  

        for i in x:
            taxon.append(i)
            j = x.index(i)
            Index[i] = j + 1
        continue

    elif match('Coefficients:', i):
        x = i.split()
        x.remove('Coefficients:')
        x = map(eval, x)
        
        for t in taxon:
            i = taxon.index(t)
            coef[t] = sum(x[i:])
            pathLengths[t] = x[i]

        continue
        
    i.strip()
    x = i.split()    

    #if match('Taxon:', i): continue
    #if match('Coefficients:', i): continue

    species = x[0]; population[species] = {}
    
    if species in sample.keys():
        duplicates.append(species)
    else:
        sample[species] = {}
        population[species] = {}


    if missing == 'y':
        mtax = ''
        for t in taxon:
            if x[Index[t]] == '/':
                #sample[species][t] = sample[species][t]
                sample[species][t] = mtax
            else:
                sample[species][t] = x[Index[t]]
                mtax = x[Index[t]]

            population[species][t] = sample[species][t]
              
    else:
        for t in taxon:
            #y = Taxon[t]
            sample[species][t] = x[Index[t]]
	    population[species][t] = sample[species][t]
	    
    #for t in taxon:
        #y = Taxon[t]
    #    population[species][t] = x[Index[t]]


if len(duplicates) > 0:
    print "Population master list contains duplicates:"
    for i in duplicates: print i,'\n'

def PathLength(population):
    taxonN = {}
    
    X = {}
    for t in taxon:
        Taxon[t] = {}
        X[t] = [population[i][t] for i in sample]

	if taxon.index(t) == 0:
	    for i in set(X[t]):
	        Taxon[t][i] = X[t].count(i)
	else:
            for i in set(X[t]): 
                if i not in X[taxon[taxon.index(t)-1]]:
                    Taxon[t][i] = X[t].count(i)
        
        taxonN[t] = len(Taxon[t])

    n = [float(len(Taxon[t])) for t in taxon]
    
    n.insert(0,1.0)
        
    #s = 100/float(N)
    raw = []
    for i in range((len(n)-1)):
        j = i + 1
        
        if n[i] > n[j]:
            c = 1
        else:
            c = (1 - n[i]/n[j])

        raw.append(c)

    s = sum(raw)
    adjco = [i*100/s for i in raw]

    coef = {}; pathLengths = {}
    for i in range(len(taxon)):
        t = taxon[i]
        coef[t] = sum(adjco[i:])
        pathLengths[t] = adjco[i]

    return coef, taxonN, pathLengths

if pathlengths == 'n':
    coef, popN, pathLengths = PathLength(population)
if pathlengths == 'y':
    XXX, popN, YYY = PathLength(population)
    del XXX, YYY

#N = len(sample.keys())
def ATDmean(data,sample):
    #[sample = data.keys()
    N = len(sample)
    
    Taxon = {}; taxonN = {}; AvTD = 0; n = 0
    #Taxon are counts of taxa at each level, taxonN are numbers of pairwise differences
    #at each level, with n being the accumlation of pairwise differences at that level. the difference
    #between n and TaxonN is the number of species that are in different taxa in that level
    #but not in upper levels

    for t in taxon:
        Taxon[t] = {}
        x = [data[i][t] for i in sample]
        for i in set(x):
            Taxon[t][i] = x.count(i)

    for t in taxon:
        taxonN[t] = sum([Taxon[t][i] * Taxon[t][j] for i in Taxon[t] for j in Taxon[t] if i != j])
        n = taxonN[t] - n
        AvTD = AvTD + (n * coef[t]) 
        n = taxonN[t]

    #print sample
    AvTD /= (N * (N - 1))

    return AvTD,taxonN, Taxon

def ATDvariance(taxonN, sample, atd):
    vtd = []
    
    #N = sum(taxon)

    vtd = 0; N = 0; n = 0

    for t in taxon:
        n = taxonN[t] - n
        vtd = vtd + n * coef[t]**2 
        n = taxonN[t]

    N = len(sample)
    n = N * (N - 1)

    vtd = (vtd - ((atd*n)**2)/n)/n

    #vtd = (sum([tax1,tax2,tax3,tax4]) - (((atd * n)**2)/n))/n

    return vtd
    
def euler(data, atd, TaxonN):
    sample = data.keys()

    n = len(sample)
    TDmin = 0
    N = 0
    for t in taxon:
        k = len(Taxon[t])
        TDmin += coef[t] * (((k-1)*(n-k +1)* 2+ (k-1)*(k-2))-N)
        N += ((k-1)*(n-k +1)* 2 + (k-1)*(k-2))-N

    TDmin /= (n * (n-1))

    #Taxon = {}

    #tax = []

    #taxon.append('sample')
    #Taxon['sample'] = sample
    taxon.reverse()
    TaxMax = {}

    taxonN = {}
    import random
    for t in taxon:
        TaxMax[t] = []
        if taxon.index(t) == 0:
            TaxMax[t] = []
            for i in range(len(Taxon[t])):
                TaxMax[t].append([])
            for i in range(len(Taxon[t])):
                TaxMax[t][i] = [sample[j] for j in range(i,n,len(Taxon[t]))]
        else:
            TaxMax[t] = []
            for i in range(len(Taxon[t])):
                TaxMax[t].append([])
                s = taxon[taxon.index(t)-1]
                
                Tax = [TaxMax[s][j] for j in range(i,len(Taxon[s]),len(Taxon[t]))]

                for j in Tax:
                    TaxMax[t][i] += j
        TaxMax[t].reverse()
            
    taxon.reverse(); TDmax = 0; n = 0; N = len(sample)
    for t in taxon:
        taxonN[t] = sum([len(TaxMax[t][i]) * len(TaxMax[t][j]) for i in range(len(TaxMax[t])) for j in range(len(TaxMax[t])) if i != j])
        n = taxonN[t] - n
        TDmax += n * coef[t]
        n = taxonN[t]
        #for i in TaxMax[t]:
        #    print t, len(i)

    TDmax /= (N * (N-1))

    EI = (TDmax-atd)/(TDmax-TDmin)

    Eresults = {'EI':EI, 'TDmin':TDmin,'TDmax':TDmax}
    return Eresults
    #print TDmax

print "Output from Average Taxonomic Distinctness\n"
def Sample(samplefile):
    sample = {}
    print samplefile
    for i in open(samplefile):
        if match('Taxon:', i): continue
        elif match('Coefficients:', i): continue

        x = i.split()

        species = x[0]
        #sample[species] = {}

        sample[species] = population[species]

    return sample


results = {}

for f in Files:
    sample = Sample(f)
    f = f.split('.')
    f = f[0]
    
    results[f] = {}
    
    samp = sample.keys()
    
    atd,taxonN, Taxon = ATDmean(sample,samp)
    vtd = ATDvariance(taxonN,samp,atd)
    Eresults = euler(sample,atd, taxonN)
    
    results[f]['atd'] = atd
    results[f]['vtd'] = vtd
    results[f]['euler'] = Eresults
    results[f]['N'] = taxonN
    results[f]['n'] = len(sample)
    results[f]['taxon'] = Taxon

N = len(sample.keys())

def printResults():
    #if parameter == 'm':
    #if parameter == 'm':
    #    print "parameter is Average Taxonomic Distinctness\n"
    #elif parameter == 'v':
    #    print "parameter is Variation in Taxonomic Distinctness\n"
    #elif parameter == 'e':
    #    print "parameter is Euler's Index of Imbalance\n"
            
    print "Number of taxa and path lengths for each taxonomic level:"

    for t in taxon:
        print '%-10s\t%d\t%.4f' %(t,popN[t],pathLengths[t])
        n = taxonN[t]

    print "\n",

    for f in results:
        print "---------------------------------------------------"
        print "Results for sample: ", f,'\n'
        print "Dimension for this sample is", results[f]['n'], '\n\n',
        print "Number of taxa and pairwise comparisons  at each taxon level:"
            
        n = 0
        for t in taxon:
            
            N = results[f]['N'][t] - n
            print '%-10s\t%i\t%i' %(t,len(results[f]['taxon'][t]),N)
            n = results[f]['N'][t]

        print """\nNumber of pairwise comparisons is for pairs that differ \
at each level excluding comparisons that differ at upper levels"""
        print "\n", 
          
        print "Average taxonomic distinctness      = %.4f" % results[f]['atd']
        print "Variation in taxonomic distinctness = %.4f" % results[f]['vtd']
        print "Minimum taxonomic distinctness      = %.4f" % results[f]['euler']['TDmin']
        print "Maximum taxonomic distinctness      = %.4f" % results[f]['euler']['TDmax']
        print "von Euler's index of imbalance      = %.4f" % results[f]['euler']['EI']
        print '\n',


printResults()
print "---------------------------------------------------"

#sys.stdout = saveout

#sys.stdout=sys.__stdout__


sys.stdout = saveout
    
sys.stdout=sys.__stdout__

if ci == 'y':
    
    output = out.split('_')[0] + '_funnel.out'

    o = open(output,'a')
    
    saveout = sys.stdout
    sys.stdout = open(output, 'w')
    print """Confidence limits for average taxonomic distinctness and variation in taxonomic distinctness
limits are lower 95% limit for AvTD and upper 95% limit for VarTD
"""
    print "Number of permutations for confidence limits =", p, '\n'

    #if paramter == 'm':
    #    print "Confidence limits for Average Taxonomic Distinctiveness are in file ", output
    #if paramter == 'v':
    #    print "Confidence limits for Variation in Taxonomic Distinctiveness are in file ", output
   
    
    #o = open('sample2.txt','w')
    
    #saveout = sys.stdout
    #sys.stdout = open(output, 'w')
    
    ciarray = []; x = [];carray = []
    def Funnel(p,d1,d2):
        from random import sample
        pop = population.keys()
    
        dims = []; up = []; lo = []; means = []

        print "dimension AvTD05%   AvTDmean  AvTD95%   AvTDup    VarTDlow   VarTD05%   VarTDmean  VarTD95%"
        for d in range(d1, d2 + 1):
        #for i in range(10):
            #d = N
            #if d != N: continue
            #from math import max, min
            x.append(d)
            AvTDci = []; VarTDci = []
            for j in range(p):
                rsamp = sample(pop,d)
    
                atd,taxonN, Taxon = ATDmean(population,rsamp); AvTDci.append(atd)
                vtd = ATDvariance(taxonN,rsamp,atd); VarTDci.append(vtd)

            AvTDci.sort()
            VarTDci.sort()

            AvTD = AvTDci[int(.05 * p)], sum(AvTDci)/p, AvTDci[int(.95 * p)], max(AvTDci)
            VarTD = min(VarTDci), VarTDci[int(.05 * p)],sum(VarTDci)/p,VarTDci[int(.95 * p)] 
    
            dims.append(d)
            ciarray.append(AvTD[0])
            carray.append(AvTD[1])

            #up.append(ci95[1])
            #lo.append(ci95[0])
            #means.append(mean)
            print '%i        %6.4f   %6.4f   %6.4f   %6.4f   %6.4f   %6.4f   %6.4f   %6.4f' \
                %(d, AvTD[0], AvTD[1], AvTD[2], AvTD[3], VarTD[0], VarTD[1], VarTD[2], VarTD[3])
            
            #if d == N:
            #    Ie = (max(cache)-atd)/(max(cache)-min(cache))
            #    print d, Ie, ci95, mean
            
        #return dims, up, lo, means
            #print d,ci95
    
    Funnel(p,d1,d2)
    #dims, up, lo, means = Funnel(p,d1,d2)

    sys.stdout = saveout
        
    sys.stdout=sys.__stdout__
    
    #from QUASImage import *; from numpy import *
    #ciarray = array(ciarray)
    #from pgen import *

    #ciarray += carray

    #x *= 1
    #charplot(x,ciarray)

    #plot(ciarray)
"""
    from matplotlib.pylab import *
    
    if parameter == 'm':
        param = 'Average Taxonomic Distinctiveness'
    elif parameter == 'v':
        param = 'Variation in Taxnomic Distinctiveness'
    elif parameter == 'e':
        param = 'Imbalance'
    
    #N = len(sample)    
    #print N, atd
    #figure(1)
    plot(dims,up,dims, lo, dims, means)
    title('ATD',fontstyle='italic')
    xlabel('Number of Species')
    ylabel(param,fontstyle='italic')
    #savefig(figureOutput+".png")
    
    show()
    
    #sys.stdout = saveout
    
    #sys.stdout=sys.__stdout__
"""

