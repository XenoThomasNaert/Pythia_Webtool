
import logging
import warnings
warnings.filterwarnings('ignore')
warnings.filterwarnings("ignore", category=DeprecationWarning)

logger = logging.getLogger('pythia.editing')
from Bio import SeqIO
from Bio.Seq import Seq
from Bio import SeqUtils
from Bio import SeqIO
import pyfastx
import pandas as pd
import sys
sys.path.insert(0, '/home/lienkamplab/Pythia/Indelphi_installation/inDelphi-model-master')
import inDelphi
import importlib


# Define a global variable to track the last used dropdown_value
last_celltype = None

def reload_inDelphi_if_needed(dropdown_value):
    global last_celltype, inDelphi
    if dropdown_value != last_celltype:
        inDelphi = importlib.reload(inDelphi)
        inDelphi.init_model(celltype=dropdown_value)
        last_celltype = dropdown_value

def process_pythia_editing(input_box_value, input_box_2_value, input_box_3_value, input_box_4_value, dropdown_value, min_length, max_length):
    total_combos = (max_length - min_length) ** 2
    logger.info("Editing calculation started — scoring %d arm-length combinations (cell type: %s)", total_combos, dropdown_value)

    warnings.filterwarnings('ignore')
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Reload and reinitialize inDelphi module if dropdown_value changes
    reload_inDelphi_if_needed(dropdown_value)

    if dropdown_value != "1":
        inDelphi.init_model(celltype=dropdown_value)
    import altair as alt

    results_df = pd.DataFrame()
    results_df_right = pd.DataFrame()
    Carry_Over_fom_Left = ""
    Loop_left_counter = ""
    Predicted_Freq_left = ""
    results_df_final = pd.DataFrame()

    Left = input_box_value
    Left_point = input_box_3_value
    Right = input_box_2_value
    Right_point = input_box_4_value

    for i in range(min_length, max_length, 1):
        logger.info("Scoring left arm length %d/%d", i - min_length + 1, max_length - min_length)
        Left_acceptor = Left
        Left_donor = Left_point[len(Left_point)-i:]+Right

        pred_df, stats = inDelphi.predict(Left_acceptor+Left_donor, len(Left_acceptor))
        pred_df = inDelphi.add_genotype_column(pred_df, stats)
        pred_df = pred_df.dropna(subset=['Genotype'])

        for k, row in pred_df.iterrows():
            genotype = row['Genotype']
            if Left_point+Right in genotype:
                frequency = row['Predicted frequency']
                results_df = results_df.append({'Loop index': i, 'Predicted frequency': frequency}, ignore_index=True)

                Loop_left_counter = i
                Predicted_Freq_left = frequency
                Carry_Over_fom_Left = Left_point[len(Left_point)-i:]
            else:
                results_df = results_df.append({'Loop index': i, 'Predicted frequency': ""}, ignore_index=True)

        for p in range(min_length, max_length, 1):
            Right_donor = Carry_Over_fom_Left + Right_point[:p]
            Primer_to_Order = Right_donor
            Right_acceptor = Right

            pred_df, stats = inDelphi.predict(Right_donor+Right_acceptor, len(Right_donor))
            pred_df = inDelphi.add_genotype_column(pred_df, stats)
            pred_df = pred_df.dropna(subset=['Genotype'])

            for g, row in pred_df.iterrows():
                genotype = row['Genotype']
                if Carry_Over_fom_Left+Right_point in genotype:
                    frequency = row['Predicted frequency']
                    results_df_right = results_df_right.append({'Loop index_right': p, 'Predicted frequency_right': frequency, 'Loop index':Loop_left_counter, 'Predicted frequency':Predicted_Freq_left, "primer_to_order":Primer_to_Order}, ignore_index=True)

    if results_df_right.shape == (0, 0):
        result_editing = "no_solution"
        logger.info("Editing calculation complete — no solution found")
    else:
        results_df_right['Predicted frequency'] = results_df_right['Predicted frequency'].replace('', 0)
        results_df_right['Joint probability'] = (results_df_right['Predicted frequency']/100) * (results_df_right['Predicted frequency_right']/100) * 100
        results_df_right = results_df_right[results_df_right['Joint probability'] != 0]
        result_editing = results_df_right
        logger.info("Editing calculation complete — %d results passed to frontend", len(results_df_right))

    return result_editing