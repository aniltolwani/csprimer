# in this exercise, we will implement a simple heap file database.
# it will work with db-query.py and support
# 1. ingesting a file into a heap file data structure (pages of 8192 bytes)
# 2. a "header format" record per page that contains the page number, num_valid_records in a page
# 3. a "record format" per record in a page that contains the record number, and the record data.
# this will be encoded with a simple binary/bytes format and support some bits for nulls values.
# an some sort of encode/decode function to read/write these to the file based on a schema.
# 4. a "page manager" that will encode just the header information for a page and a pointer to that page.
# 5. a "heap file" that will manage the pages and provide a simple interface for reading and writing records.
# as a stretch, we can implement a B+ tree index on top of the heap file to speed up queries.

PAGE_SIZE = 8192

import struct    
import os
import csv
import pytest
class RecordWrapper (object):
    def __init__(self, schema):
        self.schema = schema

    def encode(self, record: tuple) -> bytes:
        data = b""
        idx = 0
        for _, type in self.schema.items():
            value = record[idx]
            idx += 1
            if type == int or type == float:
                data += type(value).to_bytes(4, "little")
            elif type == str:
                bs = value.encode("utf-8")
                data += len(bs).to_bytes(1, "little") + bs
            else:
                raise ValueError(f"Invalid type: {type}")
        return data

    def decode(self, data) -> tuple:
        record = []
        idx = 0
        for _, type in self.schema.items():
            if type == int or type == float:
                value = int.from_bytes(data[idx:idx+4], "little")
                idx += 4
            elif type == str:
                length = int.from_bytes(data[idx:idx+1], "little")
                value = data[idx+1:idx+length+1].decode("utf-8")
                idx += length + 1
            else:
                raise ValueError(f"Invalid type: {type}")
            record.append(value)
        return tuple(record)

class Page(object):
    def __init__(self, page_num):
        self.page_num = page_num
        self.records = []
        self.data = b''
        self.free_ptr = 0
        self.fill_factor = 0.8

    @property
    def num_records(self):
        return len(self.records)
    
    @property
    def free_space(self):
        "Stop filling when we are half full."
        free_space = (PAGE_SIZE * self.fill_factor) - len(self.data)
        return free_space

    def add_record(self, record: bytes):
        self.data += record
        self.records.append((self.free_ptr, self.free_ptr + len(record), 1))
        self.free_ptr += len(record)
    
    def get_record(self, record_num):
        start, end, valid = self.records[record_num]
        if valid == 0:
            raise ValueError(f"Record {record_num} is not valid")
        return self.data[start:end]
    
    def is_valid(self, record_num):
        _, _, valid = self.records[record_num]
        return valid == 1

    def delete_record(self, record_num):
        self.records[record_num] = (self.records[record_num][0], self.records[record_num][1], 0)

