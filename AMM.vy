from vyper.interfaces import ERC20

tokenAQty: public(uint256) #Quantity of tokenA held by the contract
tokenBQty: public(uint256) #Quantity of tokenB held by the contract

invariant: public(uint256) #The Constant-Function invariant (tokenAQty*tokenBQty = invariant throughout the life of the contract)
	
tokenA: ERC20 #The ERC20 contract for tokenA
tokenB: ERC20 #The ERC20 contract for tokenB
	
owner: public(address) #The liquidity provider (the address that has the right to withdraw funds and close the contract)



# ERC20 library 
# (https://github.com/vyperlang/vyper/blob/master/examples/tokens/ERC20.vy)

# example Automated Market Maker (AMM) contract that trade ETH to ECR 
# (https://github.com/vyperlang/vyper/blob/master/examples/market_maker/on_chain_market_maker.vy)


	
	
@external
def get_token_address(token: uint256) -> address:
	if token == 0:
		return self.tokenA.address
	if token == 1:
		return self.tokenB.address
	return ZERO_ADDRESS	





# Sets the on chain market maker with its owner, and initial token quantities
# Both tokenA_addr and tokenB_addr should be addresses of valid ERC20 contracts, 
# and tokenA_amount and tokenB_amount should be the quantities of each token that are being deposited. 
# The sender corresponds to the address which provides liquidity (and therefore is the owner)
@external
# def initiate(token_addr: address, token_quantity: uint256):
def provideLiquidity(tokenA_addr: address, 
		     tokenB_addr: address, 
		     tokenA_quantity: uint256, 
		     tokenB_quantity: uint256):
	assert self.invariant == 0 #This ensures that liquidity can only be provided once
	
	#Your code here
	# send the address of A and B
	self.tokenA = ERC20(tokenA_addr)
	self.tokenB = ERC20(tokenB_addr)
	
	# drag the input amount of A and B from message sender
	self.tokenA.transferFrom(msg.sender, self, tokenA_quantity)
	self.tokenB.transferFrom(msg.sender, self, tokenB_quantity)
	
	# set owner, amount of A and B, and invariant at the Automated Market Maker (AMM) contract 
	self.owner = msg.sender
	self.tokenAQty = tokenA_quantity
	self.tokenBQty = tokenB_quantity
	self.invariant = tokenA_quantity * tokenB_quantity
	
	assert self.invariant > 0

	
	
# Trades one token for the other
# token_addr should match either tokenA_addr or tokenB_addr, 
# and “amount” should be the amount of that token being traded to the contract. 
# The contract should calculate the amount of the other token to return to the sender using the invariant calculation of Uniswap.
@external
def tradeTokens(sell_token: address, 
		sell_quantity: uint256):
	assert sell_token == self.tokenA.address or sell_token == self.tokenB.address
	
	#Your code here
	# if message sender want to sell A for B
	if sell_token == self.tokenA.address:
		# drag the input amount of A from message sender 
		self.tokenA.transferFrom(msg.sender, self, sell_quantity)
		# set new amount of A and calculate new amount of B
		new_total_A: uint256 = self.tokenAQty + sell_quantity
		new_total_B: uint256 = self.invariant / new_total_A
		# send the extra amount of B back to message sender 
		self.tokenB.transfer(msg.sender, self.tokenBQty - new_total_B)
		# set new amount of A and B at the Automated Market Maker (AMM) contract 
		self.tokenAQty = new_total_A
		self.tokenBQty = new_total_B
		
	# if message sender want to sell B for A
	if sell_token == self.tokenB.address:
		# drag the input amount of B from message sender 
		self.tokenB.transferFrom(msg.sender, self, sell_quantity)
		# set new amount of B and calculate new amount of A
		new_total_B: uint256 = self.tokenBQty + sell_quantity
		new_total_A: uint256 = self.invariant / new_total_B
		# send the extra amount of A back to message sender 
		self.tokenA.transfer(msg.sender, self.tokenAQty - new_total_A)
		# set new amount of A and B at the Automated Market Maker (AMM) contract 
		self.tokenAQty = new_total_A
		self.tokenBQty = new_total_B


	
	
# Owner can withdraw their funds and destroy the market maker
# If the message sender was the initial liquidity provider, 
# this should give all tokens held by the contract to the message sender, otherwise it should fail.
@external
def ownerWithdraw():
	assert self.owner == msg.sender
	#Your code here
	# send the total amount of A and B currently at the Automated Market Maker (AMM) contract back to message sender 
	self.tokenA.transfer(self.owner, self.tokenAQty)
	self.tokenB.transfer(self.owner, self.tokenBQty)
	selfdestruct(self.owner)
