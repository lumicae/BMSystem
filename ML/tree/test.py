# -*- coding:utf-8 -*-
# Python2.7.12

import trees
import treePlotter

reload(trees)
reload(treePlotter)
def test():
    fr = open('lenses.txt')
    lenses = [inst.strip().split('\t') for inst in fr.readlines()]
    lensesLabels = ['age', 'prescript', 'astigmatic', 'tearRate']
    lensesTree = trees.createTree(lenses, lensesLabels)
    #treePlotter.createPlot(lensesTree)
    result = trees.classify(lensesTree, lensesLabels, ['young','myope', 'no', 'normal'])
    print result
    
if __name__ == '__main__':
    test()
