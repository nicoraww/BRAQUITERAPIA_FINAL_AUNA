import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pydicom
import plotly.graph_objects as go
import tempfile
import shutil
from skimage.transform import resize

# Configuración inicial de la página
st.set_page_config(page_title="Brachyanalysis", layout="wide")

st.markdown("""
    <style>
    .giant-title {
        font-size: 45px !important;
        font-weight: bold;
        color: #28aec5;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Función para cargar archivos DICOM desde un directorio
def load_dicom_directory(directory):
    slices = []
    for filename in sorted(os.listdir(directory)):
        path = os.path.join(directory, filename)
        try:
            ds = pydicom.dcmread(path)
            if hasattr(ds, 'SliceLocation'):
                slices.append(ds)
        except:
            pass
    slices.sort(key=lambda x: float(getattr(x, 'SliceLocation', 0)))
    return slices

# Función para aplicar ventana y nivel
def apply_window_level(image, ww, wc):
    img = image.astype(np.float32)
    img = (img - (wc - ww / 2)) / ww
    img = np.clip(img, 0, 1)
    return img

# Cargar DICOMs
st.sidebar.title("Cargar archivos DICOM")
uploaded_files = st.sidebar.file_uploader("Sube una carpeta de DICOMs comprimida (.zip)", type=["zip"], accept_multiple_files=False)

if uploaded_files:
    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_path = os.path.join(tmpdirname, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_files.getbuffer())
        shutil.unpack_archive(zip_path, tmpdirname)
        dicom_files = load_dicom_directory(tmpdirname)

        if len(dicom_files) > 0:
            slices = dicom_files
            slices.sort(key=lambda x: float(getattr(x, 'SliceLocation', 0)))
            pixel_spacing = slices[0].PixelSpacing
            slice_thickness = slices[0].SliceThickness
            spacing = (*pixel_spacing, slice_thickness)
            img = np.stack([s.pixel_array for s in slices])
            original_image = img.copy()
        else:
            st.warning("No se encontraron archivos DICOM válidos.")
            img = None
else:
    img = None

# Visualización
if img is not None:
    n_ax, n_cor, n_sag = img.shape
    st.sidebar.subheader("Opciones de visualización")
    slice_axial = st.sidebar.slider("Corte axial", 0, n_ax - 1, n_ax // 2)
    slice_coronal = st.sidebar.slider("Corte coronal", 0, n_cor - 1, n_cor // 2)
    slice_sagittal = st.sidebar.slider("Corte sagital", 0, n_sag - 1, n_sag // 2)

    # Presets de ventana
    min_val, max_val = float(img.min()), float(img.max())
    default_ww = max_val - min_val
    default_wc = min_val + default_ww / 2
    presets = {"Default": (default_ww, default_wc), "CT Abdomen": (350, 50), "CT Bone": (2000, 350), "Custom": None}
    preset_choice = st.sidebar.selectbox("Presets ventana", list(presets.keys()))
    if preset_choice != "Custom":
        ww, wc = presets[preset_choice]
    else:
        ww = st.sidebar.number_input("Ancho de ventana (WW)", 1.0, default_ww * 2, default_ww)
        wc = st.sidebar.number_input("Centro ventana (WL)", min_val - default_ww, max_val + default_ww, default_wc)

    # Función para renderizar cortes
    def render2d(slice2d):
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.axis('off')
        ax.imshow(apply_window_level(slice2d, ww, wc), cmap='gray', origin='lower')
        return fig

    ax_fig = render2d(img[slice_axial, :, :])
    cor_fig = render2d(img[:, slice_coronal, :])
    sag_fig = render2d(img[:, :, slice_sagittal])

    # Imagen 3D
    target_shape = (64, 64, 64)
    img_resized = resize(original_image, target_shape, anti_aliasing=True)
    x, y, z = np.mgrid[0:target_shape[0], 0:target_shape[1], 0:target_shape[2]]
    fig3d = go.Figure(data=go.Volume(
        x=x.flatten(), y=y.flatten(), z=z.flatten(),
        value=img_resized.flatten(),
        opacity=0.1,
        surface_count=15,
        colorscale="Gray",
    ))
    fig3d.update_layout(margin=dict(l=0, r=0, b=0, t=0))

    # Mostrar todo en un solo cuadro
    st.markdown("""
    <div style='border: 3px solid #28aec5; border-radius: 10px; padding: 15px; margin-top: 25px;'>
    <h3 style='color:#28aec5;text-align:center;'>Visualización en 4 cuadrantes</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Vista Axial")
        st.pyplot(ax_fig)
        st.markdown("#### Vista Sagital")
        st.pyplot(sag_fig)

    with col2:
        st.markdown("#### Vista Coronal")
        st.pyplot(cor_fig)
        st.markdown("#### Vista 3D")
        st.plotly_chart(fig3d, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Encabezado y pie de página
st.markdown('<p class="giant-title">Brachyanalysis</p>', unsafe_allow_html=True)
st.markdown("""
<hr>
<div style="text-align:center;color:#28aec5;font-size:14px;">
    Brachyanalysis - Visualizador de imágenes DICOM
</div>
""", unsafe_allow_html=True)
