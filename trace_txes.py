from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
from datetime import datetime

rpc_user='quaker_quorum'
rpc_password='franklin_fought_for_continental_cash'
rpc_ip='3.134.159.30'
rpc_port='8332'

rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpc_user, rpc_password, rpc_ip, rpc_port))






###################################



class TXO:
    def __init__(self, tx_hash, n, amount, owner, time ):
        self.tx_hash = tx_hash 
        self.n = n
        self.amount = amount
        self.owner = owner
        self.time = time
        self.inputs = []

    def __str__(self, level=0):
        ret = "\t"*level+repr(self.tx_hash)+"\n"
        for tx in self.inputs:
            ret += tx.__str__(level+1)
        return ret

    def to_json(self):
        fields = ['tx_hash','n','amount','owner']
        json_dict = { field: self.__dict__[field] for field in fields }
        json_dict.update( {'time': datetime.timestamp(self.time) } )
        if len(self.inputs) > 0:
            for txo in self.inputs:
                json_dict.update( {'inputs': json.loads(txo.to_json()) } )
        return json.dumps(json_dict, sort_keys=True, indent=4)

        # this classmethod should connect to the Bitcoin blockchain,
    # and retrieve the n'th output of the transaction with the given hash.
    # Then it should create and return a new object with the fields, 'tx_hash’, 'n’, 'amount’, ‘owner’ and ‘time’
    # set to the values retrieved from the blockchain.
    # This method does not need to initialize the list 'inputs’.
    # Note that the ‘time’ field should be converted to a datetime object (using the datetime.fromtimestamp method)
    @classmethod
    def from_tx_hash(cls, tx_hash, n=0):
        # get tx from the Bitcoin blockchain
        tx = rpc_connection.getrawtransaction(tx_hash, True)

        # check if n in within range of number of output tx
        if n < len(tx["vout"]):
            # create a new TXO and return it
            amount = int(tx["vout"][n]["value"] * (10 ** 8))
            owner = tx["vout"][n]["scriptPubKey"]["addresses"][0]
            datetime_time = datetime.fromtimestamp(tx["time"])
            txo = TXO(tx_hash, n, amount, owner, datetime_time)
            return txo
        else:
            pass

    # def get_inputs_inner(self, d):

    # this method should connect to the Bitcoin blockchain,
    # and populate the list of inputs, up to a depth   d .
    # In other words, if   d=1  it should create TXO objects to populate self.inputs with the appropriate TXO objects.
    # If   d=2  it should also populate the inputs field of each of the TXOs in self.inputs etc.
    # it does not return any objects. It operates on the object passed to it (self argument)
    def get_inputs(self, d=1):
        if d > 0:
            tx = rpc_connection.getrawtransaction(self.tx_hash, True)
            len_vin = len(tx["vin"])
            for i in range(0, len_vin):
                txo = TXO.from_tx_hash(tx["vin"][i]["txid"], tx["vin"][i]["vout"])
                print(txo)
                self.inputs.append(txo)
                txo.get_inputs(d - 1)
        else:
            pass