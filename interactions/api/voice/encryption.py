import struct

__all__ = ("Encryption",)

try:
    from nacl import secret, utils

    nacl_imported = True
except ImportError:
    nacl_imported = False


class Encryption:
    SUPPORTED = (
        "xsalsa20_poly1305_lite",
        "xsalsa20_poly1305_suffix",
        "xsalsa20_poly1305",
    )

    def __init__(self, secret_key) -> None:
        if not nacl_imported:
            raise RuntimeError("Please install interactions[voice] to use voice components.")
        self.box: secret.SecretBox = secret.SecretBox(bytes(secret_key))

        self._xsalsa20_poly1305_lite_nonce: int = 0

    def encrypt(self, mode: str, header: bytes, data) -> bytes:
        match mode:
            case "xsalsa20_poly1305_lite":
                return self.xsalsa20_poly1305_lite(header, data)
            case "xsalsa20_poly1305_suffix":
                return self.xsalsa20_poly1305_suffix(header, data)
            case "xsalsa20_poly1305":
                return self.xsalsa20_poly1305(header, data)
            case _:
                raise RuntimeError(f"Unsupported encryption type requested: {mode}")

    def xsalsa20_poly1305_lite(self, header: bytes, data) -> bytes:
        nonce = bytearray(24)
        nonce[:4] = struct.pack(">I", self._xsalsa20_poly1305_lite_nonce)

        self._xsalsa20_poly1305_lite_nonce += 1
        if self._xsalsa20_poly1305_lite_nonce > 2**32:
            self._xsalsa20_poly1305_lite_nonce = 0

        return header + self.box.encrypt(bytes(data), bytes(nonce)).ciphertext + nonce[:4]

    def xsalsa20_poly1305_suffix(self, header: bytes, data) -> bytes:
        nonce = utils.random(secret.SecretBox.NONCE_SIZE)
        return header + self.box.encrypt(bytes(data), nonce).ciphertext + nonce

    def xsalsa20_poly1305(self, header: bytes, data) -> bytes:
        nonce = bytearray(24)
        nonce[:12] = header

        return header + self.box.encrypt(bytes(data), bytes(nonce)).ciphertext
