'''
Created on Mar 21, 2016

@author: Luke
'''

from sfc.sfcfactory import SFCFactory

#===============================================================================
# DEMOS
# The run function here demonstrates a few uses of the SFC Factory API.
#===============================================================================

def run():
    
    #===========================================================================
    # StudentFunctionCaller > StudentDeserializeLocationCaller
    #
    # Here we create and use a caller for the deserialized_location function.
    # To call it, instantiate and use the call method with keyword arguments.
    #===========================================================================
    
    SDLC = SFCFactory.sfc(name = 'StudentDeserializeLocationCaller',
                          sfn = deserialize_location,
                          required = ['location_str'])
    
    loc = SDLC().call(location_str = '2,4')
    
    #===========================================================================
    # StudentMethodCaller > StudentLocationEqCaller
    #
    # Here we create and use a caller for the Location.__eq__ method.
    # To call methods, a 'sobj' (student object) argument must also be passed
    # for the instance parameter (conventionally called self); it does not have
    # to be a keyword argument. The rest is the same as for functions.
    #===========================================================================
    
    SLEC = SFCFactory.smc(name = 'StudentLocationEqCaller',
                          sfn = Location.__eq__,
                          required = ['other'])
    
    sobj = Location(2, 4)
    is_equal = SLEC().call(sobj, other = Location(3, 5))
    
    #===========================================================================
    # StudentObjectMaker > StudentRiderMaker
    #
    # Here we create and use a maker for the Rider class.
    # To create a Rider instance, we instantiate and use make.
    # Note that we use the optional 'possible' argument here. This represents
    # parameters we think the student may use even though they don't need to,
    # and the default argument we would like to pass if it is required.
    #===========================================================================
    
    SRM = SFCFactory.som(name = 'StudentRiderMaker',
                         stype = Rider,
                         required = ['identifier', 'patience', 'origin',
                                   'destination'],
                         possible = {'status': WAITING})
    
    rider = SRM().make(i = 'A', p = 5, o = Location(2,4), d = Location(3,5))
    
    return loc, is_equal, rider

#===============================================================================
# IFFY STUDENT CODE FOR DEMOS
# Pulled from real life. :)
#===============================================================================

WAITING = "waiting"
CANCELLED = "cancelled"
SATISFIED = "satisfied"

class Rider:
    def __init__(self,id,location,destination,patience):
        '''
        Initializes a Rider
        @type self:Rider
        @type id:int
        @type location:Location
        @type destination:Location
        @type patience:int
        '''


        self.origin=location
        self.status=WAITING
        self.destination=destination
        self.patience=patience
        self.id=id

    # TODO
    pass
    def  __repr__(self):
        '''
        return a string representation of the Rider
        @type self:Rider
        '''

        return self.id

class Location:
    def __init__(self, row, column):
        """Initialize a location.

        @type self: Location
        @type row: int
        @type column: int
        @rtype: None
        """
        # TODO
        self.row=row
        self.column=column

    def __eq__(self, other):
        """Return True if self equals other, and false otherwise.
        @type self:Location
        @type other:Location
        @rtype: bool
        """
        # TODO
        return self.row==other.row and self.column==other.column

def deserialize_location(location_str):
    """Deserialize a location.

    @type location_str: str
        A location in the format 'row,col'
    @rtype: Location
    """
    # TODO
    return Location(int(location_str.split(",")[0]),
                    int(location_str.split(",")[1]))
