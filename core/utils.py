import pyotp

def generate_otp():
    totp = pyotp.TOTP("<your_secret_key>", digits=6, interval=300)
    return totp.now()

def verify_otp(otp_input):
    totp = pyotp.TOTP("<your_secret_key>", digits=6, interval=300)
    return totp.verify(otp_input)
