# -*- coding:utf-8 -*-
# Python2.7.12

from math import log
import operator


#第一步准备数据（1）：准备数据集
def createDataSet():
    
    #测试数据
    dataSet = [[1, 1, 'yes'],
               [1, 1, 'yes'],
               [1, 0, 'no'],
               [0, 1, 'no'],
               [0, 1, 'no']]
    
    #属性名称集合
    labels = ['no surfacing', 'flippers']
    
    return dataSet, labels

#第二步分析数据（1）：计算给定数据集的香农熵
def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:
        
        #为所有可能分类创建字典
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
        
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key]) / numEntries
        
        #以2为底求对数
        shannonEnt -= prob * log(prob,2)
        
    return shannonEnt


#第二步分析数据（2）：划分数据集
#dataSet 待划分的数据集
#axis    划分数据集的特征
#value   特征值
def splitDataSet(dataSet, axis, value):
    
    #创建新的list对象
    retDataSet = []

    #遍历特征
    for featVec in dataSet:
        
        #抽取指定特征的数据
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]
            reducedFeatVec.extend(featVec[axis+1:])
            #print featVec
            #print reducedFeatVec
            retDataSet.append(reducedFeatVec)
            
    return retDataSet

#第二步分析数据（3）：选择最好的数据集划分方式
# return 最好划分特征的索引值
def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0
    bestFeature = -1
    #print 'baseEntropy is %f' %baseEntropy
    for i in range(numFeatures):
        
        #创建唯一的分类标签列表
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        
        newEntropy = 0.0
        
        #计算每种划分方式的信息熵
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i , value)
            prob = len(subDataSet)/float(len(dataSet))
            cst = calcShannonEnt(subDataSet)
            newEntropy += prob * cst
            #print 'the %d feature, value is %s, prob is %f, cst is %f, newEntroy is %f' \
            #%(i, value, prob, cst, newEntropy)
        infoGain = baseEntropy - newEntropy

        #计算最好的信息增益
        if(infoGain > bestInfoGain):
            bestInfoGain = infoGain
            bestFeature = i
            
    return bestFeature

#第三步训练算法（1）：构建决策树的工具方法
#当数据集已经处理了所有属性，但是类标签不唯一时，采用多数表决法决定叶子节点的分类
def majorityCnt(classList):
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.iteritems(),key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

#第三步训练算法（2）：递归构建决策树
def createTree(dataSet, labels):
    #复制类标签
    #在Python语言中函数参数是列表类型时，参数是按照引用方式传递的
    #为了保证每次调用函数createTree()时不改变原始列表的内容，使用
    #新变量subLabels代替原始列表
    newLabels = labels[:]
    classList = [example[-1] for example in dataSet]
    
    #类型完全相同则停止继续划分
    if classList.count(classList[0]) == len(classList):
        return classList[0]

    #遍历完所有特征时返回出现次数最多的
    if len(dataSet[0]) == 1:
        return majorityCnt(classList)
    
    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = newLabels[bestFeat]
    
    myTree = {bestFeatLabel:{}}
    del(newLabels[bestFeat])
    
    #得到列表包含的所有属性值
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    
    for value in uniqueVals:
        
        #subLabels = newLabel[:]
        
        #递归
        myTree[bestFeatLabel][value] = createTree(splitDataSet\
                                                  (dataSet, bestFeat, value), newLabels)
    return myTree
    
#第四步测试算法：使用决策树的分类函数
#inputTree 第三步构建的决策树
#featLabels 属性名称集合
#testVec   测试数据，是一个列表，与训练数据的区别是不包含标签
def classify(inputTree, featLabels, testVec):
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]

    #将标签字符串转换为索引
    featIndex = featLabels.index(firstStr)
    
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':

                #递归分类
                classLabel = classify(secondDict[key], featLabels, testVec)
            else:
                classLabel = secondDict[key]
    return classLabel

#第五步使用算法（1）:存储决策树
def storeTree(inputTree, filename):
    import pickle
    fw = open(filename, 'w')
    pickle.dump(inputTree, fw)
    fw.close()

#第五步使用算法（2）:读取决策树
def grabTree(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)
