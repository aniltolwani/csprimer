import csv
# let's implement a simple, mock relational DB
# need to support
# projection (subset of columns)
# selection (subset of rows), equality, inequality (basic filters)
# limits (return the first N rows of a query)
# sorting (in memory, ascending or descending)
# for now, run the queries over test data that is already in memory i.e. a hand-coded list of "rows". We will implement heap files and an index later.


# the return for this should be an iterator where each operation is a linked list. Each node will store it's own state, and provide a next() method.
# the next method will yield the next row of the query one by one.
# importantly, you can assume that queries are already parsed.

class QueryNode(object):
    """"
    We can define a custom parent class for all the nodes, and then inherit from it.
    
    This lets us define a close method that will cascade from root -> leaf nodes. (Right now we really only support leaf -> root with returning None).
    """
    def __init__(self):
        self.child = None

    def __next__(self):
        if self.child is None:
            return None
        return next(self.child)

    def close(self):
        if self.child is not None:
            self.child.close()

class MemoryScan(QueryNode):
    """
    Yield all records from the given "table" in memory.

    This is really just for testing... in the future our scan nodes
    will read from disk.
    """
    def __init__(self, table):
        self.table = table
        self.idx = 0
        self.child = None
    def __next__(self):
        if self.idx >= len(self.table):
            return None

        x = self.table[self.idx]
        self.idx += 1
        return x


class Projection(QueryNode):
    """
    Map the child records using the given map function, e.g. to return a subset
    of the fields.
    """
    def __init__(self, proj):
        self.proj = proj
        self.child = None
    
    def __next__(self):
        if self.child is None:
            return None
        x = next(self.child)
        if x:
            return self.proj(x)
        return None

class Selection(QueryNode):
    """
    Filter the child records using the given predicate function.

    Yes it's confusing to call this "selection" as it's unrelated to SELECT in
    SQL, and is more like the WHERE clause. We keep the naming to be consistent
    with the literature.
    """
    def __init__(self, predicate):
        self.predicate = predicate
        self.child = None
    def __next__(self):
        if self.child is None:
            return None
        x = next(self.child)
        while x:
            if self.predicate(x):
                return x
            x = next(self.child)
        return None

class Limit(QueryNode):
    """
    Return only as many as the limit, then stop
    """
    def __init__(self, n):
        self.n = n
        self.child = None
        self.curr = 0
    
    def __next__(self):
        if self.child is None:
            return None
        x = next(self.child)
        if x:
            if self.curr < self.n:
                self.curr += 1
                return x
        return None

class Sort(QueryNode):
    """
    Sort based on the given key function
    """
    def __init__(self, key, desc=False):
        self.key = key
        self.desc = desc
        self.child = None
        self.it = None
    
    def construct_iter(self):
        if self.child is None:
            return None
        res = []
        x = next(self.child)
        while x:
            res.append(x)
            x = next(self.child)
        if not res:
            return None
        return iter(sorted(res, key=self.key, reverse = self.desc))
        
    def __next__(self):
        if not self.it:
            self.it = self.construct_iter()
        try:
            x = next(self.it)
        except StopIteration:
            return None
        return x
def Q(*nodes):
    """
    Construct a linked list of executor nodes from the given arguments,
    starting with a root node, and adding references to each child
    """
    ns = iter(nodes)
    parent = root = next(ns)
    for n in ns:
        parent.child = n
        parent = n
    return root

class CSVScanner:
    def __init__(self, file_path, schema):
        self.file_path = file_path
        self.file = open(file_path, 'r')
        self.reader = csv.reader(self.file)
        self.schema = schema
        self.header = next(self.reader)
        self.child = None
    def __iter__(self):
        return self

    def __next__(self):
        try:
            next_val = next(self.reader)
            # try schema validation
            for idx, val in enumerate(next_val):    
                next_val[idx] = self.schema[idx][1](val)
            if len(next_val) != len(self.schema):
                raise ValueError("Schema validation error, number of columns in row does not match schema")
            return tuple(next_val)
        except StopIteration:
            self.file.close()
            return None
        # schema validation error
        except ValueError as e:
            print("ValueError, probably a schema validation error", e)
            raise e
        
    def close(self):
        if self.file:
            print('run the close on the file')
            self.file.close()


def run(q):
    """
    Run the given query to completion by calling `next` on the (presumed) root
    """
    while True:
        x = next(q)
        if x is None:
            break
        yield x
    q.close()


