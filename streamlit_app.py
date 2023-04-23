import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio
import os
from zipfile import ZipFile

st.sidebar.title('ESMFold')
st.sidebar.write('[*ESMFold*](https://esmatlas.com/about) is an end-to-end single sequence protein structure predictor based on the ESM-2 language model. For more information, read the [research article](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) and the [news article](https://www.nature.com/articles/d41586-022-03539-1) published in *Nature*.')


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
    
    

# Protein sequence input 
DEFAULT_SEQ = ""
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)
line_data=''



#Directory
directory = 'my_folder'
if not os.path.exists(directory):
    os.makedirs(directory)

uploaded_files = st.sidebar.file_uploader("Upload Fasta files", accept_multiple_files=True)
list_of_files={"Name":[],"Sequence":[]}
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    str_data = bytes_data.decode('utf-8')  # convert bytes to str
    line_data = str_data.split('\n')[1]
    #st.write("filename:", uploaded_file.name)
    #st.write(bytes_data)
    list_of_files["Name"].append(uploaded_file.name[:-3])
    list_of_files["Sequence"].append(line_data)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=line_data)
    name = line_data[:3] + line_data[-3:]
    pdb_string = response.content.decode('utf-8')

    with open(f'{directory}/{uploaded_file.name[:-3]}.pdb', 'w') as f:
        f.write(pdb_string)
    st.download_button(
        label=f"Download {uploaded_file.name[:-3]}",
        data=pdb_string,
        file_name=f'{uploaded_file.name[:-3]}.pdb',
        mime='text/plain',
    )
    # save as third value of dictionary, add each item to a zip file for download
     
    
#st.write(list_of_files)

with ZipFile(f'{directory}.zip', 'w') as zip:
    for file in os.listdir(directory):
        zip.write(os.path.join(directory, file), file)

# create a download button for the zip file
st.download_button(
    label="Download all files as zip",
    data=open(f'{directory}.zip', 'rb').read(),
    file_name=f'{directory}.zip'
)


    


# ESMfold
def update(sequence=line_data):
    
 
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    name = sequence[:3] + sequence[-3:]
    pdb_string = response.content.decode('utf-8')

    with open('predicted.pdb', 'w') as f:
        f.write(pdb_string)

    struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
    b_value = round(struct.b_factor.mean(), 4)

    # Display protein structure
    st.subheader('Visualization of predicted protein structure')
    render_mol(pdb_string)

    # plDDT value is stored in the B-factor field
    st.subheader('plDDT')
    st.write('plDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
    st.info(f'plDDT: {b_value}')

    st.download_button(
        label="Download PDB",
        data=pdb_string,
        file_name='predicted.pdb',
        mime='text/plain',
    )


    
predict = st.sidebar.button('Predict', on_click=update)


if not predict:
    st.sidebar.warning('Enter protein sequence data or upload 1 or more fasta files')
