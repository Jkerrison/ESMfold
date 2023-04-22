import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio


# stmol
def render_mol(pdb):
    pdbview = py3Dmol.view()
    pdbview.addModel(pdb,'pdb')
    pdbview.setStyle({'cartoon':{'color':'spectrum'}})
    pdbview.setBackgroundColor('white')#('0xeeeeee')
    pdbview.zoomTo()
    pdbview.zoom(2, 800)
    pdbview.spin(True)
    showmol(pdbview, height = 500,width=800)
    
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)
