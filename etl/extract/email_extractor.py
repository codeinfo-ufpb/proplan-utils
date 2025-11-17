import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import os
import argparse
from pathlib import Path
import re
from dateutil import parser as date_parser
from config.settings import settings
from .extraction_models import SourceMetadata
from core.base_extractor import BaseExtractor 
from common.logging_utils import get_logger
from .file_utils import extract_and_trash_zip

def extract_and_trash_zip(zip_path, dest_dir):
    # Método para realizar a extração dos dados nos formatos .zip dos arquivos que vierem dos e-mail estabelecidos nos parâmetros.
    import zipfile
    logger = get_logger("email-extractor")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extracted_paths = [str(Path(dest_dir) / name) for name in zip_ref.namelist()]
            zip_ref.extractall(dest_dir)
        os.remove(zip_path)
        return extracted_paths
    except Exception as e:
        logger.error(f"[ERRO] Houve uma falha no processo de extração do arquivo. Arquivo: {zip_path}: {e}")
        return []
    # Fim do método de extração de arquivos .zip

class EmailExtractor(BaseExtractor):
    """
    Classe responsável pelo download dos arquivos nos formatos (CSV, XLS, XLSX, ZIP entre outros que se fizerem necessários no futuro). 
    Parametrizado para aceitar uma data de início de busca, realizar busca por termos chaves no assunto. Caso não seja informado nenhuma data temos o default de 30 dias para buscar os e-mails.
    """

    def __init__(self):

        self.logger = get_logger("email-extractor")
        
        # Variáveis com os parâmetros necessários para a extração.
        self.email_user = os.getenv("EMAIL")
        self.email_pass = os.getenv("EMAIL_PWD")
        self.remetente_esperado = os.getenv("EMAIL_IN")
        self.imap_server = os.getenv("IMAP_SERVER")
        self.imap_port = int(os.getenv("IMAP_PORT", 993))
        self.imap_folder = os.getenv("IMAP_FOLDER", "INBOX")
        assunto_chave_str = os.getenv("EMAIL_SUBJECT", os.getenv("EMAIL_SUBJECT", "DW_TESTE"))
        self.assunto_chaves = [k.strip().lower() for k in assunto_chave_str.split(',') if k.strip()]
        self.valid_extensions = ("xls", "xlsx", "zip", "csv")
        #  Fim das variáveis com os parâmetros necessários para extração.

        # Definição do diretório de destino dos arquivos baixados do e-mail.
        self.dir_destino = Path(settings.DIR_RAW_EMAIL)
        
    def _check_credentials(self):
        """Método para verificar as credenciais obrigatórias e caso estejam ausentes retorna com erro."""
        
        if not all([self.email_user, self.email_pass, self.imap_server, self.remetente_esperado]):
            self.logger.error("[ERRO] : Credenciais IMAP obrigatórias. Verique (EMAIL, EMAIL_PWD, IMAP_SERVER, EMAIL_IN) que estão ausentes ou são inválidas. <<< Extração abortada >>>.")
            raise ValueError("Credenciais IMAP foram retornadas e abortadas.")

    def _is_subject_match(self, subject: str) -> bool:
        """Método para verificar se o assunto contém qualquer uma das palavras-chave definidas."""
        if not self.assunto_chaves:
            # Se a lista de chaves estiver vazia, significa que não há filtro por assunto.
            return True
        subject_lower = subject.lower()
        for key in self.assunto_chaves:
            if key in subject_lower:
                return True
        return False
    
    def _decode_header(self, header_value):
        """Método para decodificar os cabeçalhos dos e-mails."""

        try:
            decoded, charset = decode_header(header_value)[0]
            if isinstance(decoded, bytes):
                return decoded.decode(charset or "utf-8", errors="ignore")
            return str(decoded)
        except Exception:
            return str(header_value)
    
    def _get_clean_email(self, full_from_header: str) -> str:
        "Método para extrair o endereço de e-mail do cabeçalho 'FROM' - Remetente "
        
        match = re.search(r'<(.+?)', full_from_header)
        return match.group(1) if match else full_from_header.strip()
    
    def _parse_email_date(self, date_header: str) -> datetime:
        "Método para converter o cabeçalho de data do e-mail para um objeto datetime."
        
        try:
            return date_parser.parse(date_header)
        except Exception:
            self.logger.info(f"[INFO] Não foi possível realizar o parser da data do e-mail: {date_header}. Usando a data atual.")
            return datetime.now()
        
    def extract(self, since_date: datetime = None) -> list[SourceMetadata]:
        """
        Método principal para extração dos arquivos do e-mail, requer uma data de início explícita.
        - Args: since_date (datetime): Data a partir da qual a busca de e-mails deve começar.     
        - Returns: List[SourceMetadata]: Lista de objetos metadados dos arquivos extraídos com sucesso.
        """
        self.logger.info("[STATUS] Iniciando a extração dos anexos do e-mail...")

        try:
            self._check_credentials()
            # Criação do diretório onde será armazenado os arquivos extraídos, caso não exista.
            self.dir_destino.mkdir(parents=True, exist_ok=True)
        except ValueError:
            return []
        
        except Exception as e:
            self.logger.error(f"[ERRO] Falha ao criar diretório: {e}")
            return []

        if since_date is None:
            since_date = datetime.today() - timedelta(days=30)
            self.logger.info(f"[INFO] A busca dos anexos nos e-mails data do período desde: {since_date.strftime('%d/%m/%Y')}.")
            self.logger.info(f"[INFO] Na Pasta IMAP alvo: '{self.imap_folder}'. As Palavras-Chave de Assunto são: {self.assunto_chaves or 'Nenhuma (Buscará todos os assuntos)'}")

        extracted_metadata: list[SourceMetadata] = []
        mail = None

        try:
            # Realiza conexão com o IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_user, self.email_pass)

            # Seleciona a pasta para armazenamento
            mail.select(self.imap_folder)
            self.logger.info(f"[OK] Conexão IMAP bem-sucedida e pasta '{self.imap_folder}' selecionada.")

            # IMAP com os critério de busca
            date_str = since_date.strftime("%d-%b-%Y")
            criteria = f'(SINCE "{date_str}" FROM "{self.remetente_esperado}")'
            self.logger.info(f"[INFO] Critérios de busca IMAP (apenas data e remetente): {criteria}")
            result, data = mail.search(None, criteria)

            if result != "OK":
                self.logger.error("[ERROR] Ocorreu um falha ao buscar anexos no e-mail.")
                return []

            uids = data[0].split()
            self.logger.info(f"[INFO] {len(uids)} e-mail(s) encontrados na busca IMAP inicial.")

            for uid in uids:
                # Resultado da chamada
                result, msg_data = mail.fetch(uid, "(RFC822)")
                if result != "OK":
                    self.logger.warning(f"[AVISO] Não foi possível buscar e-mail UID {uid.decode()}")
                    continue

                msg = email.message_from_bytes(msg_data[0][1])

                uid_str = uid.decode()
                assunto = self._decode_header(msg["Subject"])
                from_header = self._decode_header(msg["From"])
                sender_email = self._get_clean_email(from_header)
                date_received = self._parse_email_date(msg["Date"])
                self.logger.info(f"[INFO] Processando UID {uid_str}: Assunto: {assunto}, De:{sender_email}")

                # Filtro com o conteúdo. Busca por mais de um critério chave no assunto do e-mail. 
                if not self._is_subject_match(assunto):
                    self.logger.info(f"[INFO] E-mail (UID: {uid.decode()}) ignorado: O assunto '{assunto}' não contém nenhuma das palavras-chave.")
                    continue

                # Itera sobre as partes do e-mail para encontrar anexos, caso não tenha anexos o if irá ignorar
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                        continue
                    
                    filename_encoded = part.get_filename()
                    if not filename_encoded:
                        continue
                    decoded_filename = self._decode_header(filename_encoded)
                    
                    # Verifica se as extensões são válidas dentro da lista necessária para download.
                    ext = decoded_filename.split('.')[-1].lower()
                    if ext not in self.valid_extensions:
                        self.logger.info(f"[AVISO] Anexos ignorados: {decoded_filename} (Extensão não é suportada. Consulte a lista do tipo de arquivo: .{ext})")
                        continue

                    caminho = self.dir_destino / decoded_filename

                    # Início dos Metadados Básicos do E-mail
                    attachment_metadata = SourceMetadata(
                        message_id=uid_str,
                        sender_email=sender_email,
                        subject=assunto,
                        date_received=date_received,
                        other_info={"saved_path": str(caminho), "original_from_header": from_header}
                    )

                    # Verifica se o arquivo já existe, caso exista não fará o download para que não haja duplicidade
                    if caminho.exists():
                        self.logger.info(f"[INFO] O arquivo já existe! Nome do arquivo é: {decoded_filename}")
                        extracted_metadata.append(attachment_metadata)
                        continue
                    
                    else:
                        # Salva o arquivo, caso não exista!
                        with open(caminho, "wb") as f:
                            f.write(part.get_payload(decode=True))
                            self.logger.info(f"[OK] Anexo salvo: {caminho}")

                    # Lida com a extração de ZIPs. Caso o arquivo tem arquivos compactados, será realizada a extração e armazenado o conteúdo do zip.
                    if ext == "zip":
                        self.logger.info(f"[INFO] Arquivo ZIP detectado. Extraindo e limpando pasta com o arquivo .zip: {caminho}")
                        extracted_paths = extract_and_trash_zip(caminho, self.dir_destino)

                        for new_path in extracted_paths:
                            new_filename = Path(new_path).name
                            zip_metadata = SourceMetadata(
                                message_id=uid_str,
                                sender_email=sender_email,
                                subject=assunto,
                                date_received=date_received,
                                other_info={"saved_path": new_path, "original_from_header": from_header, "extracted_from_zip": decoded_filename})
                            extracted_metadata.append(zip_metadata)
                    else:
                        extracted_metadata.append(attachment_metadata)


            self.logger.info(f"[OK] A extração foi concluída com sucesso. Temos {len(extracted_metadata)} arquivo(s) processado(s).")
            return extracted_metadata
        
        except imaplib.IMAP4.error as e:
             self.logger.error(f"Ops! [ERRO] Houve falha no IMAP durante o processo: Consulte o erro: {e}")
             return []
       
        except Exception as e:
            self.logger.error(f"Ops! [ERRO] Tivemos uma falha durante o processo de extração: Consulte o erro: {e}")
            return []
       
        finally:
            if mail:
                try:
                    mail.logout()
                    self.logger.info("[OK] Realizado a saída do processo. IMAP bem-sucedido!")
                except Exception:
                    # Ignora erros de logout se a conexão já estava quebrada
                    pass

