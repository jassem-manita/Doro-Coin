from hashlib import sha256

#hashing the args
def updatehash(*args):
    hashing_text = ""
    h = sha256()
    for arg in args:
        hashing_text += str(arg)

    h.update(hashing_text.encode('utf-8'))
    return h.hexdigest()

#creating the block structure
class Block():

    def __init__(self,number=0, previous_hash="0"*64, data=None, nonce=0):
        self.data = data
        self.number = number
        self.previous_hash = previous_hash
        self.nonce = nonce


    #hashing function
    def hash(self):
        return updatehash(self.number,self.previous_hash,self.data,self.nonce)

    def __str__(self):
        return str("Block#: %s\nHash: %s\nPrevious: %s\nData: %s\nNonce: %s\n" %( self.number,self.hash(),self.previous_hash,self.data,self.nonce))


#creating the blockchain structure
class Blockchain():
    difficulty = 4

    def __init__(self):
        self.chain = []

    def add(self, block):
        self.chain.append(block)

    #remove chain from the blockchain
    def remove(self, block):
        self.chain.remove(block)

    #nonce == difficulty add to chain
    def mine(self, block):
        try: block.previous_hash = self.chain[-1].hash()
        except IndexError:
            pass

        while True:
            if block.hash()[:self.difficulty] == "0" * self.difficulty:
                self.add(block); break
            else:
                # increase nounce if nonce doesnt match
                block.nonce += 1

    #comparing the previous hash to the actual hash of the previous block
    def isValid(self):
        for i in range(1,len(self.chain)):
            _previous = self.chain[i].previous_hash
            _current = self.chain[i-1].hash()
            
            if _previous != _current or _current[:self.difficulty] != "0"*self.difficulty:
                return False

        return True



