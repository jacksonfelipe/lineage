import struct

BLOCK_SIZE = 64  # 512 bits
R = 10  # Number of rounds

Sd = (
    "\u68d0\ueb2b\u489d\u6ae4\ue3a3\u5681\u7df1\u859e"
    "\u2c8e\u78ca\u17a9\u61d5\u5d0b\u8c3c\u7751\u2242"
    "\u3f54\u4180\ucc86\ub318\u2e57\u0662\uf436\ud16b"
    "\u1b65\u7510\uda49\u26f9\ucb66\ue7ba\uae50\u52ab"
    "\u05f0\u0d73\u3b04\u20fe\uddf5\ub45f\u0ab5\uc0a0"
    "\u71a5\u2d60\u7293\u3908\u8321\u5c87\ub1e0\u00c3"
    "\u1291\u8a02\u1ce6\u45c2\uc4fd\ubf44\ua14c\u33c5"
    "\u8423\u7cb0\u2515\u3569\uff94\u4d70\ua2af\ucdd6"
    "\u6cb7\uf809\uf367\ua4ea\uecb6\ud4d2\u141e\ue124"
    "\u38c6\udb4b\u7a3a\ude5e\udf95\ufcaa\ud7ce\u070f"
    "\u3d58\u9a98\u9cf2\ua711\u7e8b\u4303\ue2dc\ue5b2"
    "\u4ec7\u6de9\u2740\ud837\u928f\u011d\u533e\u59c1"
    "\u4f32\u16fa\u74fb\u639f\u341a\u2a5a\u8dc9\ucff6"
    "\u9028\u889b\u310e\ubd4a\ue896\ua60c\uc879\ubcbe"
    "\uef6e\u4697\u5bed\u19d9\uac99\ua829\u641f\uad55"
    "\u13bb\uf76f\ub947\u2fee\ub87b\u8930\ud37f\u7682"
)

T0 = [0] * 256
T1 = [0] * 256
T2 = [0] * 256
T3 = [0] * 256
T4 = [0] * 256
T5 = [0] * 256
T6 = [0] * 256
T7 = [0] * 256
rc = [0] * R

def rotl64(x, n):
    return ((x << n) & 0xFFFFFFFFFFFFFFFF) | (x >> (64 - n))

def init_tables():
    ROOT = 0x11d
    S = [0] * 256
    j = 0
    for i in range(256):
        c = ord(Sd[i >> 1])
        s = (c >> 8) if (i & 1) == 0 else (c & 0xFF)
        s2 = s << 1
        if s2 > 0xFF:
            s2 ^= ROOT
        s3 = s2 ^ s
        s4 = s2 << 1
        if s4 > 0xFF:
            s4 ^= ROOT
        s5 = s4 ^ s
        s8 = s4 << 1
        if s8 > 0xFF:
            s8 ^= ROOT
        s9 = s8 ^ s

        S[i] = s
        t = (
            (s << 56) | (s << 48) | (s3 << 40) | (s << 32) |
            (s5 << 24) | (s8 << 16) | (s9 << 8) | s5
        )
        T0[i] = t
        T1[i] = rotl64(t, 8)
        T2[i] = rotl64(t, 16)
        T3[i] = rotl64(t, 24)
        T4[i] = rotl64(t, 32)
        T5[i] = rotl64(t, 40)
        T6[i] = rotl64(t, 48)
        T7[i] = rotl64(t, 56)

    for r in range(R):
        rc[r] = (
            (S[j] << 56) | (S[j + 1] << 48) | (S[j + 2] << 40) | (S[j + 3] << 32) |
            (S[j + 4] << 24) | (S[j + 5] << 16) | (S[j + 6] << 8) | S[j + 7]
        )
        j += 8


init_tables()


def transform(block, hash_val):
    """
    :param block: bytes de 64 bytes (512 bits)
    :param hash_val: lista de 8 inteiros de 64 bits (state hash)
    """
    # Expand input
    block = list(struct.unpack('>8Q', block))
    k = hash_val.copy()
    state = [block[i] ^ k[i] for i in range(8)]

    # Key schedule
    for r in range(R):
        L = [0] * 8
        for i in range(8):
            L[i] = (
                T0[(k[i >> 0] >> 56) & 0xFF] ^
                T1[(k[(i - 1) & 7] >> 48) & 0xFF] ^
                T2[(k[(i - 2) & 7] >> 40) & 0xFF] ^
                T3[(k[(i - 3) & 7] >> 32) & 0xFF] ^
                T4[(k[(i - 4) & 7] >> 24) & 0xFF] ^
                T5[(k[(i - 5) & 7] >> 16) & 0xFF] ^
                T6[(k[(i - 6) & 7] >> 8) & 0xFF] ^
                T7[(k[(i - 7) & 7]) & 0xFF]
            )
        k = L
        k[0] ^= rc[r]

        # Apply round transformation
        L2 = [0] * 8
        for i in range(8):
            L2[i] = (
                T0[(state[i >> 0] >> 56) & 0xFF] ^
                T1[(state[(i - 1) & 7] >> 48) & 0xFF] ^
                T2[(state[(i - 2) & 7] >> 40) & 0xFF] ^
                T3[(state[(i - 3) & 7] >> 32) & 0xFF] ^
                T4[(state[(i - 4) & 7] >> 24) & 0xFF] ^
                T5[(state[(i - 5) & 7] >> 16) & 0xFF] ^
                T6[(state[(i - 6) & 7] >> 8) & 0xFF] ^
                T7[(state[(i - 7) & 7]) & 0xFF]
            ) ^ k[i]
        state = L2

    # Finalize hash
    for i in range(8):
        hash_val[i] ^= state[i] ^ block[i]


class Whirlpool2000:
    def __init__(self):
        self._buffer = b''
        self._counter = 0  # em bits
        self._hash = [0] * 8  # 8 blocos de 64 bits

    def update(self, data: bytes):
        self._buffer += data
        self._counter += len(data) * 8  # bits

        while len(self._buffer) >= 64:
            block = self._buffer[:64]
            self._buffer = self._buffer[64:]
            transform(block, self._hash)

    def _finalize(self):
        # Padding: append '1' bit, then zeroes, then 64-bit length
        pad_len = 64 - ((self._counter // 8 + 9) % 64)
        pad = b'\x80' + b'\x00' * pad_len + struct.pack('>Q', self._counter)
        self.update(pad)

    def digest(self) -> bytes:
        hash_copy = self._hash[:]
        buffer_copy = self._buffer
        counter_copy = self._counter

        self._finalize()
        result = b''.join(struct.pack('>Q', h) for h in self._hash)

        # Restaura estado original (para múltiplos .digest() sem quebrar)
        self._hash = hash_copy
        self._buffer = buffer_copy
        self._counter = counter_copy

        return result

    def hexdigest(self) -> str:
        return self.digest().hex()


if __name__ == '__main__':
    import base64
    h = Whirlpool2000()
    h.update(b"yang")
    password = h.hexdigest()
    hash = base64.b64encode(password.encode()).decode()
    print(hash)
