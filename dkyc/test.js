var a = require('./js/contractDetails.js')
var Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
var kycContract = web3.eth.contract(a.abi);
var deployedContract = kycContract.new({
    data: a.binaryData,
    from: web3.eth.accounts[0],
    gas: 4700000
});
var contractInstance = kycContract.at(a.contractAddress);
