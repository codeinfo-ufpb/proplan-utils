import os
from pathlib import Path
import zipfile
from etl.extract.file_utils import move_to_trash, extract_zip

def create_dummy_file(file_path):
    """Cria um arquivo de teste com conteúdo dummy."""
    with open(file_path, "w") as f:
        f.write("conteúdo de teste")

def create_dummy_zip(zip_path, files):
    """Cria um arquivo ZIP com arquivos dummy."""
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            create_dummy_file(file)
            zipf.write(file, arcname=os.path.basename(file))
            os.remove(file)  # limpa o arquivo original, só deixa no ZIP

def test_move_to_trash():
    test_file = Path("dummy_file.txt")
    create_dummy_file(test_file)
    print(f"Arquivo criado: {test_file}")
    
    move_to_trash(str(test_file))
    
    trash_file = Path(".trash") / test_file.name
    assert trash_file.exists(), "Arquivo não foi movido para a lixeira!"
    print(f"[OK] move_to_trash funcionou: {trash_file}")
    
    # cleanup
    trash_file.unlink()
    trash_file.parent.rmdir()

def test_extract_zip():
    zip_file = Path("dummy.zip")
    files_inside = ["file1.txt", "file2.txt"]
    create_dummy_zip(zip_file, files_inside)
    
    dest_folder = Path("zip_output")
    extracted_files = extract_zip(str(zip_file), str(dest_folder))
    
    for f in extracted_files:
        assert Path(f).exists(), f"Arquivo não extraído: {f}"
    print(f"[OK] extract_zip funcionou: {extracted_files}")
    
    # cleanup
    for f in extracted_files:
        Path(f).unlink()
    dest_folder.rmdir()
    zip_file.unlink()

if __name__ == "__main__":
    print("Testando move_to_trash...")
    test_move_to_trash()
    print("Testando extract_zip...")
    test_extract_zip()
    print("\nTodos os testes do file_utils concluídos com sucesso!")

