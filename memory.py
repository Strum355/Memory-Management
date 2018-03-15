from dlinkedlist import DLinkedList as dll
from math import ceil, log

class Memory:
    def __init__(self):
        self._page_size = 4
        self._list = dll()
        self._next_num = 0
        self.step = 0
        self.make_blocks(64, 4)
        self.make_blocks(32, 8)
        self.make_blocks(16, 16)
        self.make_blocks(8, 32)
        #self.make_blocks(4, 64)
        self.size = self._size()
        self._curr_pages = set()
        self._swap = Swap()
   
    def make_blocks(self, count, size):
        for i in range(count):
            isfirst = False if i & 1 else True
            b = Block(size, isfirst, self._next_num, self, self.step)
            self._list.add_last(b)
            self.increment_id()

    def _size(self):
        from functools import reduce
        return str(reduce((lambda curr, next: int(curr) + next.size), (x.element for x in iter(self._list))))+"KB"

    def request(self, size, pid):
        power = max(self._poweroftwo(size), self._page_size)
        best, oldest = None, None
        for block in self._list:
            if block.element.free and block.element.size >= size:
                if best == None or best.element.size > block.element.size:
                    best = block
            if (oldest == None or block.element.access_time < oldest.element.access_time) and block.element.initial >= power:
                oldest = block
        print(best, ", ", oldest)
        if not best:
            best = oldest
            next_to_swap = best.next
            self._swap_out(best.element)
            while not best.element.size == power:
                print(next_to_swap)
                self._swap_out(next_to_swap.element)
                next_to_swap = next_to_swap.next
        best.element.allocate(size, power, best, pid)

    def _swap_out(self, old):
        print("swapping out", old)
        self._swap.put(old)
        old.deallocate()

    def _poweroftwo(self, x):
        return 2**ceil(log(x)/log(2))

    def increment_id(self):
        self._next_num += 1

    def __str__(self):
        return str(self._list)

class Swap:
    def __init__(self):
        self._list = dll()

    def put(self, block):
        self._list.add_last(SwapBlock(block))

    def get(self, id):
        res = self._list.find((lambda x, y: x.element.process_id == y), id)
        return res.element if res else res

    def __str__(self):
        return str(self._list)

class SwapBlock:
    def __init__(self, block):
        self.id = block.id
        self.process_id = block.process_id
        self.size = block.size
        self.used = block.used 

    def __str__(self):
        return "%d %d %d %d" % (self.id, self.process_id, self.size, self.used)

#Not including an attribute for data, we're not concerned about that
class Block:
    def __init__(self, size, first, id, memory, access, initial=None):
        self.size = size
        self.first = [first]
        self.initial = size if not initial else initial
        self.free = True
        self.used = 0
        self.id = id
        self.memory = memory
        self.process_id = None
        self.access_time = 0

    def allocate(self, size, power, curr, pid):
        self.split_n(curr, power)
        self.free = False
        self.used = size
        self.process_id = pid

    def deallocate(self):
        self.free = True
        self.process_id = None
        self.used = 0
        return self.merge_up()

    #curr needs to be a DLLNode
    def _split(self, curr):
        self.size /= 2
        self.first.append(True)
        pair = Block(self.size, False, self.memory._next_num, self.memory, self.memory.step, initial=self.initial)
        self.memory._list.add_after(pair, curr)
        self.memory.increment_id()

    def split_n(self, curr, size):
        while self.size/2 >= size:
            self._split(curr)

    def _merge_up(self):
        curr = self.memory._list.find((lambda x, y: x.element.id == y), self.id)
        if self.first[len(self.first)-1]:
            buddy = curr.next
        else:
            buddy = curr.previous
        if buddy.element.size == self.size and buddy.element.free:
            if buddy == curr.previous:
                buddy.element.first = buddy.element.first[:len(buddy.element.first)-1]
                self.memory._list.remove_node(curr)
                buddy.element.size *= 2
                return buddy
            self.size *= 2
            self.first = self.first[:len(self.first)-1]
            self.memory._list.remove_node(buddy)
            return 1
        return 0

    def merge_up(self):
        res = None
        while self.size != self.initial:
            res = self._merge_up()
            if res == 0:
                break
            elif res == 1:
                continue
            elif isinstance(res.element, Block):
                res.element.merge_up()
                break
        return res

    def __int__(self):
        return self.size
    
    def __str__(self):
        return "%d/%d pid:%d id:%d %s" % (self.used, self.size, self.process_id if not self.process_id == None else -1 , self.id, "¹" if self.first[len(self.first)-1] else "²")

from random import randint 

mem = Memory()
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
mem.request(32, randint(0, 20))
print("mem", mem)
print("swap", mem._swap)