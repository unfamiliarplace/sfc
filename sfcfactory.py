"""
StudentFunctionCaller Factory
@author: Luke Sawczak
March 21, 2016
"""
__version__ = '1.1.1'

"""
The StudentFunctionCaller Factory is a suite of extensible classes that serve
to reconcile the gap between parameters that comp sci instructors expect their
students will use in their design exercises, and those that the students have
actually used. This allows the programmatic testing of large numbers of student
submissions with an arbitrary degree of conformity to expectations.

There are three main extensible classes:
(1) StudentFunctionCaller: For aligning and calling module-level functions
(2) StudentMethodCaller: For aligning and calling object member methods
(3) StudentObjectMaker: For instantiating objects with unknown constructors

The API provides parallel static methods for extending these classes:
(1) StudentFunctionCaller: SFCFactory.sfc
(2) StudentMethodCaller: SFCFactory.smc
(3) StudentObjectMaker: SFCFactory.som

Once created, the children of these classes can be used with simple methods:
(1) StudentFunctionCaller: call. Pass keyword arguments
(2) StudentMethodCaller: call. Pass an instance (for self) + keyword arguments
(3) StudentObjectMaker: make. Pass keyword arguments for init (without self)

To extend a class, very little is required: a name for the class; the function,
method, or object to align; a list of required parameters; and a dictionary
mapping possible parameters a student might have used unnecessarily to the
default values they should have. The latter two items may be omitted and the
last one usually is.

Some parameter name configurations are so wildly off as to make even the best
guess a mismatch, generating a TypeError. The function and method callers do no
error-handling; the object maker returns an instance of UninstantiatedX,
where X is the name of the class that could not be instantiated.

This library also includes a Calibrator class, the engine that matches expected
parameter names to actual ones. Although a public API has not been provided, it
could easily be written as an extension of its fairly outward-facing structure.

Demonstrations of how to use these extensible classes can be found in demos.py.
"""

#===============================================================================
# IMPORTS
#===============================================================================

from sfc.calibrator import Calibrator
from random import sample
import inspect

#===============================================================================
# CONSTANTS
#===============================================================================

# Some functions are constructors for objects. They need an argument passed for
# the type definition to be properly instantiated. This constant gives a name
# reserved for that argument (should be guaranteed unique and impossible to
# mis-identify as any actual argument).
STYPE_ARG = '_sfc_stype_arg_' + ''.join(sample([str(n) for n in range(99)], 9))

# Similar for a self object in the case of member functions.
SSELF_ARG = '_sfc_sself_arg_' + ''.join(sample([str(n) for n in range(99)], 9))

#===============================================================================
# FACTORY API
#===============================================================================

class SFCFactory(object):
    """
    Public API for creating StudentFunctionCaller, StudentMethodCaller, and
    StudentObjectMaker objects.
    """

    @staticmethod
    def sfc(name: str, sfn: callable, required: list=[], possible: dict={}):
        """
        Return a child of StudentFunctionCaller for the given student function.
        """
        
        namespace = {'sfn': sfn, 'required': required, 'possible': possible}
        return type(name, (StudentFunctionCaller,), namespace)
    
    @staticmethod
    def smc(name: str, sfn: callable, required: list=[], possible: dict={}):
        """
        Return a child of StudentMethodCaller for the given student method.
        """
        
        namespace = {'sfn': sfn, 'required': required, 'possible': possible}
        return type(name, (StudentMethodCaller,), namespace)
    
    @staticmethod
    def som(name: str, stype: type, required: list=[], possible: dict={}):
        """
        Return a child of StudentObjectMaker for the given student class.
        """
        
        namespace = {'stype': stype, 'required': required, 'possible': possible}
        return type(name, (StudentObjectMaker,), namespace)

#===============================================================================
# STUDENTFUNCTIONCALLER
#===============================================================================

