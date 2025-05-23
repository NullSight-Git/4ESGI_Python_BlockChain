from datetime import time
import hashlib

class Block :
    def __init__(self, index, data= None, prev_hash="0"):
        self._index = index
        self._data = data
        self._prev_hash = prev_hash
        self._nonce = ""
        self._hash = ""
        self._timestamp = 0

    def calculate_hash(self):
        block_string = f"{self.index}{self._prev_hash}{self.data}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        if self._hash != "":
            raise ValueError("Block already mined")
        
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

        self._timestamp = int(time.time())

    def is_validate(self) :
        if self._hash == "":
            raise ValueError("Block not mined yet")
        
        if self._hash or self._hash != self.calculate_hash():
            raise ValueError("Block hash mismatch")
        
        return True

    @property
    def index(self):
        return self._index
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value) :
        if not isinstance(value, str):
            raise ValueError("Data must be a string")
        self._data = value
    
    @property
    def prev_hash(self):
        return self._prev_hash
    
    @property
    def nonce(self):
        return self._nonce
    
    @property
    def timestamp(self):
        return self._timestamp

    def __str__(self):
        return f"Block(data={self._data}, prev_hash={self._prev_hash}, nonce={self._nonce}, hash={self._hash}, timestamp={self._timestamp})"

class Block_Chain :
    def __init__(self, difficulty=1):
        self._chain = []
        self._difficulty = difficulty
        self._block_size = 10
        self._max_size = 100
        self._current_size = 0
        self._current_block = None

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block")

    def get_block (self, index) :
        for block in self._chain :
            if block.index == index : 
                return block
        return None
    
    def get_latest_block(self) :
        return self._current_block

    def add_block(self, data) :
        prev_block = self.get_latest_block()
        
        if prev_block.is_validate():
            prev_block.mine_block(self._difficulty)

        self._current_size += 1
        new_block = Block(len(self._current_size), prev_block.hash, data)
        self._chain.append(new_block)
        self._current_block = new_block

    def modify_block(self, data) :
        if self._current_block is None:
            raise ValueError("No current block to modify")
        
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        
        self._current_block.data = data
    
    def validate_block(self):
        if not self.current_block.is_validate() :
            self.current_block.mine_block(self._difficulty)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            if curr.hash != curr.calculate_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
        return True
    
    @property
    def chain(self):
        return self._chain
    
    @property
    def difficulty(self):
        return self._difficulty
    
    @property
    def block_size(self):
        return self._block_size
    
    @property
    def max_size(self):
        return self._max_size
    
    @property
    def current_size(self):
        return self._current_size
    
    @property
    def current_block(self):
        return self._current_block
    
    def __str__(self):
        return f"Block_Chain(chain={self._chain}, difficulty={self._difficulty}, block_size={self._block_size}, max_size={self._max_size}, current_size={self._current_size}, current_block={self._current_block})"

if __name__ == "main":
    my_chain = Block_Chain(difficulty=3)
    my_chain.add_block("First block data")
    my_chain.add_block("Second block data")

    for block in my_chain.chain:
        print(block.index)
        print(block)
