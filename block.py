import hashlib as hasher
import time
import json

class Transaction:
    def __init__(self, sender, recipient, amount, timestamp):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
        }

    def __repr__(self):
        return f"Transaction({self.sender} -> {self.recipient}: {self.amount})"

class Block:
    def __init__(self, index, time, transactions, previous_hash, nonce=None):
        self.index = index
        self.time = time
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        block_string = json.dumps({
            'index': self.index,
            'time': self.time,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root
        }, sort_keys=True).encode()
        sha.update(block_string)
        return sha.hexdigest()

    def calculate_merkle_root(self):
        if not self.transactions:
            return hasher.sha256(b'').hexdigest()

        tx_hashes = [hasher.sha256(json.dumps(tx.to_dict(),
            sort_keys=True).encode()).hexdigest() for tx in self.transactions]

        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            new_hashes = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                new_hash = hasher.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            tx_hashes = new_hashes
        return tx_hashes[0]

    def mine_block(self, difficulty):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.hash_block()
        return self.hash

    def to_dict(self):
        return {
            'index': self.index,
            'time': self.time,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'merkle_root': self.merkle_root,
            'hash': self.hash,
        }

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash[:10]}...)"