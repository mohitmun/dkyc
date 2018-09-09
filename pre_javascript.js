var forge = require('node-forge');
var bigInt = require("big-integer");

var bits = 160;
forge.prime.generateProbablePrime(bits, function(err, num) {
  // Create prime factor and convert to bigInt
  var factor = bigInt(num.toString(10));
  // Find a larger prime of which factor is prime factor
  // Determine a large even number as a co-factor
  var coFactor = bigInt.randBetween("2e260", "3e260"); // should be bitLength(prime) - bitLength(factor)
  var prime = bigInt(4);
  while(!coFactor.isEven() || !prime.isPrime()) {
    console.log("here")
    coFactor = bigInt.randBetween("2e260", "3e260"); // should be bitLength(prime) - bitLength(factor)
    prime = coFactor.multiply(factor);
    prime = prime.add(1);
    console.log("prime: " + bigInt(prime))
    console.log("coFactor: " + coFactor)
  }
  // Get a generator g for the multiplicative group mod factor
  var j = prime.minus(1).divide(factor);
  var h = bigInt.randBetween(2, prime.minus(1));
  var g = h.modPow(j, factor);
  // Alice's keys
  // Secret key
  //var a = bigInt.randBetween(2, factor.minus(2));
  //// Public key
  //var A = g.modPow(a, prime);
  //// Bob's keys
  //// Secret key
  //var b = bigInt.randBetween(2, factor.minus(2));
  //// Public key
  //var B = g.modPow(b, prime);
  //// Shared secret
  //// Calculated by Alice
  //var Sa = B.modPow(a, prime);
  //// Calculated by Bob
  //var Sb = A.modPow(b, prime);
  //// Check
  //// Encryption by Alice
  //var k = bigInt.randBetween(1, factor.minus(1));
  //var c1 = g.modPow(k, prime);
  //// Using Bob's public key
  //var m = bigInt(2234266) // our message
  //var c2 = m.multiply(B.modPow(k, prime)).mod(prime);
  //// Decryption by Bob
  //var decrypt = c1.modPow((prime.minus(b).minus(bigInt(1))), prime).multiply(c2).mod(prime);
  //console.log(decrypt); // should be 2234266
  
  
  // Proxy re-encryption test
  // x is secret key
  var x = bigInt.randBetween(1, factor.minus(1));
  var x1 = bigInt.randBetween(1, x);
  var x2 = x.minus(x1);
  // y is public key
  var y = g.modPow(x, prime);
  var r = bigInt.randBetween(1, factor.minus(1));
  var c3 = g.modPow(r, prime);
  // mg^xr
  var c4 = m.multiply(y.modPow(r, prime)).mod(prime);
  var _decryptP = c4.multiply(c3.modPow(x1, prime).modInv(prime)).mod(prime);
  var _decryptF = _decryptP.multiply(c3.modPow(x2, prime).modInv(prime)).mod(prime);
  console.log(_decryptF); // should be 2234266
});
