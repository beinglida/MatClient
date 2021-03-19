import zipfile

file_dir = "/Users/mark/Downloads/MatClient/source/Question-client/Q_1.zip"
zipFile = zipfile.ZipFile(file_dir)
print(zipFile.infolist())