def main():
        """Função principal para execução via linha de comando."""
        # src/pipelines/tesouro_gerencial/email_extractor.py --date 2024-06-15
        # python3 src/pipelines/tesouro_gerencial/email_extractor.py --days 1
        # python3 src/pipelines/tesouro_gerencial/email_extractor.py --days 7
        # python3 src/pipelines/tesouro_gerencial/email_extractor.py
        
        parser = argparse.ArgumentParser(description="Extrator de anexos de e-mail IMAP para ETL. Permite buscar por data ou dias passados.")

        # Argumentos mutuamente exclusivos para definição da data de início
        group = parser.add_mutually_exclusive_group()
        
        group.add_argument("--date", 
                        type=str, 
                        help="Data de início explícita para a busca (formato YYYY-MM-DD).")
        
        group.add_argument("--days", 
                        type=int, 
                        default=30, # Padrão para 30 dias se nada for especificado, pode ser alterado.
                        help="Número de dias passados para iniciar a busca (ex: 7 para a última semana). Padrão: 30 dias.")

        args = parser.parse_args()

        # Determina a data de início (since_date)
        if args.date:
            try:
            # Se a data for fornecida, tenta converter
                since_date = datetime.strptime(args.date, "%Y-%m-%d")
            except ValueError:
                print("Erro: Formato de data inválido. Use YYYY-MM-DD.")
                return
        else:
        # Se --days for usado (ou for o padrão 30)
            since_date = datetime.today() - timedelta(days=args.days)

        # Executa a extração
        try:
            extractor = EmailExtractor()
            # Chama o método extract com a data calculada/fornecida
            extracted_files = extractor.extract(since_date=since_date)
            if extracted_files:
                print(f"\nExtrator concluído. Arquivos baixados/processados: {len(extracted_files)}")
            else:
                print("\nExtrator concluído. Nenhum arquivo novo foi baixado.")
                
        except ValueError:
            pass
        except Exception as e:
            print(f"\nFalha na execução principal: {e}")

if __name__ == "__main__":
     main()


                        