if __name__ == '__main__':
    # Test data generated by Claude and probably not accurate!
    birds = (
        ('amerob', 'American Robin', 0.077, True),
        ('baleag', 'Bald Eagle', 4.74, True),
        ('eursta', 'European Starling', 0.082, True),
        ('barswa', 'Barn Swallow', 0.019, True),
        ('ostric1', 'Ostrich', 104.0, False),
        ('emppen1', 'Emperor Penguin', 23.0, False),
        ('rufhum', 'Rufous Hummingbird', 0.0034, True),
        ('comrav', 'Common Raven', 1.2, True),
        ('wanalb', 'Wandering Albatross', 8.5, False),
        ('norcar', 'Northern Cardinal', 0.045, True)
    )
    schema = (
        ('id', str),
        ('name', str),
        ('weight', float),
        ('in_us', bool),
    )

    # test a simple scan
    assert tuple(run(Q(
        Projection(lambda x: (x[0],)),
        Selection(lambda x: not x[3]),
        MemoryScan(birds)
    ))) == (
        ('ostric1',),
        ('emppen1',),
        ('wanalb',),
    ), f"Projection and Selection failed. {tuple(run(Q(Projection(lambda x: (x[0],)), Selection(lambda x: not x[3]), MemoryScan(birds))))}"
    
    # # id and weight of 3 heaviest birds
    assert tuple(run(Q(
        Projection(lambda x: (x[0], x[2])),
        Limit(3),
        Sort(lambda x: x[2], desc=True),
        MemoryScan(birds),
    ))) == (
        ('ostric1', 104.0),
        ('emppen1', 23.0),
        ('wanalb', 8.5),
    )
    # try a few much harder cases, nested filter etc.
    assert tuple(run(Q(
        Projection(lambda x: (x[0], x[2])),
        Selection(lambda x: x[2] > 10),
        MemoryScan(birds),
    ))) == (
        ('ostric1', 104.0),
        ('emppen1', 23.0),
    )

    # try a few much harder cases, nested filter etc.
    assert tuple(run(Q(
        Projection(lambda x: (x[0], x[2])),
        Selection(lambda x: x[2] > 10),
        MemoryScan(birds),
    ))) == (
        ('ostric1', 104.0),
        ('emppen1', 23.0),
    )

    # nested selection
    # Original two asserts
    assert tuple(run(Q(
        Projection(lambda x: (x[0],)),
        Selection(lambda x: not x[3]),
        MemoryScan(birds)
    ))) == (
        ('ostric1',),
        ('emppen1',),
        ('wanalb',),
    )

    assert tuple(run(Q(
        Projection(lambda x: (x[0], x[2])),
        Limit(3),
        Sort(lambda x: x[2], desc=True),
        MemoryScan(birds),
    ))) == (
        ('ostric1', 104.0),
        ('emppen1', 23.0),
        ('wanalb', 8.5),
    )

    # New asserts testing different combinations
    # Get names of 2 lightest US birds
    assert tuple(run(Q(
        Projection(lambda x: (x[1],)),
        Limit(2),
        Sort(lambda x: x[2]),  # sort by weight ascending
        Selection(lambda x: x[3]),  # US birds only
        MemoryScan(birds),
    ))) == (
        ('Rufous Hummingbird',),
        ('Barn Swallow',)
    )

    # Get all birds over 1kg (>1.0), sorted by name
    assert tuple(run(Q(
        Projection(lambda x: (x[1], x[2])),
        Sort(lambda x: x[1]),  # sort by name
        Selection(lambda x: x[2] > 1.0),
        MemoryScan(birds),
    ))) == (
        ('Bald Eagle', 4.74),
        ('Common Raven', 1.2),
        ('Emperor Penguin', 23.0),
        ('Ostrich', 104.0),
        ('Wandering Albatross', 8.5),
    )

    # Get IDs of the 2 heaviest non-US birds
    assert tuple(run(Q(
        Projection(lambda x: (x[0],)),
        Limit(2),
        Sort(lambda x: x[2], desc=True),
        Selection(lambda x: not x[3]),  # non-US birds
        MemoryScan(birds),
    ))) == (
        ('ostric1',),
        ('emppen1',),
    )

    movie_schema = (
        ('movieId', int),
        ('title', str),
        ('genres', str)
    )
    # print(len(tuple(run(Q(CSVScanner('./movies.csv', movie_schema))))))
    # # top 10 movies, sorted by title
    # print("top 10 movies, sorted by title")
    # print(tuple(run(Q(
    #     Projection(lambda x: (x[1],)),
    #     Limit(10),
    #     Sort(lambda x: x[1], desc=False),
    #     CSVScanner('./movies.csv', movie_schema)
    # ))))
    print(tuple(run(Q(
        Limit(10),
        Selection(lambda x: x[0] == 5_000),
        Sort(lambda x: x[1], desc=False),
        CSVScanner('./movies.csv', movie_schema)
    ))))
    print("done")



