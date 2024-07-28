# from dadata import Dadata
# token = "3cc3b1b92eadca34601e7ba2a341a3a594f3f6e0"
# dadata = Dadata(token)
# result = dadata.find_by_id("delivery", "Брёхово мкр Школьный к8 г Химки")
# print(result['value'])



from dadata import Dadata
token = "3cc3b1b92eadca34601e7ba2a341a3a594f3f6e0"
dadata = Dadata(token)
result = dadata.suggest("postal_unit", "деревня Брёхово, 78А")
print(result)