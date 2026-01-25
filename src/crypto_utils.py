import os
import base64
import hashlib

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.fernet import Fernet
except ImportError:
    print("Erreur: La librairie 'cryptography' est manquante.")
    print("Installez-la avec: pip install cryptography")
    raise

# --- AJOUTS : Conversion Base64 pour le protocole texte ---
def pem_vers_str(pem_bytes):
    return base64.b64encode(pem_bytes).decode('utf-8')

def str_vers_pem(b64_str):
    return base64.b64decode(b64_str.encode('utf-8'))
# ----------------------------------------------------------

def generer_cles_ecdh():
    cle_privee = ec.generate_private_key(ec.SECP256R1())
    cle_publique = cle_privee.public_key()
    return cle_privee, cle_publique

def serialiser_cle_publique(cle_publique):
    return cle_publique.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def charger_cle_publique(pem_bytes):
    return serialization.load_pem_public_key(pem_bytes)

def calculer_secret_partage(ma_cle_privee, cle_publique_distante):
    return ma_cle_privee.exchange(ec.ECDH(), cle_publique_distante)

def deriver_cle_session(secret_partage):
    cle_derivee = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(secret_partage)
    return base64.urlsafe_b64encode(cle_derivee)

def hacher_mdp(mot_de_passe):
    return hashlib.sha256(mot_de_passe.encode()).hexdigest()

def verifier_mdp(hash_stocke, mot_de_passe):
    return hash_stocke == hashlib.sha256(mot_de_passe.encode()).hexdigest()

class SocketSecurise:
    def __init__(self, socket, cle_de_session=None):
        self.socket = socket
        self.tampon = ""
        self.rfile = self.socket.makefile('rb') 
        self.set_key(cle_de_session)

    def set_key(self, cle):
        if cle:
            self.fernet = Fernet(cle)
            self.encrypted = True
        else:
            self.fernet = None
            self.encrypted = False

    def write(self, message_en_clair):
        if message_en_clair:
            self.tampon += message_en_clair

    def flush(self):
        if not self.tampon: return

        if self.encrypted:
            try:
                message_chiffre = self.fernet.encrypt(self.tampon.encode('utf-8'))
                self.socket.sendall(message_chiffre + b'\n')
            except Exception: pass
        else:
            # Mode clair
            msg = self.tampon.encode('utf-8')
            if not msg.endswith(b'\n'): msg += b'\n'
            self.socket.sendall(msg)
        self.tampon = ""

    def readline(self):
        try:
            line = self.rfile.readline()
            if not line: return ""
            line = line.strip()
            if not line: return ""
            
            if self.encrypted:
                try:
                    return self.fernet.decrypt(line).decode('utf-8')
                except: return ""
            else:
                return line.decode('utf-8')
        except: return ""

    def close(self):
        try:
            self.rfile.close()
            self.socket.close()
        except: pass