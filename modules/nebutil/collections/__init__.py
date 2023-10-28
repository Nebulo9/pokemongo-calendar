import copy
from typing import Any, Callable, Iterator, Optional, Sequence, Union, List
from .. import Serializable
class Collec(Serializable):
    def __init__(self,items:Union[Iterator[Any],Sequence[Any]]) -> None:
        self.__items = list(items)
        
    @property
    def items(self) -> List[Any]:
        """
        Returns the items of the collection.
        :returns: the items of the collection.
        :rtype: `list`
        """
        return self.__items
    
    @property
    def first(self) -> Any:
        """
        Returns the first item of the collection.
        :returns: the first item of the collection.
        :rtype: `Any`
        """
        return self.__items[0]
    
    @property
    def last(self) -> Any:
        """
        Returns the last item of the collection.
        :returns: the last item of the collection.
        :rtype: `Any`
        """
        return self.__items[-1]
    
    @property
    def size(self):
        """
        Returns the size of the collection.
        :returns: the size of the collection.
        :rtype: `int`
        """
        return len(self.__items)
    
    @items.setter
    def setItems(self,items):
        """
        Sets the items of the collection.
        :param items: the items of the collection.
        :type items: `list`
        """
        self.__items = items
        
    def filter(self,func:Callable[[Any],bool]):
        """
        Filters the collection using a function.
        :param func: the filter function.
        :type func: Callable[[Any],bool]
        :returns: the filtered collection.
        :rtype: `Collec`
        """
        return self.__class__(filter(func,self.__items))
    
    def sort(self,key:Optional[Callable[[Any],Any]],reverse:Optional[bool]):
        """
        Sorts the collection.
        :param key: the key to sort on.
        :type key: Optional[Callable[[Any],Any]]
        :param reverse: whether to reverse the order.
        :type reverse: Optional[bool]
        :returns: the sorted collection.
        :rtype: `Collec`
        """
        if key is None:
            if reverse is None:
                return self.__class__(sorted(self.__items))
            return self.__class__(sorted(self.__items,reverse=reverse))
        else:
            if reverse is None:
                return self.__class__(sorted(self.__items,key=key))
            return self.__class__(sorted(self.__items,key=key,reverse=reverse))
        
    def forEach(self,func:Callable[[Any],Any]):
        """
        Applies a function to each item of the collection.
        Does not change the collection.
        :param func: the function to apply.
        :type func: `Callable[[Any],Any]`
        """
        for event in copy.copy(self.__items):
            func(event)
           
    def __str__(self) -> str:
        return f"Collec(items={self.items})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __iter__(self):
        return iter(self.__items)
    
    def __len__(self) -> int:
        return len(self.__items)
    
    def __contains__(self, o: object) -> bool:
        return o in self.__items
    
    def __getitem__(self, key) -> Any:
        if isinstance(key,str):
             return NotImplemented
        return self.__items[key]
    
    def __add__(self, o: object):
        if isinstance(o,Collec):
            return self.__class__(self.items + o.items)
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
    
    def __sub__(self, o:object):
        if isinstance(o,Collec):
            return self.__class__([ev for ev in self.items if ev not in o.items])
        else:
            raise TypeError(f"unsupported operand type(s) for -: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
    
    def __and__(self, o: object):
        if isinstance(o,Collec):
            return self.__class__([ev for ev in self.items if ev in o.items])
        else:
            raise TypeError(f"unsupported operand type(s) for &: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
    
    def __or__(self, o: object):
        if isinstance(o,Collec):
            return self.__add__(o)
        else:
            raise TypeError(f"unsupported operand type(s) for |: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
    
    def __xor__(self, o: object):
        if isinstance(o,Collec):
            return Collec([ev for ev in self.items if ev not in o.items] + [ev for ev in o.items if ev not in self.items])
        else:
            raise TypeError(f"unsupported operand type(s) for ^: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
    
    def __radd__(self, o: object):
        if isinstance(o,Collec):
            return self + o
        else:
            raise TypeError(f"unsupported operand type(s) for +=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
    
    def __rsub__(self, o:object):
        if isinstance(o,Collec):
            return o - self
        else:
            raise TypeError(f"unsupported operand type(s) for -=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
    
    def __rand__(self, o: object):
        if isinstance(o,Collec):
            return self & o
        else:
            raise TypeError(f"unsupported operand type(s) for &=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
    
    def __ror__(self, o: object):
        if isinstance(o,Collec):
            return self | o
        else:
            raise TypeError(f"unsupported operand type(s) for |=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
    
    def __rxor__(self, o: object):
        if isinstance(o,Collec):
            return self ^ o
        else:
            raise TypeError(f"unsupported operand type(s) for ^=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o,Collec):
            return self.items == o.items
        else:
            return False
    
    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)
    
    def __hash__(self) -> int:
        return hash(self.__items)
    
    def __bool__(self) -> bool:
        return bool(self.__items)
