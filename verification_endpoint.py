from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    content = request.get_json(silent=True)

    # get contents from JSON
    sig = content['sig']
    payload = content['payload']
    message = content['payload']['message']
    pk = content['payload']['pk']
    platform = content['payload']['platform']

    # Check if signature is valid
    # Should only be true if signature validates
    result = False

    if platform == "Algorand":
        print("Algorand")
        if algosdk.util.verify_bytes(payload.encode('utf-8'), sig, pk):
            print("Algo sig verifies!")
            result = True

    elif platform == "Ethereum":
        print("Ethereum")
        eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
        if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk:
            print("Eth sig verifies!")
            result = True

    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