class HeapFile(object):
    def __init__(self, file_path, schema):
        self.file_path = file_path
        self.pages = []
        self.page_idx = 0
        self.record_idx = 0
        self.record_wrapper = RecordWrapper(schema)

    def ingest_from_csv(self):
        with open(self.file_path, "r") as f:
            reader = csv.reader(f)
            # skip header
            next(reader)
            for row in reader:
                record = self.record_wrapper.encode(row)
                if self.page_idx >= len(self.pages):
                    self.pages.append(Page(self.page_idx))
                curr_space = self.pages[self.page_idx].free_space
                if curr_space < len(record):
                    self.page_idx += 1
                    self.pages.append(Page(self.page_idx))

                self.pages[self.page_idx].add_record(record)

        self.page_idx = 0
    def write_to_disk(self, out_file):
        """
        Write it to a custom file format on disk.
        
        This will let us lazily read in PAGE_SIZE chunks from the file and process records one at a time
        without loading the entire file into memory.
        
        Importantly, you need to be careful to go page by page:
            1. write the page number, number of total records (bytes)
            2. write the slots, which are tuples of (start, end) byte locations from the page_start
            3. write the actual data from the program..
            
        Since we made sure we left empty space, you should be able to add this and still stay under 8192 bytes for python's
        standard buffer size. It's okay to write a few empty bytes, we'll fix it in the future."""
        with open(out_file, "wb") as f:
            for page in self.pages:
                page_num, num_records, slots, data = page.page_num, page.num_records, page.records, page.data
                f.write(struct.pack("II", page_num, num_records))
                for slot in slots:
                    f.write(struct.pack("II", slot[0], slot[1]))
                f.write(data)
                # calculate the amount of padding needed to make the page size 8192
                padding = PAGE_SIZE - (8 + (num_records * 8) + len(data))
                f.write(b'\x00' * padding)


    def read_from_disk(self, in_file):
        with open(in_file, "rb") as f:
            chunk = f.read(PAGE_SIZE)
            while chunk:
                page_num, num_records = struct.unpack("II", chunk[:8])
                page = Page(page_num)
                chunk_pos = 8
                for _ in range(num_records):
                    start, end = struct.unpack("II", chunk[chunk_pos:chunk_pos+8])
                    chunk_pos += 8
                    page.records.append((start, end, 1))
                
                page.data = chunk[chunk_pos:]
                page.free_ptr = len(page.data)
                self.pages.append(page)
                chunk = f.read(PAGE_SIZE)

    
    def next(self):
        # skip empty pages or if we are at the end
        if self.record_idx >= len(self.pages[self.page_idx].records):
            self.page_idx += 1
            self.record_idx = 0
            return self.next()
        # skip deleted records
        if not self.pages[self.page_idx].is_valid(self.record_idx):
            self.record_idx += 1
            return self.next()
        byte_record = self.pages[self.page_idx].get_record(self.record_idx)
        record = self.record_wrapper.decode(byte_record)
        self.record_idx += 1
        return record


def main():
    schema = {
        "movieId": int,
        "title": str,
        "genres": str,
    }
    # first, let's just test some round trip tests on the record encoding/decoding
    r1 = (
        1,
        "Toy Story (1995)",
        "Adventure|Animation|Children|Comedy|Fantasy",
    )
    rw = RecordWrapper(schema)
    encoded = rw.encode(r1)
    print("encoded record:", encoded)
    decoded = rw.decode(encoded)
    print("decoded record:", decoded)
    print("equivalency test:", r1 == decoded)
    print("record size:", len(encoded))

    r2 = (
        2,
        "Jumanji (1995)",
        "Adventure|Children|Fantasy",
    )
    encoded = rw.encode(r2)
    print("encoded record:", encoded)
    decoded = rw.decode(encoded)
    print("decoded record:", decoded)
    print("equivalency test:", r2 == decoded)
    print("record size:", len(encoded))
    print("-----")
    print(" HEAPFILE TESTING")
    hf = HeapFile("movies.csv", schema)
    hf.ingest_from_csv()

    print(hf.next())
    print(hf.next())
    print(hf.next())
    print(hf.next())
    print("num pages:", len(hf.pages))
    print("bytes on first page:", len(hf.pages[0].data))
    print("sample bytes on first page:", hf.pages[0].data[:100])
    print("records on first page:", hf.pages[0].num_records)
    print ("----")
    print("TEST DELETE")
    print("before delete:", hf.pages[0].get_record(0))
    hf.pages[0].delete_record(0)
    with pytest.raises(ValueError):
        hf.pages[0].get_record(0)
    print("-----")
    print("TEST WRITE TO DISK, ROUNDTRIP")
    hf.write_to_disk("movies.hf")
    new_hf = HeapFile("movies.hf", schema)
    print("READ FROM DISK")
    new_hf.read_from_disk("movies.hf")
    print("num pages in old vs. new:", len(hf.pages), len(new_hf.pages))
    print("num records in old vs. new:", len(hf.pages[0].records), len(new_hf.pages[0].records))
    print("-----")
if __name__ == "__main__":
    main()