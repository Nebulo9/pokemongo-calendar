from typing import Any, Dict
class Serializable:
    @staticmethod
    def serialize(o:Any):
        """
        Serializes an object.
        :param o: the object to serialize.
        :type o: Any
        :returns: the serialized object.
        :rtype: Any
        """
        if isinstance(o, Serializable):
            # Remove the class name from each key
            return {k.strip(f'_{o.__class__.__name__}__'): v for k, v in o.__dict__.items()}
        raise TypeError("Object of type %s is not JSON serializable" % type(o))
    
def serializer(o:Any) -> Dict[str,Any]:
    if isinstance(o,Serializable):
        return Serializable.serialize(o)
    raise TypeError("Object of type %s is not JSON serializable" % type(o))