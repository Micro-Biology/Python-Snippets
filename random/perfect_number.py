def get_factors(x):
    factors = []
    for y in range(1,int(x)):
        z = x / y
        if is_whole(z) == True:
            factors.append(y)
    return factors
    
def is_whole(x):
    if x % 1 == 0:
        return True
    else:
        return False
        
def sum_list(lst):
    total = 0
    for x in lst:
        total = total + x
    return total
    
def is_perfect(i):
    factors = get_factors(i)
    if i == sum_list(factors):
        return True
    else:
        return False
    
assert get_factors(100) == [1,2,4,5,10,20,25,50]
assert is_whole(10) == True
assert is_whole(10.0000001) == False
assert sum_list([1,2,4,5,10,20,25,50]) == 117
assert is_perfect(6) == True

def main():
    i = 2
    while True:
        factors = get_factors(i)
        if i == sum_list(factors):
            print(str(i) + " is perfect")
        i=i+2
    
if __name__ == "__main__":
    main()
