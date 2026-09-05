"""
GesmedCrypto — encriptación AES-256-GCM para campos sensibles de GesmedWeb.

─── Formato de almacenamiento en columna BLOB ───────────────────────────────
    [ nonce 12 B ] [ ciphertext ] [ GCM-tag 16 B ]
    El tag lo añade/verifica automáticamente AESGCM de `cryptography`.

─── Prerequisito ────────────────────────────────────────────────────────────
    pip install cryptography

─── Variable de entorno requerida ───────────────────────────────────────────
    GESMED_MASTER_KEY = <64 caracteres hexadecimales = 32 bytes>

    Generar una clave nueva (ejecutar una sola vez):
        python -c "import os; print(os.urandom(32).hex())"

    Guardar en .env (NUNCA en control de versiones):
        echo 'GESMED_MASTER_KEY=<resultado_anterior>' >> .env

─── Extender encriptación a nuevas tablas ───────────────────────────────────
    No se requiere modificar este archivo.
    En la función de query que lee la tabla nueva:

        crypto = GesmedCrypto.para_medico(medico_id)
        registro["campo_sensible"] = crypto.desencriptar(row.campo_sensible)

    En la función que escribe:

        crypto = GesmedCrypto.para_medico(medico_id)
        nuevo.campo_sensible = crypto.encriptar(valor_en_claro)

─── Migración futura a clave por médico ─────────────────────────────────────
    1. Descomentar el bloque HKDF en para_medico().
    2. Re-encriptar la BD con un script de migración.
    3. El resto del código no cambia: sigue llamando para_medico(medico_id).
"""

from __future__ import annotations

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ── Caché de clave maestra (cargada una sola vez por proceso) ─────────────────
_key_cache: bytes | None = None


def _load_master_key() -> bytes:
    """Lee y valida GESMED_MASTER_KEY. Lanza EnvironmentError / ValueError si falla."""
    global _key_cache
    if _key_cache is not None:
        return _key_cache

    raw = os.environ.get("GESMED_MASTER_KEY", "").strip()
    if not raw:
        raise EnvironmentError(
            "Variable de entorno GESMED_MASTER_KEY no está definida.\n"
            "Genere una clave: python -c \"import os; print(os.urandom(32).hex())\"\n"
            "Luego añada GESMED_MASTER_KEY=<resultado> a su archivo .env"
        )
    try:
        key = bytes.fromhex(raw)
    except ValueError:
        raise ValueError(
            "GESMED_MASTER_KEY no es un string hexadecimal válido. "
            "Debe contener exactamente 64 caracteres hexadecimales."
        )
    if len(key) != 32:
        raise ValueError(
            f"GESMED_MASTER_KEY debe representar 32 bytes (64 hex chars). "
            f"Se recibieron {len(key)} bytes ({len(raw)} chars)."
        )
    _key_cache = key
    return key


