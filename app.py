import streamlit as st
import zipfile
import io
import pydicom
import matplotlib.pyplot as plt
import math

st.set_page_config(layout="wide")
st.title("Visor de archivos DICOM en cuadrantes")

uploaded_file = st.file_uploader("Sube un archivo .zip que contenga imágenes DICOM", type=["zip"])

if uploaded_file is not None:
    try:
        dicoms = []
        with zipfile.ZipFile(uploaded_file, "r") as archive:
            for filename in archive.namelist():
                if filename.endswith(".dcm"):
                    with archive.open(filename) as file:
                        try:
                            dicom = pydicom.dcmread(file)
                            dicoms.append((filename, dicom))
                        except Exception as e:
                            st.warning(f"Archivo no válido: {filename} — {e}")

        if not dicoms:
            st.error("No se encontraron archivos DICOM válidos en el .zip.")
        else:
            st.success(f"Se encontraron {len(dicoms)} archivos DICOM válidos.")

            # Calcular filas y columnas para el número de imágenes
            n_images = len(dicoms)
            n_cols = 2
            n_rows = math.ceil(n_images / n_cols)

            fig, axs = plt.subplots(n_rows, n_cols, figsize=(10, 5 * n_rows))

            if n_rows == 1:
                axs = [axs]  # Asegura que axs sea una lista de listas

            for i, (filename, dicom) in enumerate(dicoms):
                row = i // n_cols
                col = i % n_cols
                ax = axs[row][col] if n_rows > 1 else axs[col]

                if "PixelData" in dicom:
                    ax.imshow(dicom.pixel_array, cmap="gray")
                    ax.set_title(f"{filename}", fontsize=10)
                else:
                    ax.set_title(f"{filename} (sin imagen)", fontsize=10)
                ax.axis("off")

            # Ocultar cuadrantes vacíos si hay
            total_subplots = n_rows * n_cols
            for j in range(len(dicoms), total_subplots):
                row = j // n_cols
                col = j % n_cols
                ax = axs[row][col] if n_rows > 1 else axs[col]
                ax.axis("off")

            st.pyplot(fig)

    except zipfile.BadZipFile:
        st.error("El archivo subido no es un .zip válido.")

