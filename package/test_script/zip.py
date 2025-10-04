import os
import zipfile

def add_to_zip(zipf, path, arcname=None):
    """递归地将文件或文件夹添加到 ZIP 文件中"""
    if os.path.isfile(path):
        zipf.write(path, arcname or path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算在 ZIP 文件中的相对路径
                archive_path = os.path.relpath(file_path, os.path.dirname(path))
                zipf.write(file_path, archive_path)

def zip_files_and_folders(file_path, folder_path, output_zip):
    """将文件和文件夹压缩到一个 ZIP 文件中"""
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if not file_path and not folder_path:
                print("错误: 至少需要提供一个文件或文件夹路径")
                os.remove(output_zip)
                return
            if isinstance(file_path, str):
                file_path = [file_path]
            if isinstance(folder_path, str):
                folder_path = [folder_path]
            # 添加单个文件
            if file_path:
                if isinstance(file_path, list):
                    for file in file_path:
                        if os.path.exists(file) and os.path.isfile(file):
                            add_to_zip(zipf, file)
                            print(f"add: {file}")
                        else:
                            print(f"not found file: {file}")

            # 添加文件夹
            if folder_path:
                if isinstance(folder_path, list):
                    for folder in folder_path:
                        if os.path.exists(folder) and os.path.isdir(folder):
                            add_to_zip(zipf, folder)
                            print(f"add: {folder}")
                        else:
                            print(f"not found folder: {folder}")
        print(f"压缩完成! ZIP 文件已保存为: {output_zip}")
        return
    except Exception as e:
        print(f"压缩过程中发生错误: {e}")
        return
if __name__ == "__main__":
    # usage
    print('usage:')
    print("="*42)
    print("from zip import zip_files_and_folders")
    print("zip_files_and_folders('file_path', 'folder_path', 'output_zip')")