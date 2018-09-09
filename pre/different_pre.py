from umbral import pre, keys, signing

from flask import Flask
users = {}
import json
from umbral import pre, keys, signing
app = Flask(__name__)
import base64
from flask import request
import json
import base64
# Generate Umbral keys for Alice.

def encrypt(plaintext, public_key):
    global capsule
    ciphertext, capsule = pre.encrypt(public_key, plaintext)
    return ciphertext

def grant(private_key, public_key, signer):
    kfrags = pre.split_rekey(delegating_privkey=private_key,
                         signer=signer,
                         receiving_pubkey=public_key,
                         threshold=10,
                         N=20)
    return kfrags

def reencrypt(kfrags, delegator_public_key, delegatee_pk, delegator_verifying_key):
    capsule.set_correctness_keys(delegating=delegator_public_key,
                             receiving=delegatee_pk,
                             verifying=delegator_verifying_key)

    global cfrags
    cfrags = list()           # Bob's cfrag collection
    for kfrag in kfrags[:10]:
      cfrag = pre.reencrypt(kfrag=kfrag, capsule=capsule)
      cfrags.append(cfrag)    # Bob collects a cfrag
    return cfrags

def decrypt_reencrypted(ciphertext, private_key):

    for cfrag in cfrags:
      capsule.attach_cfrag(cfrag)

    bob_cleartext = pre.decrypt(ciphertext=ciphertext,
                                capsule=capsule,
                                decrypting_key=private_key)
    return bob_cleartext

alices_private_key = keys.UmbralPrivateKey.gen_key()
alices_public_key = alices_private_key.get_pubkey()

alices_signing_key = keys.UmbralPrivateKey.gen_key()
alices_verifying_key = alices_signing_key.get_pubkey()
alices_signer = signing.Signer(private_key=alices_signing_key)

# Generate Umbral keys for Bob.
bobs_private_key = keys.UmbralPrivateKey.gen_key()
bobs_public_key = bobs_private_key.get_pubkey()
plaintext = b'Proxy Re-encryption is cool!'

ciphertext = encrypt(plaintext, alices_public_key)
print(ciphertext)
ciphertext = base64.b64encode(ciphertext)
kfrags_generated = grant(alices_private_key, bobs_public_key, alices_signer)
cfrags = reencrypt(kfrags_generated, alices_public_key, bobs_public_key, alices_verifying_key)
print("deocdeded ============")
ciphertext = base64.b64decode(ciphertext ) #+ b'fds'
print(ciphertext)
bob_cleartext = decrypt_reencrypted(ciphertext, bobs_private_key)
assert bob_cleartext == plaintext
@app.route("/new_user/<string:user_id>")
def new_user(user_id):
    alices_private_key = keys.UmbralPrivateKey.gen_key()
    alices_public_key = alices_private_key.get_pubkey()

    alices_signing_key = keys.UmbralPrivateKey.gen_key()
    alices_verifying_key = alices_signing_key.get_pubkey()
    alices_signer = signing.Signer(private_key=alices_signing_key)
    users[user_id] = {'prk': alices_private_key, 'pubk': alices_public_key, 'signk': alices_signing_key, 'signer': alices_signer, 'verifying_key': alices_verifying_key}
    print(users)
    return "New User created"

@app.route("/encrypt")
def encrypt_():
    user_id = request.args.get('user_id')
    if not user_id in users:
        print("User not found, creating new")
        new_user(user_id)

    user = users[user_id]
    global capsule
    ciphertext, capsule = pre.encrypt(user['pubk'], request.args.get('msg').encode())
    return base64.b64encode(ciphertext).decode()

@app.route("/reencrypt")
def reencrypt_():

    delegator_id = request.args.get('delegator_id')
    delegatee_id = request.args.get('delegatee_id')
    if not delegator_id in users:
        print("Delegator not found, creating new")
        new_user(delegator_id)

    if not delegatee_id in users:
        print("Delegatee not found, creating new")
        new_user(delegatee_id)
    delegator = users[delegator_id]
    print("==========")
    delegatee = users[delegatee_id]
    kfrags_ = grant(delegator['prk'], delegatee['pubk'], delegator['signer'])
    cfrags = reencrypt(kfrags_, delegator['pubk'], delegatee['pubk'], delegator['verifying_key'])
    return "Done"

@app.route("/decrypt_reencrypt")
def decrypt_reencrypt():
    user_id = request.args.get('user_id')
    if user_id in users:
        print("user found")
        user = users[user_id]
        print("user_id:")
        print(request.args.get('user_id'))
        print("msg:")
        print(request.args.get('msg'))
        print("user")
        print(user)

        ciphertext = request.args.get('ciphertext')

        print("cipher")
        print(ciphertext)
        ciphertext = base64.b64decode(ciphertext)
        print("cipher")
        print(ciphertext)
        cleartext = decrypt_reencrypted(ciphertext, user['prk'])
        print(cleartext)
        # return json.dumps({'cleartext': cleartext.encode()})
        return cleartext
    else:
        return "No user found"
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

if __name__ == "__main__":
    app.run()
