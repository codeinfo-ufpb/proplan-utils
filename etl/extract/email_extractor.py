import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from os import path, makedirs, getenv
from core.base_extractor import BaseExtractor
from common.logging_utils import get_logger
from .file_utils import extract_and_trash_zip


class EmailExtractor(BaseExtractor):
    """Faz o download e extrai os anexos dos e-mails corporativos/externos via IMAP (CSV, XLS, XLSX, ZIP entre outros). Depois armazena localmente para posterior processamento."""

    def __init__(self):
        self.logger = get_logger("email-extractor")
        
        # Variáveis com os parâmetros de ambiente utilizados em cada módulo do sistema.
        self.email_user = getenv("EMAIL")
        self.email_pass = getenv("EMAIL_PWD")
        self.remetente_esperado = getenv("EMAIL_IN")
        self.imap_server = getenv("IMAP_SERVER")
        self.imap_port = int(getenv("IMAP_PORT", 993))
        self.dir_destino = getenv("DIR_DESTINO", "./data/emails")
        self.assunto_chave = getenv("EMAIL_SUBJECT", "DW_TESTE")
        self.valid_extensions = ("xls", "xlsx", "zip", "csv")
        # Fim das variáveis com os parâmetros

        makedirs(self.dir_destino, exist_ok=True)

    def extract(self, since_date: datetime = None):
        """
        Método para realizar o processo de extração dos anexos presentes nos e-mails/e-mail.
        - Possui os status e demais comunicações que serão armazenadas no log.
        """
        self.logger.info("[STATUS] Iniciando a extração dos anexos do e-mail...")
        if since_date is None:
            since_date = datetime.today() - timedelta(days=30)
            self.logger.info(f"[INFO] A busca dos anexos nos e-mails data do período desde {since_date.strftime('%d/%m/%y')}.")

        arquivos_baixados = []

        try:
            # Conexão IMAP segura
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_user, self.email_pass)
            mail.select("INBOX")

            # Formata data para IMAP: 01-Oct-2025
            date_str = since_date.strftime("%d-%b-%Y")
            criteria = f'(SINCE "{date_str}" FROM "{self.remetente_esperado}" SUBJECT "{self.assunto_chave}")'
            result, data = mail.search(None, criteria)

            if result != "OK":
                self.logger.error("Ops! [ERRO] Falha ao buscar anexos no e-mail.")
                return []

            uids = data[0].split()
            self.logger.info(f"[INFO] {len(uids)} e-mail(s) encontrados.")

            for uid in uids:
                result, msg_data = mail.fetch(uid, "(RFC822)")
                if result != "OK":
                    self.logger.warning(f"[AVISO] Não foi possível buscar e-mail UID {uid.decode()}")
                    continue

                msg = email.message_from_bytes(msg_data[0][1])
                remetente = self._decode_header(msg["From"])
                assunto = self._decode_header(msg["Subject"])
                self.logger.info(f"[INFO] Processando UID {uid.decode()}: {assunto}")

                if self.remetente_esperado.lower() not in remetente.lower():
                    continue

                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    filename = part.get_filename()
                    if not filename:
                        continue

                    decoded_filename = self._decode_header(filename)
                    if not decoded_filename.lower().endswith(self.valid_extensions):
                        self.logger.info(f"[ATENÇÃO] Anexo ignorado: {decoded_filename}")
                        continue

                    caminho = path.join(self.dir_destino, decoded_filename)
                    if path.exists(caminho):
                        self.logger.info(f"[INFO] O arquivo já existe! Nome do arquivo é: {decoded_filename}")
                        arquivos_baixados.append(caminho)
                        continue

                    with open(caminho, "wb") as f:
                        f.write(part.get_payload(decode=True))
                        arquivos_baixados.append(caminho)
                        self.logger.info(f"[OK] Anexo salvo: {caminho}")
                    
                    # Se o arquivo é ZIP, extrai automaticamente
                    if caminho.lower().endswith(".zip"):
                        arquivos_extraidos = extract_and_trash_zip(caminho, self.dir_destino)
                        arquivos_baixados.extend(arquivos_extraidos)

            mail.logout()
            self.logger.info(f"[OK] A extração foi concluída com sucesso. Temos {len(arquivos_baixados)} arquivo(s) processado(s).")
            return arquivos_baixados

        except Exception as e:
            self.logger.error(f"Ops! [ERRO] Tivemos uma falha durante o processo de extração: Erro: {e}")
            return []

    def _decode_header(self, header_value):
        """Decodifica cabeçalhos de e-mail com segurança."""
        try:
            decoded, charset = decode_header(header_value)[0]
            if isinstance(decoded, bytes):
                return decoded.decode(charset or "utf-8", errors="ignore")
            return str(decoded)
        except Exception:
            return str(header_value)
