import logging
import warnings
from Bio import SeqIO
from Bio.Seq import Seq
from Bio import SeqUtils
import pyfastx
import pandas as pd
import sys
import importlib

logger = logging.getLogger('pythia.integration')

# Define a global variable to track the last used dropdown_value
last_celltype = None

# Append the module path
sys.path.insert(0, './Indelphi_installation/inDelphi-model-master')

# Import the module initially
import inDelphi

def reload_inDelphi_if_needed(dropdown_value):
    global last_celltype, inDelphi
    if dropdown_value != last_celltype:
        inDelphi = importlib.reload(inDelphi)
        inDelphi.init_model(celltype=dropdown_value)
        last_celltype = dropdown_value

def process_pythia_integration(input_box_value, input_box_2_value, input_box_3_value, dropdown_value):
    logger.info("Calculation started (pre-designed gRNA, cell type: %s)", dropdown_value)
    warnings.filterwarnings('ignore')
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Reload and reinitialize inDelphi module if dropdown_value changes
    reload_inDelphi_if_needed(dropdown_value)

    import altair as alt

    # Initialize data structures
    results_df = pd.DataFrame()
    gRNA = "test_string"
    
    Left = input_box_value
    Right = input_box_2_value
    Casette = input_box_3_value
    
    # Run code for left boundary
    for i in range(2, 7):
        for j in range(1, 6):
            Left_donor = Left[len(Left) - i:] * j + Casette
            ology = Left[len(Left) - i:]
            
            pred_df, stats = inDelphi.predict(Left + Left_donor, (len(Left)))
            pred_df = inDelphi.add_genotype_column(pred_df, stats)
            pred_df = pred_df.dropna(subset=['Genotype'])
            
            for k, row in pred_df.iterrows():
                genotype = row['Genotype']
                for x in range(8):
                    repair_string = Left + ology * x + Casette
                    if repair_string in genotype:
                        frequency = row['Predicted frequency']
                        results_df = results_df.append({"side": "left", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)
    
    # Run code for right boundary
    for i in range(2, 7):
        for j in range(1, 6):
            Right_donor = Casette + (Right[:i] * j)
            ology = Right[:i]
            
            pred_df, stats = inDelphi.predict(Right_donor + Right, (len(Right_donor)))
            pred_df = inDelphi.add_genotype_column(pred_df, stats)
            pred_df = pred_df.dropna(subset=['Genotype'])
            
            for k, row in pred_df.iterrows():
                genotype = row['Genotype']
                for x in range(8):
                    repair_string = Casette + ology * x + Right
                    if repair_string in genotype:
                        frequency = row['Predicted frequency']
                        results_df = results_df.append({"side": "right", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)
    
    # Aggregate and summarize results
    aggregated_df = results_df.groupby(['Amount of trimologies', 'Homol_length', "side"])['Predicted frequency'].sum().reset_index()
    logger.info("Calculation complete — results passed to frontend")
    return aggregated_df

