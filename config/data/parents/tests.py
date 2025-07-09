import base64

merchant_id = "686e4fe3d7ab35889d6cb26b"
account_key = "order_id"
order_id = "7c15d251-0e87-40b4-ac7b-3ad8540d5eb8"
amount = 5000.00
return_url = "https://google.com"

params = f"m={merchant_id};ac.{account_key}={order_id};a={amount};c={return_url}"
encode_params = base64.b64encode(params.encode("utf-8"))
encode_params = str(encode_params, 'utf-8')
url = f"https://checkout.paycom.uz/{encode_params}"

# params = f"m={TOKEN};ac.{KEY}={order_id};a={amount};c={return_url}"
#
# url = f"{self.LINK}/{encode_params}"
# return url

print(url)