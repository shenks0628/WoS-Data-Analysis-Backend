# WoS Data Analysis Backend
## API documentation
* 詳細 API 說明文件已上傳至 HackMD，連結 https://hackmd.io/@shen0628/WoS-API

## Steps to run the backend server locally
* 使用前須將以下部分註解「**去除**」：
  * requirements.txt 中最後三行（下載必要程式庫；另外，可將檔案中的 gunicorn 註解掉，因為本地端運行用不到）
  * fileSecure.py 中第 8、10 行（load .env）
  * server.py 中第 27 ~ 28 行、第 840 ~ 1142 行（Enable BERT model for semantic keyword clustering）
* 使用 pip 下載會用到的程式庫 `pip install -r requirements.txt`
* 做完以上步驟即可順利執行 `python server.py`

## Others
* 應自行生成 Firebase 的 apiKey 並加密。
* serviceAccount.json.secure 是 Firebase Admin SDK 的密鑰檔案經過 fileSecure.py 中的 encrypt_file 函式產生的檔案。欲解密請使用 decrypt_to_string 函式。
* server.py 中的第 45 行是 Firebase 的 apiKey 經過 fileSecure.py 中的 encrypt_string 函式所取得。欲解密請使用 decrypt_string 函式。

## Details
For further information and system details, feel free to contact me or other contributors.
