class OldIterator:
    def __init__(self):
        self.count = 0
    
    def next(self):  # Old style
        self.count += 1
        if self.count > 3:
            return None
        return self.count

class NewIterator:
    def __init__(self):
        self.count = 0
    
    def __next__(self):  # Modern style
        self.count += 1
        if self.count > 3:
            raise StopIteration
        return self.count
    
    def __iter__(self):  # Should implement this too for completeness
        return self

print("Creating iterators")
old = OldIterator()
new = NewIterator()
breakpoint()
print("Done")