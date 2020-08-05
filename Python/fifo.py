# First-In First-Out buffer (FIFO)
# implemented by wrapping the "deque" double ended queue
# Added functionalies are:
# (a) controlled resizing of the queue
# (b) providing statistics

from collections import deque
import statistics as stat


class fifo:
    # Create a new FIFO (bases on collections.deque) with up to <size> items
    def __init__(self, size=1) :
        self.data = deque([], maxlen=size)

    # add a new item to the "left" (="in") of the FIFO
    def put(self, item) :
        self.data.appendleft(item)
        
    # return all items as a list       
    def all(self) :
        return list(self.data)
      
    # return the number of items currently in the FIFO (identical to len() )
    def num(self) :
        return len(self.data)
    
    # return the number of items currently in the FIFO (identical to num() )
    def len(self) :
        return len(self.data) # notice the namespaces ...
    

    # resize the FIFO, relying on a temporary copy:
    # if the new size is bigger, all data will be transferred
    # if the new size is smaller only the "last in" items still fitting are transferred
    def dim(self, size) :
        if self.data.maxlen == size : # size OK, no action required
            return
        old = self.data
        oldlen = len(self.data)
        del self.data
        if oldlen <= size : # increase size
            self.data = deque(old, maxlen=size) # take all the available data into the new buffer
        else : # decrease size
            self.data = deque([], maxlen=size)     
            for i, e in enumerate(old) :
                if i >= size :
                    break
            self.data.append(e)
        del old


    # return the sum of all items (for numerical values)
    def sum(self) :
        return sum(self.data) # notice the namespaces ...
      
    # return the arithmetical average of the items
    # in case of no data (undefined) zero is returned.
    def avr(self) :
        n = len(self.data)
        if n<1 :
            return 0.0
        return sum(self.data)/float(n)
      
    # return the standard deviation as defined by the statistics module
    # in case of <2 items, zero is returned.
    def stdev(self) :
        if len(self.data) < 2 :
            return 0
        return stat.stdev(self.data)
      
