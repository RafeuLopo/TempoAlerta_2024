from azure.storage.blob import BlobServiceClient
import os


def download_blob(connection_string, container_name, blob_name, download_file_path):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print(f"Arquivo {blob_name} baixado para {download_file_path}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")


def upload_blob(connection_string, container_name, blob_name, file_path):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print(f"Arquivo {file_path} enviado para o blob {blob_name}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")


def download_all_blobs(connection_string, container_name, prefix, local_download_path):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        blobs = container_client.list_blobs(name_starts_with=prefix)

        os.makedirs(local_download_path, exist_ok=True)

        for blob in blobs:
            file_name = os.path.basename(blob.name)
            download_file_path = os.path.join(local_download_path, file_name)
            download_blob(connection_string, container_name, blob.name, download_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")


def upload_all_blobs_from_folder(connection_string, container_name, prefix, local_folder):
    try:
        for root, _, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                blob_name = os.path.join(prefix, file)
                upload_blob(connection_string, container_name, blob_name, local_file_path)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
