import math
import random
from sympy import isprime

class RSA:
    def __init__(self, start=1000, end=10000):
        self.p = None
        self.q = None
        self.n = None
        self.e = None
        self.d = None
        self.set_prime_range(start, end)

    def set_prime_range(self, start, end):
        if not (isinstance(start, int) and isinstance(end, int)):
            raise TypeError("مقادیر شروع و پایان باید عدد صحیح باشند")
        if start < 2:
            raise ValueError("مقدار شروع باید بزرگتر مساوی 2 باشد")
        if end <= start + 5:
            raise ValueError("مقدار پایان باید حداقل 6 واحد بزرگتر از شروع باشد")
            
        self.start_number = start
        self.end_number = end
        return self

    def generate_prime_numbers(self):
        flag=False
        while flag==False:
            self.p = random.randint(self.start_number, self.end_number)
            self.q = random.randint(self.start_number, self.end_number)
            
            if self.p != self.q and isprime(self.p) and isprime(self.q):
                flag=True

    def calculate_keys(self):
        phi_n = (self.p - 1) * (self.q - 1)

        if phi_n > 65537 and math.gcd(65537, phi_n) == 1:
            e = 65537
        else:
            e = 3
            while e < phi_n and math.gcd(e, phi_n) != 1:
                e += 2  

        n = self.p * self.q
        d = pow(e, -1, phi_n)  
        
        self.phi_n = phi_n
        self.e = e
        self.n = n
        self.d = d

    def generate_keys(self):
        self.generate_prime_numbers()
        self.calculate_keys()
        return (self.n, self.e), (self.n, self.d)  

    def encrypt_message(self, message):
        if self.n is None or self.e is None:
            raise RuntimeError("کلیدها هنوز تولید نشده‌اند. ابتدا generate_keys() را فراخوانی کنید")
        
        encrypted_numbers = []
        for char in message:
            encrypted_numbers.append(pow(ord(char), self.e, self.n))
        return encrypted_numbers

    def decrypt_message(self, encrypted_numbers):
        if self.n is None or self.d is None:
            raise RuntimeError("کلیدها هنوز تولید نشده‌اند. ابتدا generate_keys() را فراخوانی کنید")
        
        decrypted_chars = []
        for number in encrypted_numbers:
            decrypted_chars.append(chr(pow(int(number), self.d, self.n)))
        return "".join(decrypted_chars)

    def get_public_key(self):
        if self.n is None or self.e is None:
            raise RuntimeError("کلیدها تولید نشده‌اند")
        return (self.n, self.e)

    def get_private_key(self):
        if self.n is None or self.d is None:
            raise RuntimeError("کلیدها تولید نشده‌اند")
        return (self.n, self.d)

    def is_keys_generated(self):
        return all([self.n, self.e, self.d, self.p, self.q])

    def get_key_info(self):
        if not self.is_keys_generated():
            return "کلیدها تولید نشده‌اند"
        
        return {
            "p": self.p,
            "q": self.q,
            "n": self.n,
            "e": self.e,
            "d": self.d,
            "phi_n": self.phi_n
        }