class GesmedCrypto:
    """
    Encriptador AES-256-GCM para campos sensibles de GesmedWeb.

    Uso mínimo:
        crypto = GesmedCrypto.para_medico(medico_id)
        blob   = crypto.encriptar("Juan Pérez")          # → bytes (BLOB)
        texto  = crypto.desencriptar(blob)               # → "Juan Pérez"
    """

    def __init__(self, key: bytes) -> None:
        if len(key) != 32:
            raise ValueError("La clave interna debe ser exactamente 32 bytes.")
        self._aesgcm = AESGCM(key)

    # ── Factoría ──────────────────────────────────────────────────────────────

    @classmethod
    def para_medico(cls, medico_id: int) -> "GesmedCrypto":
        """
        Devuelve una instancia lista para usar.

        Hoy   → clave global (GESMED_MASTER_KEY) para todos los médicos.
        Futuro → descomentar bloque HKDF para derivar clave por medico_id.
        """
        master = _load_master_key()

        # ── Implementación actual: clave global ───────────────────────────────
        return cls(master)

        # ── Implementación futura: clave por médico ───────────────────────────
        # from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        # from cryptography.hazmat.primitives import hashes
        # hkdf = HKDF(
        #     algorithm=hashes.SHA256(),
        #     length=32,
        #     salt=None,
        #     info=f"gesmed:medico:{medico_id}".encode("utf-8"),
        # )
        # return cls(hkdf.derive(master))

    # ── Primitivas ────────────────────────────────────────────────────────────

    def encriptar(self, dato: str) -> bytes:
        """
        Encripta un string UTF-8.

        Returns:
            bytes listos para almacenar en columna BLOB:
            nonce (12 B) | ciphertext | GCM-tag (16 B)

        Raises:
            TypeError si dato no es str.
        """
        if not isinstance(dato, str):
            raise TypeError(f"Se esperaba str, se recibió {type(dato).__name__}.")
        nonce = os.urandom(12)
        ciphertext_tag = self._aesgcm.encrypt(nonce, dato.encode("utf-8"), None)
        return nonce + ciphertext_tag

    def desencriptar(self, dato_cifrado: bytes | None) -> str:
        """
        Desencripta bytes obtenidos de una columna BLOB.

        Returns:
            String en claro. Devuelve "" si dato_cifrado es None o b"".

        Raises:
            InvalidTag  si el dato fue alterado o la clave es incorrecta.
            ValueError  si el blob es demasiado corto para ser válido.
        """
        if not dato_cifrado:
            return ""
        # Mínimo: 12 (nonce) + 0 (payload vacío) + 16 (tag) = 28 bytes
        if len(dato_cifrado) < 28:
            raise ValueError(
                f"Blob demasiado corto ({len(dato_cifrado)} bytes). "
                "Mínimo esperado: 28 bytes (12 nonce + 16 tag)."
            )
        nonce = dato_cifrado[:12]
        ciphertext_tag = dato_cifrado[12:]
        plaintext = self._aesgcm.decrypt(nonce, ciphertext_tag, None)
        return plaintext.decode("utf-8")

    # ── Operaciones sobre colecciones ─────────────────────────────────────────

    def desencriptar_campos(self, registro: dict, campos: list[str]) -> dict:
        """
        Devuelve una COPIA del registro con los campos listados desencriptados.

        Los campos ausentes o con valor None se omiten sin error.
        El registro original no se modifica.

        Ejemplo:
            row = {"nro_hclinica": 1, "nombre_completo": b"...", "cedula_id": b"..."}
            visible = crypto.desencriptar_campos(row, ["nombre_completo", "cedula_id"])
        """
        copia = dict(registro)
        for campo in campos:
            if campo in copia and copia[campo] is not None:
                copia[campo] = self.desencriptar(copia[campo])
        return copia

    def buscar_en_bloque(
        self,
        registros: list[dict],
        campo_busqueda: str,
        texto: str,
        campos_adicionales: list[str] | None = None,
    ) -> list[dict]:
        """
        Busca texto en campo_busqueda (cifrado) sobre una lista de registros.

        Reglas de seguridad:
        - Requiere mínimo 3 caracteres en texto; devuelve [] si no se cumple.
        - Los registros resultantes tienen los campos sensibles en claro
          solo en memoria RAM, nunca en BD ni archivos.
        - Registros con error de desencriptación se descartan silenciosamente
          (clave incorrecta, dato corrupto).

        Args:
            registros:          lista de dicts con campo_busqueda como bytes.
            campo_busqueda:     campo cifrado por el que se filtra.
            texto:              término de búsqueda (case-insensitive, mín. 3 chars).
            campos_adicionales: otros campos cifrados a desencriptar en los
                                resultados (p. ej. ["cedula_id"]).

        Returns:
            Lista de dicts filtrados con campo_busqueda (y campos_adicionales)
            reemplazados por sus valores en claro.
        """
        texto = texto.strip()
        if len(texto) < 3:
            return []

        texto_lower = texto.lower()
        extras = [c for c in (campos_adicionales or []) if c != campo_busqueda]
        resultado: list[dict] = []

        for r in registros:
            try:
                valor_claro = self.desencriptar(r.get(campo_busqueda))
                if texto_lower not in valor_claro.lower():
                    continue
                copia = dict(r)
                copia[campo_busqueda] = valor_claro
                for campo in extras:
                    if campo in copia and copia[campo] is not None:
                        try:
                            copia[campo] = self.desencriptar(copia[campo])
                        except (InvalidTag, ValueError):
                            copia[campo] = ""
                resultado.append(copia)
            except (InvalidTag, ValueError):
                # Registro con clave incorrecta o dato corrupto: descartar
                continue

        return resultado
