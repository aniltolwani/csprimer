import csv

class CSVScanner:
    def __init__(self, file_path, schema):
        self.file_path = file_path
        self.file = open(file_path, 'r')
        self.reader = csv.reader(self.file)
        self.schema = schema
        self.header = next(self.reader)

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
            print("StopIteration")
            self.file.close()
            return None
        # schema validation error
        except ValueError as e:
            print("ValueError, probably a schema validation error", e)
            raise e
        
    def __del__(self):
        print("Closing file from del")
        self.file.close()

if __name__ == '__main__':

    schema = (
        ('movieId', int),
        ('title', str),
        ('genres', str)
    )

    scanner = CSVScanner('./movies.csv', schema)
    row1 = next(scanner)
    row2 = next(scanner)
    row3 = next(scanner)
    print("row1", row1)
    print("row2", row2)
    print("row3", row3)
