#coding=utf-8
#!/usr/bin/python

import operator

#items中n个元素排列
def permutation(items, n):
    if (n > len(items)) or (n <= 0) or (len(items) == 0):
        return
    if n == 1:
        for i in range(len(items)):
            yield [items[i]]
    else:
        for i in items:
            st = list(items)
            st.remove(i)
            for j in permutation(st, n-1):
                yield [i] + j


#items中n个元素组合
def combination(items, n):
    if (n > len(items)) or (n <= 0) or (len(items) == 0):
        return
    if n == 1:
        for i in items:
            yield [i]
    else:
        for i in range(len(items)):
            for j in combination(items[i+1:], n-1):
                yield [items[i]] + j


def SET(n,i,MASK):
    """将整数n的第i位置1
    """
    return (n | (1 << i)) & MASK


def C(n,m):
    return  reduce(operator.mul, range(n - m + 1, n + 1)) /reduce(operator.mul, range(1, m +1))

def fac(n):
    return reduce(operator.mul, range(1,n+1))  


if __name__ == "__main__":
    """
    for i in combination([1,2], 2):
        print 'i--------',i
        for j in [1,2]:
            for k in combination(i,j):
                print k 
    a =  [l for l in permutation([1,2,3,4,5,6,7,8,9,10,11],3)]
    print len(a),'\n'
    print a
    #print [l for l in combination([1,2,3],2)]
    """
    print C(11,8)
    print C(11,5)
    print C(5,5)
    print C(4,5)