class StudentFunctionCaller(object):
    '''
    Wrapper for calling student functions using their actual parameter names.
    Should be inherited as follows: regular functions from this; object methods
    from StudentMethodCaller; object constructors from StudentObjectMaker.
    
    N.B. Uses a static function definition so that all functions, whether they
    are members or not, can be called without passing this instance as the
    first parameter (conventionally 'self').
    '''
    
    # Calibrator to use for aligning parameter names
    c = Calibrator()
    
    # Abstracts for the real values defined in child classes
    
    @staticmethod
    def sfn(**kwargs): pass
    required = []
    possible = {}
    
    # Added 1.1.1: optional separate function just for inspecting, not calling
    
    sfn_inspect = None
    
    
    def call(self, *args, **kwargs) -> object:
        """
        Call the student function with the keyword arguments from the caller.
        Return whatever it returns.
        
        If the function is uncallable, leave error handling to the client.
        """
        
        # Replace the reserved self arg with one that will be correctly ID'd
        if SSELF_ARG in kwargs:
            sobj = kwargs.pop(SSELF_ARG)
            kwargs['self'] = sobj
        
        # Get student versions of names        
        all_params = self.required + list(self.possible.keys())
        
        #  Use the special inspect-only function if it has been specified
        if self.sfn_inspect:
            student_names = self.c.calibrate_fn(self.sfn_inspect, all_params)
        else:
            student_names = self.c.calibrate_fn(self.sfn, all_params)
        
        # Match the names this function was called with against required names
        tester_names = self.c.calibrate_args(list(kwargs.keys()),self.required)
        tester_names = {v: k for k, v in tester_names.items()}
        
        # Prepare the kwargs we'll create the student object with
        student_kwargs = {}
        
        # Prepare the required parameters
        for argn, argv in kwargs.items():
            tester_name = tester_names[argn]
            student_name = student_names[tester_name]
            student_kwargs[student_name] = argv
        
        # Prepare the possible parameters, which have default values
        for name, default_value in self.possible.items():
            if student_names.get(name):
                student_kwargs[student_names.get(name)] = default_value
        
        # Call using the derived arguments
        # The client of this class is responsible for handling a TypeError!
        return type(self).sfn(**student_kwargs)
            
#===============================================================================
# STUDENTMETHODCALLER
#===============================================================================

class StudentMethodCaller(StudentFunctionCaller):
    '''
    Wrapper for calling student instance methods using their parameter names.
    There is no need to pass 'self' as a required argument.
    '''
    
    def __init__(self):
        """
        Add 'self' to the required argument list if it was not included.
        """
        
        # Add the self instance arg to the required list if it's not included
        if 'self' not in self.required:
            self.required.append('self')
        

    def call(self, sobj, **kwargs) -> object:
        '''
        Call the member function with the keyword arguments from the caller,
        using sobj for the instance of the object whose method is needed.
        Return whatever it returns.
        
        To avoid a conflict with the positional argument, do not pass a keyword
        arg 'self'.
        
        If the method is uncallable, leave error handling to the client.
        '''
        
        kwargs[SSELF_ARG] = sobj
        return super().call(**kwargs)
    
#===============================================================================
# STUDENTOBJECTMAKER
#===============================================================================

class StudentObjectMaker(StudentFunctionCaller):
    '''
    Wrapper for making student objects using whatever parameter names they used.
    
    object.__init__ requires the self parameter. However, the normal syntax for
    object instantiation omits it. A client of this class omits it too.
    '''
    
    # Abstract for the real value defined in child classes
    stype = type(None)
    

    def __init__(self):
        """
        Prepare the uninstantiated object and the instantiator for the student
        object, and add the student type argument to the required list.
        """
        
        # Save the type, create uninstantiated version
        self.uobj = self._get_uninstantiated_object()
        
        # Register the inspect-only __init__ (our initiator has a different
        # signature and hence cannot be inspected for its parameter names)
        self.sfn_inspect = self.stype.__init__
        
        # Instantiate the StudentFunctionCaller with the initiator
        type(self).sfn = self._get_instantiator()
        
        # Add the class type arg to the required list
        self.required.append(STYPE_ARG)
        
    
    def _get_instantiator(self) -> 'function':
        """
        Create a function that can instantiate and return the student object
        (__init__ does not return).
        """
        
        # The student type will end up being passed as an argument named 'self'
        def ins(**kwargs):
            stype = kwargs['self']
            del kwargs['self']
            return stype(**kwargs)
        
        return ins
    
    
    def _get_uninstantiated_object(self) -> 'Uninstantiated':
        """
        Return an "uninstantiated" dummy of the student type, to be returned
        whenever the student type object cannot be instantiated. This object is
        a child of Uninstantiated.
        """
                
        # Get the name for the dynamic class
        typestr = str(self.stype)        
        start = typestr.rfind("class '") + 7
        end = typestr.rfind("'")
        name = typestr[start:end]
        
        # Create the dynamic class
        utype = type('Uninstantiated' + name, (Uninstantiated,), {})
        
        # Instantiate
        return utype(name)
    
    
    def make(self, **kwargs) -> object:
        """
        Return a student object made with the keyword arguments from the caller.
        If it's impossible to create one, return an uninstantiated version.
        """
        
        # Pass the student type as a kwarg, to be used by the instantiator
        try:
            kwargs[STYPE_ARG] = self.stype
            sobj = super().call(**kwargs)
        
        # TypeError means the parameters couldn't be matched to the actual ones
        except TypeError as e:
            print(e)
            sobj = self.uobj
            
        return sobj
    
    
class Uninstantiated(object):
    """
    Superclass for the uninstantiated version of the student object.
    """
    
    message = '<Failure to instantiate {} due to unexpected parameters>'
    
    def __init__(self, name: str):
        """
        Set self.name to name.
        """
        
        self.name = name
        
    def __repr__(self) -> str:
        """
        Return the string representation of this uninstantiated object.
        """
        
        return self.message.format(self.name)
    