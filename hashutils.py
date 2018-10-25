import hashlib

def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()
    
 
def check_pw_hash(password,hash):
    print("#11111111" +make_pw_hash(password))
    print("$22222222"+hash)
    if make_pw_hash(password) == hash: #hash pwd in database
        return True
    return False      