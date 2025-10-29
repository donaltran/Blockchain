import datetime as date
from block import Block

def next_block(last_block):
    this_index = last_block.index + 1
    this_time = date.datetime.now()
    this_data = str(this_index)
    this_hash = last_block.hash
    return Block(this_index, this_time, this_data, this_hash)