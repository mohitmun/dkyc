from flask import Flask
users = {}
import json
from umbral import pre, keys, signing
app = Flask(__name__)
import base64
from flask import request
@app.route("/new_user/<string:user_id>")
def new_user(user_id):
    alices_private_key = keys.UmbralPrivateKey.gen_key()
    alices_public_key = alices_private_key.get_pubkey()

    alices_signing_key = keys.UmbralPrivateKey.gen_key()
    alices_verifying_key = alices_signing_key.get_pubkey()
    alices_signer = signing.Signer(private_key=alices_signing_key)
    users[user_id] = {'prk': alices_private_key, 'pubk': alices_public_key, 'signk': alices_signing_key, 'signer': alices_signer }
    print(users)
    return "New User created"

@app.route("/encrypt")
def encrypt_():
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
        global capsule
        ciphertext, capsule = pre.encrypt(user['pubk'], request.args.get('msg').encode())
        return json.dumps({'c': base64.b64encode(ciphertext).decode()})
    else:
        return "No user found"

@app.route("/decrypt")
def decrypt_():
    user_id = request.args.get('user_id')
    if user_id in users:
        print("user found")
        user = users[user_id]
        print("user_id:")
        print(request.args.get('user_id'))
        print("msg:")
        print(request.args.get('msg'))
        kfrags = pre.split_rekey(delegating_privkey=alices_private_key, signer=alices_signer, receiving_pubkey=bobs_public_key, threshold=10, N=20)

        capsule.set_correctness_keys(delegating=alices_public_key, receiving=bobs_public_key, verifying=alices_verifying_key)

        cfrags = list()           # Bob's cfrag collection
        for kfrag in kfrags[:10]:
          cfrag = pre.reencrypt(kfrag=kfrag, capsule=capsule)
          cfrags.append(cfrag)   

        ciphertext = request.args.get('msg')
        for cfrag in cfrags:
          capsule.attach_cfrag(cfrag)

        bob_cleartext = pre.decrypt(ciphertext=ciphertext, capsule=capsule, decrypting_key=bobs_private_key)
        print("bob_cleartext")
        print(bob_cleartext)
        return "ciphertext.decode()"
    else:
        return "No user found"

# print(encrypt_())
if __name__ == "__main__":
    app.run()
