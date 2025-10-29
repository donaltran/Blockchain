from newblock import next_block
from genesis import create_genesis_block

blockchain = [create_genesis_block()]
previous_block = blockchain[0]

blocks_to_add = 1000

for i in range(blocks_to_add):
    added_block = next_block(previous_block)
    blockchain.append(added_block)
    previous_block = added_block
    print("Block #{} added to blockchain".format(added_block.index))
    print("Hash: {}\n".format(added_block.hash))

