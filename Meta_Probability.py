from random import uniform
import matplotlib.pyplot as plt
from functools import wraps

plt.style.use('ggplot')

'''Using Descriptors to complete the TypeChecking - more elegant but less explicit approach.'''
class Descriptor_:
    ## The Descriptor Class can be summarised as a fine-grain redefinition of the dot: it is not applied uniformally but individually to specifically chosen fields.

    def __init__(self, name = None):
        self.name = name

    def __get__(self, instance, cls):
        return instance.__dict__[self.name]

    ## Override the procedure of setting a value to the respective field (displacing the inherited logic from the Object Class).
    ## Will only set the value passed to the corresponding field if the value satisfies all imposed checks. If not, an error will raised.
    ## Distinguish between __setattr__() by being able to modify any Class's field.
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        print("Delete", self.name)
        del instance.__dict__[self.name]

## One feature that can be built into the Descriptor Class is a Type Check system that will displace the ubiquitous conditional statements required inside a Class's Constructor.
class TypeChecked(Descriptor_):
    ## Everything in Python is an Object. Therefore, use as the base such that the Class can be inherited and specialised to any Type Check. 
    ty = object

    def __set__(self, instance, value):
        ## Before setting a value against a specific field determine if its the permissable Type.
        if not isinstance(value, self.ty):
            raise TypeError (f"Expected {self.ty} for field: {self.name}.")
        else:
            super().__set__(instance, value)

## Inherit the above framework through the MRO but update the field 'ty' to account for the Type being validated against.
class List(TypeChecked):
    ty = list

## The Method Resolution Order will ensure that the List is validated first before determining whether every element inside the List is an Integer.
class _Integers(Descriptor_):

    ## The "value" argument will, as validated by the previous Class, be a List.
    def __set__(self, instance, value):
        if not (all(list(map(lambda arg: isinstance(arg, int), value)))):
            raise TypeError("The List passed must consist of all Integer Values.")
        super().__set__(instance, value)

class _Probabilities(Descriptor_):
    
    def __set__(self, instance, value):
        try:
            _sum = sum(value)
        except TypeError as err:
            print(f"Probabilities required: {err}.")
            raise
        else:
            if abs(_sum - 1.0) < 0.0001:
                super().__set__(instance, value)
            else:
                raise ValueError("Must be within Epsilon of 1.0.")


## Combine the two Type Checks into a single Descriptor.
class List_Integers(List, _Integers):
    pass

## Alternative approach to defining the above Class. The second parameter will represent the inheritance structure and the third parameter is a dictionary of the Class's methods.
List_Integers_ = type('List_Integers_', (List_Integers, ), {})

class List_Probabilities(List, _Probabilities):
    pass


'''Using a Decorator to indicate which function has been called in the Procedural Section of the Code.'''
## Utilise a prefix to distinguish each function. This is a boon when trying to isolate an error in procedural code.
def debug(prefix = ' '):
    ## The function debug() will return a Decorator having defined the prefix inside the Enclosing Scope. The argument, 'prefix', will be accessible inside the entire scope of the constructed wrapper.

    def decorator(func):
        ## The method __qualname__() will display the name of a user-defined function or Class.

        ## The prefix passed can only be of Type String.
        if isinstance(prefix, str):
            try:
                msg = prefix + func.__qualname__
            except AttributeError:
                print(f"Method not found on: {func}.")
        else:
            msg = func.__repr__()
            
        ## It is required because the Decorator has been extended to a three-level procedure. Therefore, to preserve the ability for the operations to work from a single call, use FuncTool's method 'wraps'.
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(msg)
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
## The purpose of any Decorator is to wrap a function in additional functionality: the original function will be returned having engaged the additional logic.


