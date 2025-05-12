# ... [todas las importaciones y funciones anteriores se mantienen igual]

# Visualización 2D y 3D en cuadrícula de 2x2
if img is not None:
    n_ax, n_cor, n_sag = img.shape
    st.sidebar.subheader("Opciones de visualización")
    slice_axial = st.sidebar.slider("Corte axial", 0, n_ax - 1, n_ax // 2)
    slice_coronal = st.sidebar.slider("Corte coronal", 0, n_cor - 1, n_cor // 2)
    slice_sagittal = st.sidebar.slider("Corte sagital", 0, n_sag - 1, n_sag // 2)

    # Presets de ventana
    min_val, max_val = float(img.min()), float(img.max())
    default_ww = max_val - min_val
    default_wc = min_val + default_ww/2
    presets = {"Default": (default_ww, default_wc), "CT Abdomen": (350, 50), "CT Bone": (2000, 350), "Custom": None}
    preset_choice = st.sidebar.selectbox("Presets ventana", list(presets.keys()))
    if preset_choice != "Custom":
        ww, wc = presets[preset_choice]
    else:
        ww = st.sidebar.number_input("Ancho de ventana (WW)", 1.0, default_ww * 2, default_ww)
        wc = st.sidebar.number_input("Centro ventana (WL)", min_val - default_ww, max_val + default_ww, default_wc)

    # Renderizar cortes
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

    # Cuadro general con estilo
    st.markdown("""
    <div style='border: 3px solid #28aec5; border-radius: 10px; padding: 15px; margin-top: 25px;'>
    <h3 style='color:#28aec5;text-align:center;'>Visualización en 4 cuadrantes</h3>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Vista Axial")
        st.pyplot(ax_fig)
        st.markdown("#### Vista Sagital")
        st.pyplot(sag_fig)

    with col_right:
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

