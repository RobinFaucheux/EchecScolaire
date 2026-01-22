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

def generer_cles_ecdh():
    """
    Génère une paire de clés ECDH (Privée, Publique).
    """
    cle_privee = ec.generate_private_key(ec.SECP256R1())
    cle_publique = cle_privee.public_key()
    return cle_privee, cle_publique

def serialiser_cle_publique(cle_publique):
    """
    Convertit la clé publique en octets (PEM) pour l'envoi.
    """
    return cle_publique.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def charger_cle_publique(pem_bytes):
    """
    Charge une clé publique depuis des octets.
    """
    return serialization.load_pem_public_key(pem_bytes)

def calculer_secret_partage(ma_cle_privee, cle_publique_distante):
    """
    Calcule le secret partagé ECDH.
    """
    return ma_cle_privee.exchange(ec.ECDH(), cle_publique_distante)

def deriver_cle_session(secret_partage):
    """
    Dérive une clé de session (AES/Fernet) depuis le secret partagé.
    """
    # Fernet a besoin d'une clé de 32 octets encodée en base64
    cle_derivee = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(secret_partage)
    return base64.urlsafe_b64encode(cle_derivee)

def hacher_mdp(mot_de_passe):
    """
    Hache le mot de passe (SHA256).
    """
    return hashlib.sha256(mot_de_passe.encode()).hexdigest()

def verifier_mdp(hash_stocke, mot_de_passe):
    """
    Vérifie le mot de passe hashé correspond à la base.
    """
    return hash_stocke == hashlib.sha256(mot_de_passe.encode()).hexdigest()

class SocketSecurise:
    """
    Classe remplaçant le socket pour chiffrer/déchiffrer automatiquement grâce à Fernet
    """
    def __init__(self, socket, cle_de_session):
        self.socket = socket
        self.fernet = Fernet(cle_de_session)        
        self.tampon = ""
        # On utilise un makefile binaire pour lire les données brutes
        self.rfile = self.socket.makefile('rb') 

    def write(self, message_en_clair):
        """Ajoute le message au tampon interne."""
        if message_en_clair:
            self.tampon += message_en_clair

    def flush(self):
        """Vide le tampon : chiffre son contenu et l'envoie sur le réseau."""
        if not self.tampon:
            return

        # On chiffre tout
        message_chiffre = self.fernet.encrypt(self.tampon_ecriture.encode('utf-8'))
        
        # DEBUG : Montrer que c'est chiffré SUPPRIMER EN PROD
        print(f"\n[CRYPTO] Envoi sur réseau : {message_chiffre[:30]}... (Total {len(message_chiffre)} bytes)")
        
        # On envoie le tout + un retour à la ligne pour séparer les messages chiffrés
        self.socket.sendall(message_chiffre + b'\n')
        # Reset
        self.tampon = ""

    def readline(self):
        """Lit une ligne chiffrée du réseau et la déchiffre."""
        try:
            ligne_chiffree = self.rfile.readline()
            if not ligne_chiffree:
                return ""
            
            # Nettoyage
            ligne_chiffree = ligne_chiffree.strip()
            if not ligne_chiffree:
                return ""
            
            # Déchiffrement
            message_dechiffre = self.fernet.decrypt(ligne_chiffree)
            return message_dechiffre.decode('utf-8')
        except Exception as e:
            print(f"Erreur de sécurité (déchiffrement impossible) : {e}")
            return ""

    def close(self):
        self.rfile.close()
        self.socket.close()