'''Logic Class representing the Random Variable.'''
## The Class will be able to handle any number of Integers with the assigned probabilities representing a Probability Mass Function, finite sample space.
class RandomGen(object):

    def __init__(self, elements, probabilities):
        self.elements = elements
        self.probabilities = probabilities
        self.l_elem = len(elements)
        self.l_prob = len(probabilities)

    def list_tuple(self):
        if (self.l_elem == self.l_prob):
            return list(zip(self.elements, self.probabilities))
        else:
            raise ValueError("Expecting to map each element to a probability.")

    def next_num(self):
        list_ = self.list_tuple()
        r = uniform(0, 1)
        cdf = 0
        ## Iterate through the List consisting of each element from the finite sample space with the associated probability wrapped in a tuple.
        for item, prob in list_:
            cdf += prob
            if cdf >= r:
                return item
        return item

    ## By using a Generator it potentially avoids any wastage of memory by avoiding assignment to a variable and subsequently occupying Cache, or storing each computed value in a List.
    ## It should be noted that iterating through a Generator is slower than a List as the List is stored in memory. This discrepancy is amplified when comparing against an Array which will benefit from Spatial Locality.
    def generator_next(self, n):
        for i in range(n):
            yield self.next_num()

    def get_elements(self):
        return self.elements

    def get_probabilities(self):
        return self.probabilities
    

## Will inherit the Constructor from the Parent Class which will set the fields to the respective attributes passed.
## The subclass will control the application of the Descriptors to complete the Type Checking.
class RV(RandomGen):
    elements = List_Integers_('elements')
    probabilities = List_Probabilities('probabilities')


## The second parameter will be an instance of the above Class, "RV".
## Keep the below subroutines out of the Class, as the Class represents a Random Variable. Therefore, not technically part of its body of logic.
def generator_(n, data):
    keys = [str(_) for _ in data.get_elements()]
    dict_ = dict(zip(keys, [0 for _ in keys]))
    for i in range(n):
        output = data.next_num()
        dict_[str(output)] += 1
    return dict_

## Second implementation using the module consisting of a Generator.
@debug(prefix = "Decorator - Using the Class's method that consists of a Generator: ")
def generator(n, data):
    keys = [str(_) for _ in data.get_elements()]
    dict_ = dict(zip(keys, [0 for _ in keys]))
    nums = data.generator_next(n)

    ## Greater number of Loops but lower memory impact.
    for elem in nums:
        dict_[str(elem)] += 1
    return dict_

'''Display the Output.'''
def bar_chart(dict_, data):
    x = list(zip(dict_.keys(), data.get_probabilities()))
    numeracy = list(dict_.values())

    x_pos = [i for i, _ in enumerate(x)]
    plt.bar(x_pos, numeracy, color = "blue")
    plt.xlabel("Elements and Associated Probability")
    plt.ylabel("Count")
    plt.title("Random Generator")

    plt.xticks(x_pos, x)
    plt.show()

'''Unit Tests.'''
def test_sum(dict_, n):
    assert sum(dict_.values()) == n, f"Should equal {n}."

def prob_sum(dict_, n):
    probabilities = [(v / n) for v in dict_.values()]
    assert abs(sum(probabilities) - 1.0) < 0.00001, f"Should equal 1.0, or within epsilon." 

## If N, the sample size, tends to infinity, the number of times each element is generated, in the sample, should converge to the real probability, from the distribution, according to the Law of Large Numbers.
## Therefore, the below Unit Test is only applicable under Asymptotic Conditions.
def probability(dict_, n, prob_):
    output = [(v / n) for v in dict_.values()]
    for i, _ in enumerate(prob_):
        print(f"Actual probability: {_}.")
        print(f"Computed probabily: {output[i]}.")
        print(f"Difference: {abs(_ - output[i])}.")
        assert abs(_ - output[i]) < 0.15, f"The number of counts obtained for the element is too improbable under Asymptotic Conditions."

'''Test Case.'''
if __name__ == '__main__':
## If there is an imbalance with the number of finite elements and the associated probability, the error will only be generated once the user tries to generate values from the Random Variable.
    elements = [-1, 0, 1, 2, 3]
    probabilities = [0.01, 0.3, 0.58, 0.1, 0.01]
    
    n = 100000
    ## Instantiate an instance of the user-defined RV Class.
    inst = RV(elements, probabilities)
    dict_ = generator(n, inst)
    print(dict_)

    ## Unit Tests.
    test_sum(dict_, n)
    prob_sum(dict_, n)
    ## As discussed above, only applicable for a large sample size.
    if n > 100000:
        probability(dict_, n, probabilities)
    bar_chart(dict_, inst)
