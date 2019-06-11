'''
Created on Feb 21, 2016
Updated on Mar 21, 2016

@author: Luke
'''

import inspect
from difflib import SequenceMatcher

class Calibrator(object):
    """
    Given a list of expected parameter names, this class provides tools to
    make a good guess at matching them to the actual parameter names.
    """
        
    def _get_spellings(self, base: str) -> list:
        """
        Yield the segments of base of each possible length.
        """
        
        for i in range(len(base), 0, -1):
            yield(base[:i])
            
        
    def _get_best_shot(self, word: str, opts: list) -> float:
        """
        Return the highest similarity score of any string in opts when
        compared to word.
        """
        
        # Signaturize as uppercase
        word = word.upper()
        opts = [opt.upper() for opt in opts]
        
        return max([SequenceMatcher(None, word, opt).ratio() for opt in opts])
    
    
    def calibrate_args(self, actual: list, expected: list) -> dict:
        """
        Return a dictionary representing the best guess at a correspondence
        between the expected argument names and the actual ones.
        """
        
        # Initialize the eventual key and a dict of names to possible spellings
        key = {name: '' for name in expected}
        name_to_spellings = {name: list(self._get_spellings(name)) \
                             for name in expected}
        
        # Do the initial matching: if the argument matches a possible spelling
        # of a given name, assign it to that.
        
        for arg in actual:
            for name, spellings in name_to_spellings.items():
                
                u_arg = arg.upper()
                u_spellings = [w.upper() for w in spellings]
                
                if u_arg in u_spellings:
                    key[name] = arg
                    break
        
        # For any args that weren't a possible spelling of a known name,
        # assign each to the name that (a) the arg is most similar to and
        # (b) doesn't already have a match.
        
        unused_args = [arg for arg in actual if arg not in key.values()]
        for arg in unused_args:
            sims = {name: self._get_best_shot(arg, spellings) \
                    for (name, spellings) in name_to_spellings.items()}
            sims = sorted(sims.items(), key=lambda x: x[1], reverse=True)
            
            for name, _ in sims:
                if not key[name]:
                    key[name] = arg
                    break
        
        return key
    
    
    def calibrate_fn(self, fn: callable, expected: list) -> dict:
        """
        Return a dictionary representing the best guess at a correspondence
        between the expected argument names and the actual ones fn accepts.
        """
        
        # Find the arguments from the function
        argspec = inspect.getfullargspec(fn)
        args = argspec.args
        
        # Calibrate as list
        return self.calibrate_args(args, expected)
    