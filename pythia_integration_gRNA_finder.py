#!/usr/bin/env python
# coding: utf-8

# In[5]:


import logging
import warnings

logger = logging.getLogger('pythia.integration')

_MODE_LABELS = {
    'integration': 'INTEGRATION',
    'first_exon':  'CUSTOM TAGGING',
}


def _mode_label(mode):
    return _MODE_LABELS.get(mode, 'TAGGING')

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# You can also use this to suppress all warnings
warnings.filterwarnings("ignore")
# If the above doesn't work, you can try suppressing specific modules
warnings.filterwarnings("ignore", message="distutils Version classes are deprecated")

import sys
import warnings
from Bio import SeqIO
from Bio.Seq import Seq
from Bio import SeqUtils
import pyfastx
import pandas as pd
import importlib

#initialize final storage

df_all = pd.DataFrame(columns=['gene','gRNA_seq','CRISPR_Scan_Score','InDelphi_frameshift'], dtype=object)

#CRISPRScan database

paramsCRISPRscan = [
# converted excel table of logistic regression weights with 1-based positions
('AA',19,-0.097377097),
('TT',18,-0.094424075),('TT',13,-0.08618771),('CT',26,-0.084264893),('GC',25,-0.073453609),
('T',21,-0.068730497),('TG',23,-0.066388075),('AG',23,-0.054338456),('G',30,-0.046315914),
('A',4,-0.042153521),('AG',34,-0.041935908),('GA',34,-0.037797707),('A',18,-0.033820432),
('C',25,-0.031648353),('C',31,-0.030715556),('G',1,-0.029693709),('C',16,-0.021638609),
('A',14,-0.018487229),('A',11,-0.018287292),('T',34,-0.017647692),('AA',10,-0.016905415),
('A',19,-0.015576499),('G',34,-0.014167123),('C',30,-0.013182733),('GA',31,-0.01227989),
('T',24,-0.011996172),('A',15,-0.010595296),('G',4,-0.005448869),('GG',9,-0.00157799),
('T',23,-0.001422243),('C',15,-0.000477727),('C',26,-0.000368973),('T',27,-0.000280845),
('A',31,0.00158975),('GT',18,0.002391744),('C',9,0.002449224),('GA',20,0.009740799),
('A',25,0.010506405),('A',12,0.011633235),('A',32,0.012435231),('T',22,0.013224035),
('C',20,0.015089514),('G',17,0.01549378),('G',18,0.016457816),('T',30,0.017263162),
('A',13,0.017628924),('G',19,0.017916844),('A',27,0.019126815),('G',11,0.020929039),
('TG',3,0.022949996),('GC',3,0.024681785),('G',14,0.025116714),('GG',10,0.026802158),
('G',12,0.027591138),('G',32,0.03071249),('A',22,0.031930909),('G',20,0.033957008),
('C',21,0.034262921),('TT',17,0.03492881),('T',13,0.035445171),('G',26,0.036146649),
('A',24,0.037466478),('C',22,0.03763162),('G',16,0.037970942),('GG',12,0.041883009),
('TG',18,0.045908991),('TG',31,0.048136812),('A',35,0.048596259),('G',15,0.051129717),
('C',24,0.052972314),('TG',15,0.053372822),('GT',11,0.053678436),('GC',9,0.054171402),
('CA',30,0.057759851),('GT',24,0.060952114),('G',13,0.061360905),('CA',24,0.06221937),
('AG',10,0.063717093),('G',10,0.067739182),('C',13,0.069495944),('GT',31,0.07342535),
('GG',13,0.074355848),('C',27,0.079933922),('G',27,0.085151052),('CC',21,0.088919601),
('CC',23,0.095072286),('G',22,0.10114438),('G',24,0.105488325),('GT',23,0.106718563),
('GG',25,0.111559441),('G',9,0.114600681)]

def calcCrisprScanScores(seqs):
    """ input is a 35bp long sequence: 6bp 5', 20bp guide, 3 bp PAM and 6bp 3'
    >>> calcCrisprScanScores(["TCCTCTGGTGGCGCTGCTGGATGGACGGGACTGTA"])
    [77]
    >>> calcCrisprScanScores(["TCCTCTNGTGGCGCTGCTGGATGGACGGGACTGTA"])
    [77]
    """
    scores = []
    for seq in seqs:
        assert(len(seq)==35)
        intercept = 0.183930943629
        score = intercept
        for modelSeq, pos, weight in paramsCRISPRscan:
            subSeq = seq[pos-1:pos+len(modelSeq)-1]
            if subSeq==modelSeq:
                score += weight
        scores.append(int(100*score))
    return scores

# Define a global variable to track the last used dropdown_value
last_celltype = None

# Append the module path
sys.path.insert(0, '/home/lienkamplab/Pythia/Indelphi_installation/inDelphi-model-master')

# Import the module initially
import inDelphi

def reload_inDelphi_if_needed(dropdown_value):
    global last_celltype, inDelphi
    if dropdown_value != last_celltype:
        inDelphi = importlib.reload(inDelphi)
        inDelphi.init_model(celltype=dropdown_value)
        last_celltype = dropdown_value

def process_pythia_integration_with_gRNA(input_box_4_value, input_box_3_value, dropdown_value, integration_dropdown_value, input_box_context_value):
    label = _mode_label(integration_dropdown_value)
    logger.info("[%s] Calculation started — cell type: %s", label, dropdown_value)

    if integration_dropdown_value == 'integration':

        # Reload and reinitialize inDelphi module if dropdown_value changes
        reload_inDelphi_if_needed(dropdown_value)
    
        #inputs

        seq = input_box_4_value

        Casette = input_box_3_value


        #initialize loop counter

        fastacounter = 1
        writecounter = 1

        #initialize loop

        output_list2 = []
        output_list1 = []

        output_min = []
        output_plus = []
        right_list = []
        left_list = []
        gRNA_Start = []
        gRNA_target_sequence = []
        gRNA_CRISPRScanScore = []
        Strand = []
        frameshiftfreq = []
        filler = [[0,0,0,0,0,0, "+", 0,0,0]]
        output_indelphi_df = []
        output_indelphi_df = pd.DataFrame(filler, columns=["left_cut", "right_cut", "Length", "Genotype position", "Predicted frequency", "Category", "Inserted Bases", "found_grna", "strand", "Frameshift frequency"], dtype=object)      

        # Initialize mutationplace as None to handle the case where there may be no mutations
        mutationplace = None


        input_fasta = seq

        allowed_chars = {'A', 'C', 'T', 'G'}

        if all(char in allowed_chars for char in input_fasta.upper()):

            query = Seq("NNNNNNNGG") #insert query here ie NNNNNNNGG 
            #assert(seq_len(query==9)) need to fix this assertion

            #print("Input_fasta sequence length is ", len(input_fasta),"\n")

            #Homebrew - forward strand

            found_locs = SeqUtils.nt_search(input_fasta, query)
            found_locs_clean=(found_locs[1:])
            found_locs_clean2 = [int(x) for x in found_locs_clean]

            CRISPRScan_Score_list = []
            gRNA_list = []
            FrameFreq_list = []
            MHFreq_list = []
            percentage_list = []
            location_list = []

            for found_grna in found_locs_clean2:

                if found_grna < 20:
                    #print("Found gRNA to close to left borders of input sequence to provide CRISPRScan analysis")
                    pass
                elif found_grna > len(input_fasta)-15:
                    #print("Found gRNA to close to right borders of input sequence to provide CRISPRScan analysis")
                    pass
                else:
                    input_crisprscan = (input_fasta[(found_grna-20):(found_grna+15)])
                    gRNA = (input_fasta[(found_grna-14):(found_grna+6)])
                    #print( "gRNA target sequence:", gRNA, "\nCRISPRScan input:", input_crisprscan,)

                    #gRNA

                    gRNA_list.append(gRNA)

                    #crisprscan

                    CRISPRScan_score = calcCrisprScanScores([input_crisprscan])
                    CRISPRScan_Score_list.append(CRISPRScan_score) 

                    #indelphi


                    pred_df, stats = inDelphi.predict(input_fasta, (found_grna+3))
                    FrameFreq = stats['Frameshift frequency']
                    FrameFreq_list.append(FrameFreq)
                    MHFreq = stats['MH del frequency']
                    MHFreq_list.append(MHFreq)     
                    location_list.append(found_grna+3)

                    output_plus = pd.DataFrame(
                    {'gRNA_seq': gRNA_list,
                    'CRISPR_Scan_Score': CRISPRScan_Score_list, 'MH del frequency': MHFreq_list,
                    'InDelphi_frameshift': FrameFreq_list, 'location': location_list,
                    }, dtype='object')

                    output_plus['strand'] = 'plus'


            #reverse

            input_fasta_seq = Seq(input_fasta)
            input_fasta_complement = input_fasta_seq.reverse_complement()
            input_fasta_complement = str(input_fasta_complement)
            found_locs_complement = SeqUtils.nt_search(input_fasta_complement, query)
            found_locs_clean_complement=(found_locs_complement[1:])
            found_locs_clean2_complement = [int(x) for x in found_locs_clean_complement]

            CRISPRScan_Score_list = []
            gRNA_list = []
            FrameFreq_list = []
            MHFreq_list = []
            percentage_list = []
            location_list = []


            for found_grna in found_locs_clean2_complement:

                if found_grna < 20:
                    #print("Found gRNA to close to left borders of input sequence to provide CRISPRScan analysis")
                    pass
                elif found_grna > len(input_fasta)-15:
                    #print("Found gRNA to close to right borders of input sequence to provide CRISPRScan analysis")
                    pass
                else:
                    input_crisprscan = (input_fasta_complement[(found_grna-20):(found_grna+15)])
                    gRNA = (input_fasta_complement[(found_grna-14):(found_grna+6)])
                    #print( "gRNA target sequence:", gRNA, "\nCRISPRScan input:", input_crisprscan,)


                    #gRNA

                    gRNA_list.append(gRNA)

                    #crisprscan

                    CRISPRScan_score = calcCrisprScanScores([input_crisprscan])
                    CRISPRScan_Score_list.append(CRISPRScan_score) 

                        #indelphi

                    pred_df, stats = inDelphi.predict(input_fasta_complement, (found_grna+3))
                    FrameFreq = stats['Frameshift frequency']
                    FrameFreq_list.append(FrameFreq)
                    MHFreq = stats['MH del frequency']
                    MHFreq_list.append(MHFreq)
                    location_list.append((len(input_fasta) - found_grna)-3)


                    output_min = pd.DataFrame(
                    {'gRNA_seq': gRNA_list,
                    'CRISPR_Scan_Score': CRISPRScan_Score_list, 'MH del frequency': MHFreq_list,
                    'InDelphi_frameshift': FrameFreq_list, 'location': location_list,
                    }, dtype='object')

                    output_min['strand'] = 'min'

        else:
            fastacounter = fastacounter + 1
            pass


        # Ensure that both output_plus and output_min are DataFrames and not empty
        if isinstance(output_plus, pd.DataFrame) and not output_plus.empty:
            if isinstance(output_min, pd.DataFrame) and not output_min.empty:
                df_all_unique = pd.concat([output_plus, output_min], ignore_index=True)
            else:
                df_all_unique = output_plus.reset_index(drop=True)
        elif isinstance(output_min, pd.DataFrame) and not output_min.empty:
            df_all_unique = output_min.reset_index(drop=True)
        else:
            df_all_unique = pd.DataFrame()  # If both are empty, create an empty DataFrame

        if df_all_unique.empty:
            raise ValueError("No valid gRNAs found in the target sequence. The sequence may be too short or lack suitable PAM sites (NGG).")

        df_all_unique['CRISPR_Scan_Score'] = df_all_unique['CRISPR_Scan_Score'].astype(str).str.strip('[]')

        def reverse_complement(seq):
            complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
            return ''.join(complement[base] for base in reversed(seq))

        rev_comp_sequence = reverse_complement(seq)
        rev_comp_sequence_context = reverse_complement(input_box_context_value)

        contexts = []

        def get_context(sequence, gRNA_seq, offset_left=23, offset_right=37):
            # Find the start index of the gRNA sequence in the given context
            start_index = sequence.find(gRNA_seq)
            if start_index == -1:
                return None  # gRNA sequence not found

            # Calculate start and end indices for the context extraction
            start = start_index - offset_left
            end = start_index + len(gRNA_seq) + offset_right

            # Check if calculated indices are within the bounds of the sequence
            if start < 0 or end > len(sequence):
                return None  # Not enough room to extract context

            # Return the extracted context
            return sequence[start:end]

        contexts = []
        for index, row in df_all_unique.iterrows():
            if row['strand'] == "plus":
                context = get_context(input_box_context_value, row['gRNA_seq'])
            else:
                # Calculate the reverse complement of the input context

                context = get_context(rev_comp_sequence_context, row['gRNA_seq'])

            # Append context if it is valid (i.e., has the correct length)
            if context and len(context) == 80:
                contexts.append(context)
            else:
                contexts.append(None)  # Append None if no valid context is found

        df_all_unique['contexts'] = contexts
        df_all_unique = df_all_unique.dropna(subset=['contexts'])  # Remove rows without valid context

        df_all_unique['contexts'] = contexts
        df_all_unique = df_all_unique[df_all_unique['contexts'].str.len() == 80]

        if df_all_unique.empty:
            raise ValueError("No gRNAs with valid genomic context could be found. Try providing a longer context sequence.")

        final_results = pd.DataFrame()
        total_grnas = len(df_all_unique)
        logger.info("[%s] Found %d gRNAs with valid context — starting scoring", label, total_grnas)

        for grna_idx, (index, row) in enumerate(df_all_unique.iterrows(), 1):

            gRNA_name = row['gRNA_seq']
            loci = row['location']
            stra = row['strand']
            score = row['CRISPR_Scan_Score']
            contextsxx = row['contexts']
            logger.info("[%s] Processing gRNA %s (%d/%d)", label, gRNA_name, grna_idx, total_grnas)

            results_df = pd.DataFrame()
            Left = row['contexts'][:40]
            Right = row['contexts'][40:]

            # Run code for left boundary
            for i in range(3, 9):
                for j in range(3, 6):
                    Left_donor = Left[len(Left) - i:] * j + Casette
                    ology = Left[len(Left) - i:]
                    
                    pred_df, stats = inDelphi.predict(Left + Left_donor, (len(Left)))
                    pred_df = inDelphi.add_genotype_column(pred_df, stats)
                    pred_df = pred_df.dropna(subset=['Genotype'])
                    
                    for k, row in pred_df.iterrows():
                        genotype = row['Genotype']
                        for x in range(6):
                            repair_string = Left + ology * x + Casette
                            if repair_string in genotype:
                                frequency = row['Predicted frequency']
                                results_df = results_df.append({"side": "left", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)
            
            # Run code for right boundary
            for i in range(3, 9):
                for j in range(3, 6):
                    Right_donor = Casette + (Right[:i] * j)
                    ology = Right[:i]
                    
                    pred_df, stats = inDelphi.predict(Right_donor + Right, (len(Right_donor)))
                    pred_df = inDelphi.add_genotype_column(pred_df, stats)
                    pred_df = pred_df.dropna(subset=['Genotype'])
                    
                    for k, row in pred_df.iterrows():
                        genotype = row['Genotype']
                        for x in range(6):
                            repair_string = Casette + ology * x + Right
                            if repair_string in genotype:
                                frequency = row['Predicted frequency']
                                results_df = results_df.append({"side": "right", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)
            
            # Aggregate and summarize results
            aggregated_df = results_df.groupby(['Amount of trimologies', 'Homol_length', "side"])['Predicted frequency'].sum().reset_index()
            aggregated_df["gRNA"] = gRNA_name
            aggregated_df["CRISPRScan score"] = score
            aggregated_df["strand"] = stra
            aggregated_df["location"] = loci
            aggregated_df["context"] = contextsxx
            
            final_results = pd.concat([final_results, aggregated_df], ignore_index=True)
    
    elif integration_dropdown_value == 'first_exon':

        # Reload and reinitialize inDelphi module if dropdown_value changes
        reload_inDelphi_if_needed(dropdown_value)

        #inputs

        seq = input_box_4_value

        Casette = input_box_3_value

        # Helper function for dynamic cassette in 5' tagging
        def get_dynamic_cassette_first_exon(first_exon_seq, cleavage_index):
            """
            For 5' tagging: extract the sequence from ATG (start) up to the cleavage point.
            This preserves the N-terminal portion of the endogenous protein.
            """
            # The first_exon should start with ATG
            if not first_exon_seq.upper().startswith('ATG'):
                logger.warning("First exon doesn't start with ATG")
                return ""

            if cleavage_index < 0 or cleavage_index > len(first_exon_seq):
                logger.warning("Cleavage index %d out of bounds for first_exon_seq (len=%d)", cleavage_index, len(first_exon_seq))
                return ""

            # Return sequence from ATG (position 0) up to (but not including) the cleavage point
            # Keep the ATG to preserve the endogenous Methionine
            return first_exon_seq[0:cleavage_index]


        #initialize loop counter

        fastacounter = 1
        writecounter = 1

        #initialize loop

        output_list2 = []
        output_list1 = []

        output_min = []
        output_plus = []
        right_list = []
        left_list = []
        gRNA_Start = []
        gRNA_target_sequence = []
        gRNA_CRISPRScanScore = []
        Strand = []
        frameshiftfreq = []
        filler = [[0,0,0,0,0,0, "+", 0,0,0]]
        output_indelphi_df = []
        output_indelphi_df = pd.DataFrame(filler, columns=["left_cut", "right_cut", "Length", "Genotype position", "Predicted frequency", "Category", "Inserted Bases", "found_grna", "strand", "Frameshift frequency"], dtype=object)      

        # Initialize mutationplace as None to handle the case where there may be no mutations
        mutationplace = None


        input_fasta = seq

        allowed_chars = {'A', 'C', 'T', 'G'}

        if all(char in allowed_chars for char in input_fasta.upper()):

            query = Seq("NNNNNNNGG") #insert query here ie NNNNNNNGG 
            #assert(seq_len(query==9)) need to fix this assertion

            #print("Input_fasta sequence length is ", len(input_fasta),"\n")

            #Homebrew - forward strand

            found_locs = SeqUtils.nt_search(input_fasta, query)
            found_locs_clean=(found_locs[1:])
            found_locs_clean2 = [int(x) for x in found_locs_clean]

            CRISPRScan_Score_list = []
            gRNA_list = []
            FrameFreq_list = []
            MHFreq_list = []
            percentage_list = []
            location_list = []

            for found_grna in found_locs_clean2:

                if found_grna < 20:
                    #print("Found gRNA to close to left borders of input sequence to provide CRISPRScan analysis")
                    pass
                elif found_grna > len(input_fasta)-15:
                    #print("Found gRNA to close to right borders of input sequence to provide CRISPRScan analysis")
                    pass
                else:
                    input_crisprscan = (input_fasta[(found_grna-20):(found_grna+15)])
                    gRNA = (input_fasta[(found_grna-14):(found_grna+6)])
                    #print( "gRNA target sequence:", gRNA, "\nCRISPRScan input:", input_crisprscan,)

                    #gRNA

                    gRNA_list.append(gRNA)

                    #crisprscan

                    CRISPRScan_score = calcCrisprScanScores([input_crisprscan])
                    CRISPRScan_Score_list.append(CRISPRScan_score) 

                    #indelphi


                    pred_df, stats = inDelphi.predict(input_fasta, (found_grna+3))
                    FrameFreq = stats['Frameshift frequency']
                    FrameFreq_list.append(FrameFreq)
                    MHFreq = stats['MH del frequency']
                    MHFreq_list.append(MHFreq)     
                    location_list.append(found_grna+3)

                    output_plus = pd.DataFrame(
                    {'gRNA_seq': gRNA_list,
                    'CRISPR_Scan_Score': CRISPRScan_Score_list, 'MH del frequency': MHFreq_list,
                    'InDelphi_frameshift': FrameFreq_list, 'location': location_list,
                    }, dtype='object')

                    output_plus['strand'] = 'plus'


            #reverse

            input_fasta_seq = Seq(input_fasta)
            input_fasta_complement = input_fasta_seq.reverse_complement()
            input_fasta_complement = str(input_fasta_complement)
            found_locs_complement = SeqUtils.nt_search(input_fasta_complement, query)
            found_locs_clean_complement=(found_locs_complement[1:])
            found_locs_clean2_complement = [int(x) for x in found_locs_clean_complement]

            CRISPRScan_Score_list = []
            gRNA_list = []
            FrameFreq_list = []
            MHFreq_list = []
            percentage_list = []
            location_list = []


            for found_grna in found_locs_clean2_complement:

                if found_grna < 20:
                    #print("Found gRNA to close to left borders of input sequence to provide CRISPRScan analysis")
                    pass
                elif found_grna > len(input_fasta)-15:
                    #print("Found gRNA to close to right borders of input sequence to provide CRISPRScan analysis")
                    pass
                else:
                    input_crisprscan = (input_fasta_complement[(found_grna-20):(found_grna+15)])
                    gRNA = (input_fasta_complement[(found_grna-14):(found_grna+6)])
                    #print( "gRNA target sequence:", gRNA, "\nCRISPRScan input:", input_crisprscan,)


                    #gRNA

                    gRNA_list.append(gRNA)

                    #crisprscan

                    CRISPRScan_score = calcCrisprScanScores([input_crisprscan])
                    CRISPRScan_Score_list.append(CRISPRScan_score) 

                        #indelphi

                    pred_df, stats = inDelphi.predict(input_fasta_complement, (found_grna+3))
                    FrameFreq = stats['Frameshift frequency']
                    FrameFreq_list.append(FrameFreq)
                    MHFreq = stats['MH del frequency']
                    MHFreq_list.append(MHFreq)
                    location_list.append((len(input_fasta) - found_grna)-3)


                    output_min = pd.DataFrame(
                    {'gRNA_seq': gRNA_list,
                    'CRISPR_Scan_Score': CRISPRScan_Score_list, 'MH del frequency': MHFreq_list,
                    'InDelphi_frameshift': FrameFreq_list, 'location': location_list,
                    }, dtype='object')

                    output_min['strand'] = 'min'

        else:
            fastacounter = fastacounter + 1
            pass
                
                
# Ensure that both output_plus and output_min are DataFrames and not empty
        if isinstance(output_plus, pd.DataFrame) and not output_plus.empty:
            if isinstance(output_min, pd.DataFrame) and not output_min.empty:
                df_all_unique = pd.concat([output_plus, output_min], ignore_index=True)
            else:
                df_all_unique = output_plus.reset_index(drop=True)
        elif isinstance(output_min, pd.DataFrame) and not output_min.empty:
            df_all_unique = output_min.reset_index(drop=True)
        else:
            df_all_unique = pd.DataFrame()  # If both are empty, create an empty DataFrame

        if df_all_unique.empty:
            raise ValueError("No valid gRNAs found in the target sequence. The sequence may be too short or lack suitable PAM sites (NGG).")

        df_all_unique['CRISPR_Scan_Score'] = df_all_unique['CRISPR_Scan_Score'].astype(str).str.strip('[]')

        def reverse_complement(seq):
            complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
            return ''.join(complement[base] for base in reversed(seq))

        rev_comp_sequence = reverse_complement(seq)
        rev_comp_sequence_context = reverse_complement(input_box_context_value)

        contexts = []

        def get_context(sequence, gRNA_seq, offset_left=23, offset_right=37):
            # Find the start index of the gRNA sequence in the given context
            start_index = sequence.find(gRNA_seq)
            if start_index == -1:
                return None  # gRNA sequence not found

            # Calculate start and end indices for the context extraction
            start = start_index - offset_left
            end = start_index + len(gRNA_seq) + offset_right

            # Check if calculated indices are within the bounds of the sequence
            if start < 0 or end > len(sequence):
                return None  # Not enough room to extract context

            # Return the extracted context
            return sequence[start:end]

        contexts = []
        for index, row in df_all_unique.iterrows():
            if row['strand'] == "plus":
                context = get_context(input_box_context_value, row['gRNA_seq'])
            else:
                # Calculate the reverse complement of the input context

                context = get_context(rev_comp_sequence_context, row['gRNA_seq'])

            # Append context if it is valid (i.e., has the correct length)
            if context and len(context) == 80:
                contexts.append(context)
            else:
                contexts.append(None)  # Append None if no valid context is found

        df_all_unique['contexts'] = contexts
        df_all_unique = df_all_unique.dropna(subset=['contexts'])  # Remove rows without valid context

        df_all_unique['contexts'] = contexts
        df_all_unique = df_all_unique[df_all_unique['contexts'].str.len() == 80]

        if df_all_unique.empty:
            raise ValueError("No gRNAs with valid genomic context could be found. Try providing a longer context sequence.")

        final_results = pd.DataFrame()
        total_grnas = len(df_all_unique)
        logger.info("[%s] Found %d gRNAs with valid context — starting scoring", label, total_grnas)

        for grna_idx, (index, row) in enumerate(df_all_unique.iterrows(), 1):

            gRNA_name = row['gRNA_seq']
            loci = row['location']
            stra = row['strand']
            score = row['CRISPR_Scan_Score']
            contextsxx = row['contexts']
            logger.info("[%s] Processing gRNA %s (%d/%d)", label, gRNA_name, grna_idx, total_grnas)

            results_df = pd.DataFrame()
            Left = row['contexts'][:40]
            Right = row['contexts'][40:]

            # Get dynamic cassette: portion of first exon from ATG to cut site
            dynamic_cassette_first_exon = get_dynamic_cassette_first_exon(seq, loci)


            if stra == 'plus':
                # For plus strand: Tag (with ATG) + first exon portion (ATG to cut) creates the donor component
                # Run code for left boundary
                for i in range(3, 9):
                    for j in range(3, 6):
                        Left_donor = Left[len(Left) - i:] * j + Casette + dynamic_cassette_first_exon
                        ology = Left[len(Left) - i:]

                        pred_df, stats = inDelphi.predict(Left + Left_donor, len(Left))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])

                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = Left + ology * x + Casette + dynamic_cassette_first_exon
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "left", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)

                # Run code for right boundary
                for i in [3]:
                    for j in range(3, 6):
                        Right_donor = Casette + dynamic_cassette_first_exon + (Right[:i] * j)
                        ology = Right[:i]

                        pred_df, stats = inDelphi.predict(Right_donor + Right, len(Right_donor))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])

                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = Casette + dynamic_cassette_first_exon + ology * x + Right
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "right", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)

            elif stra == 'min':
                # For minus strand: need to reverse complement the dynamic cassette
                dynamic_cassette_first_exon_revcomp = reverse_complement(dynamic_cassette_first_exon)

                # Run code for left boundary
                for i in [3]:
                    for j in range(3, 6):
                        Left_donor = Left[len(Left) - i:] * j + dynamic_cassette_first_exon_revcomp + Casette
                        ology = Left[len(Left) - i:]

                        pred_df, stats = inDelphi.predict(Left + Left_donor, len(Left))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])

                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = Left + ology * x + dynamic_cassette_first_exon_revcomp + Casette
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "left", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)

                # Run code for right boundary
                for i in range(3, 9):
                    for j in range(3, 6):
                        Right_donor = dynamic_cassette_first_exon_revcomp + Casette + (Right[:i] * j)
                        ology = Right[:i]

                        pred_df, stats = inDelphi.predict(Right_donor + Right, len(Right_donor))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])

                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = dynamic_cassette_first_exon_revcomp + Casette + ology * x + Right
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "right", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)

                        
            # Aggregate and summarize results
            aggregated_df = results_df.groupby(['Amount of trimologies', 'Homol_length', "side"])['Predicted frequency'].sum().reset_index()
            aggregated_df["gRNA"] = gRNA_name
            aggregated_df["CRISPRScan score"] = score
            aggregated_df["strand"] = stra
            aggregated_df["location"] = loci
            aggregated_df["context"] = contextsxx
            aggregated_df["dynamic_cassette"] = dynamic_cassette_first_exon

            final_results = pd.concat([final_results, aggregated_df], ignore_index=True)

      #LAST EXON TAGGING
    else:
        # Reload and reinitialize inDelphi module if dropdown_value changes
        reload_inDelphi_if_needed(dropdown_value)

        #inputs

        seq = input_box_4_value

        Casette = input_box_3_value

        # Helper function for dynamic cassette in 3' tagging
        def get_dynamic_cassette_last_exon(last_exon_seq, cleavage_index):
            """
            For 3' tagging: extract sequence from cleavage point to end, removing stop codon.
            This preserves the C-terminal portion of the endogenous protein.
            """
            # Remove stop codon if present
            if last_exon_seq[-3:].upper() in ['TAA', 'TAG', 'TGA']:
                trimmed_seq = last_exon_seq[:-3]
            else:
                trimmed_seq = last_exon_seq

            if cleavage_index < 0 or cleavage_index > len(trimmed_seq):
                logger.warning("Cleavage index %d out of bounds for last_exon_seq (len=%d)", cleavage_index, len(trimmed_seq))
                return ""

            # Return from cleavage point to end (without stop codon)
            return trimmed_seq[cleavage_index:]


        #initialize loop counter

        fastacounter = 1
        writecounter = 1

        #initialize loop

        output_list2 = []
        output_list1 = []

        output_min = []
        output_plus = []
        right_list = []
        left_list = []
        gRNA_Start = []
        gRNA_target_sequence = []
        gRNA_CRISPRScanScore = []
        Strand = []
        frameshiftfreq = []
        filler = [[0,0,0,0,0,0, "+", 0,0,0]]
        output_indelphi_df = []
        output_indelphi_df = pd.DataFrame(filler, columns=["left_cut", "right_cut", "Length", "Genotype position", "Predicted frequency", "Category", "Inserted Bases", "found_grna", "strand", "Frameshift frequency"], dtype=object)      

        # Initialize mutationplace as None to handle the case where there may be no mutations
        mutationplace = None


        input_fasta = seq

        allowed_chars = {'A', 'C', 'T', 'G'}

        if all(char in allowed_chars for char in input_fasta.upper()):

            query = Seq("NNNNNNNGG") #insert query here ie NNNNNNNGG 
            #assert(seq_len(query==9)) need to fix this assertion

            #print("Input_fasta sequence length is ", len(input_fasta),"\n")

            #Homebrew - forward strand

            found_locs = SeqUtils.nt_search(input_fasta, query)
            found_locs_clean=(found_locs[1:])
            found_locs_clean2 = [int(x) for x in found_locs_clean]

            CRISPRScan_Score_list = []
            gRNA_list = []
            FrameFreq_list = []
            MHFreq_list = []
            percentage_list = []
            location_list = []

            for found_grna in found_locs_clean2:

                if found_grna < 20:
                    #print("Found gRNA to close to left borders of input sequence to provide CRISPRScan analysis")
                    pass
                elif found_grna > len(input_fasta)-15:
                    #print("Found gRNA to close to right borders of input sequence to provide CRISPRScan analysis")
                    pass
                else:
                    input_crisprscan = (input_fasta[(found_grna-20):(found_grna+15)])
                    gRNA = (input_fasta[(found_grna-14):(found_grna+6)])
                    #print( "gRNA target sequence:", gRNA, "\nCRISPRScan input:", input_crisprscan,)

                    #gRNA

                    gRNA_list.append(gRNA)

                    #crisprscan

                    CRISPRScan_score = calcCrisprScanScores([input_crisprscan])
                    CRISPRScan_Score_list.append(CRISPRScan_score) 

                    #indelphi


                    pred_df, stats = inDelphi.predict(input_fasta, (found_grna+3))
                    FrameFreq = stats['Frameshift frequency']
                    FrameFreq_list.append(FrameFreq)
                    MHFreq = stats['MH del frequency']
                    MHFreq_list.append(MHFreq)     
                    location_list.append(found_grna+3)

                    output_plus = pd.DataFrame(
                    {'gRNA_seq': gRNA_list,
                    'CRISPR_Scan_Score': CRISPRScan_Score_list, 'MH del frequency': MHFreq_list,
                    'InDelphi_frameshift': FrameFreq_list, 'location': location_list,
                    }, dtype='object')

                    output_plus['strand'] = 'plus'


            #reverse

            input_fasta_seq = Seq(input_fasta)
            input_fasta_complement = input_fasta_seq.reverse_complement()
            input_fasta_complement = str(input_fasta_complement)
            found_locs_complement = SeqUtils.nt_search(input_fasta_complement, query)
            found_locs_clean_complement=(found_locs_complement[1:])
            found_locs_clean2_complement = [int(x) for x in found_locs_clean_complement]

            CRISPRScan_Score_list = []
            gRNA_list = []
            FrameFreq_list = []
            MHFreq_list = []
            percentage_list = []
            location_list = []


            for found_grna in found_locs_clean2_complement:

                if found_grna < 20:
                    #print("Found gRNA to close to left borders of input sequence to provide CRISPRScan analysis")
                    pass
                elif found_grna > len(input_fasta)-15:
                    #print("Found gRNA to close to right borders of input sequence to provide CRISPRScan analysis")
                    pass
                else:
                    input_crisprscan = (input_fasta_complement[(found_grna-20):(found_grna+15)])
                    gRNA = (input_fasta_complement[(found_grna-14):(found_grna+6)])
                    #print( "gRNA target sequence:", gRNA, "\nCRISPRScan input:", input_crisprscan,)


                    #gRNA

                    gRNA_list.append(gRNA)

                    #crisprscan

                    CRISPRScan_score = calcCrisprScanScores([input_crisprscan])
                    CRISPRScan_Score_list.append(CRISPRScan_score) 

                        #indelphi

                    pred_df, stats = inDelphi.predict(input_fasta_complement, (found_grna+3))
                    FrameFreq = stats['Frameshift frequency']
                    FrameFreq_list.append(FrameFreq)
                    MHFreq = stats['MH del frequency']
                    MHFreq_list.append(MHFreq)
                    location_list.append((len(input_fasta) - found_grna)-3)


                    output_min = pd.DataFrame(
                    {'gRNA_seq': gRNA_list,
                    'CRISPR_Scan_Score': CRISPRScan_Score_list, 'MH del frequency': MHFreq_list,
                    'InDelphi_frameshift': FrameFreq_list, 'location': location_list,
                    }, dtype='object')

                    output_min['strand'] = 'min'

        else:
            fastacounter = fastacounter + 1
            pass
                
                
# Ensure that both output_plus and output_min are DataFrames and not empty
        if isinstance(output_plus, pd.DataFrame) and not output_plus.empty:
            if isinstance(output_min, pd.DataFrame) and not output_min.empty:
                df_all_unique = pd.concat([output_plus, output_min], ignore_index=True)
            else:
                df_all_unique = output_plus.reset_index(drop=True)
        elif isinstance(output_min, pd.DataFrame) and not output_min.empty:
            df_all_unique = output_min.reset_index(drop=True)
        else:
            df_all_unique = pd.DataFrame()  # If both are empty, create an empty DataFrame

        if df_all_unique.empty:
            raise ValueError("No valid gRNAs found in the target sequence. The sequence may be too short or lack suitable PAM sites (NGG).")

        df_all_unique['CRISPR_Scan_Score'] = df_all_unique['CRISPR_Scan_Score'].astype(str).str.strip('[]')

        def reverse_complement(seq):
            complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
            return ''.join(complement[base] for base in reversed(seq))

        rev_comp_sequence = reverse_complement(seq)
        rev_comp_sequence_context = reverse_complement(input_box_context_value)

        contexts = []

        def get_context(sequence, gRNA_seq, offset_left=23, offset_right=37):
            # Find the start index of the gRNA sequence in the given context
            start_index = sequence.find(gRNA_seq)
            if start_index == -1:
                return None  # gRNA sequence not found

            # Calculate start and end indices for the context extraction
            start = start_index - offset_left
            end = start_index + len(gRNA_seq) + offset_right

            # Check if calculated indices are within the bounds of the sequence
            if start < 0 or end > len(sequence):
                return None  # Not enough room to extract context

            # Return the extracted context
            return sequence[start:end]

        contexts = []
        for index, row in df_all_unique.iterrows():
            if row['strand'] == "plus":
                context = get_context(input_box_context_value, row['gRNA_seq'])
            else:
                # Calculate the reverse complement of the input context

                context = get_context(rev_comp_sequence_context, row['gRNA_seq'])

            # Append context if it is valid (i.e., has the correct length)
            if context and len(context) == 80:
                contexts.append(context)
            else:
                contexts.append(None)  # Append None if no valid context is found

        df_all_unique['contexts'] = contexts
        df_all_unique = df_all_unique.dropna(subset=['contexts'])  # Remove rows without valid context

        df_all_unique['contexts'] = contexts
        df_all_unique = df_all_unique[df_all_unique['contexts'].str.len() == 80]

        if df_all_unique.empty:
            raise ValueError("No gRNAs with valid genomic context could be found. Try providing a longer context sequence.")

        final_results = pd.DataFrame()
        total_grnas = len(df_all_unique)
        logger.info("[%s] Found %d gRNAs with valid context — starting scoring", label, total_grnas)

        for grna_idx, (index, row) in enumerate(df_all_unique.iterrows(), 1):

            gRNA_name = row['gRNA_seq']
            loci = row['location']
            stra = row['strand']
            score = row['CRISPR_Scan_Score']
            contextsxx = row['contexts']
            logger.info("[%s] Processing gRNA %s (%d/%d)", label, gRNA_name, grna_idx, total_grnas)

            results_df = pd.DataFrame()
            Left = row['contexts'][:40]
            Right = row['contexts'][40:]

            # Get dynamic cassette: portion of last exon from cut site to end (without stop)
            dynamic_cassette_last_exon = get_dynamic_cassette_last_exon(seq, loci)


            if stra == 'plus':
                # For plus strand: last exon portion (cut to end - no stop) + Tag creates the donor component
                # Run code for left boundary
                for i in [3]:
                    for j in range(3, 6):
                        Left_donor = Left[len(Left) - i:] * j + dynamic_cassette_last_exon + Casette
                        ology = Left[len(Left) - i:]
                        
                        pred_df, stats = inDelphi.predict(Left + Left_donor, len(Left))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])
                        
                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = Left + ology * x + dynamic_cassette_last_exon + Casette
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "left", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)

                # Run code for right boundary
                for i in range(3, 9):
                    for j in range(3, 6):
                        Right_donor = dynamic_cassette_last_exon + Casette + (Right[:i] * j)
                        ology = Right[:i]
                        
                        pred_df, stats = inDelphi.predict(Right_donor + Right, len(Right_donor))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])

                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = dynamic_cassette_last_exon + Casette + ology * x + Right
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "right", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)

            elif stra == 'min':
                # For minus strand: need to reverse complement the dynamic cassette
                dynamic_cassette_last_exon_revcomp = reverse_complement(dynamic_cassette_last_exon)

                # Run code for left boundary
                for i in range(3, 9):
                    for j in range(3, 6):
                        Left_donor = Left[len(Left) - i:] * j + Casette + dynamic_cassette_last_exon_revcomp
                        ology = Left[len(Left) - i:]
                        
                        pred_df, stats = inDelphi.predict(Left + Left_donor, len(Left))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])
                        
                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = Left + ology * x + Casette + dynamic_cassette_last_exon_revcomp
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "left", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)

                # Run code for right boundary
                for i in [3]:
                    for j in range(3, 6):
                        Right_donor = Casette + dynamic_cassette_last_exon_revcomp + (Right[:i] * j)
                        ology = Right[:i]

                        pred_df, stats = inDelphi.predict(Right_donor + Right, len(Right_donor))
                        pred_df = inDelphi.add_genotype_column(pred_df, stats)
                        pred_df = pred_df.dropna(subset=['Genotype'])

                        for k, row in pred_df.iterrows():
                            genotype = row['Genotype']
                            for x in range(6):
                                repair_string = Casette + dynamic_cassette_last_exon_revcomp + ology * x + Right
                                if repair_string in genotype:
                                    frequency = row['Predicted frequency']
                                    results_df = results_df.append({"side": "right", "Homol_length": i, 'Amount of trimologies': j, 'Predicted frequency': frequency, 'Perfect repair at': x}, ignore_index=True)


            # Aggregate and summarize results
            aggregated_df = results_df.groupby(['Amount of trimologies', 'Homol_length', "side"])['Predicted frequency'].sum().reset_index()
            aggregated_df["gRNA"] = gRNA_name
            aggregated_df["CRISPRScan score"] = score
            aggregated_df["strand"] = stra
            aggregated_df["location"] = loci
            aggregated_df["context"] = contextsxx
            aggregated_df["dynamic_cassette"] = dynamic_cassette_last_exon

            final_results = pd.concat([final_results, aggregated_df], ignore_index=True)



    # Find the index of the row with the highest predicted frequency for each gRNA and side
    max_freq_index_left = final_results[final_results['side'] == 'left'].groupby('gRNA')['Predicted frequency'].idxmax()
    max_freq_index_right = final_results[final_results['side'] == 'right'].groupby('gRNA')['Predicted frequency'].idxmax()

    

    # Use the index to extract the rows with the highest predicted frequency for each gRNA and side
    max_freq_left = final_results.loc[max_freq_index_left]
    max_freq_right = final_results.loc[max_freq_index_right]

    # Split the DataFrame into left and right based on the 'side' column
    left_df = final_results[final_results['side'] == 'left'].copy()
    right_df = final_results[final_results['side'] == 'right'].copy()

    # Reset index to ensure a clean merge
    left_df.reset_index(drop=True, inplace=True)
    right_df.reset_index(drop=True, inplace=True)

    # Rename columns to clarify their origin once merged
    left_df.columns = [f'{col}_left' for col in left_df.columns]
    right_df.columns = [f'{col}_right' for col in right_df.columns]

    # Perform the merge on the gRNA column, ensuring combinations are only within the same gRNA
    merged_df = pd.merge(left_df, right_df, left_on='gRNA_left', right_on='gRNA_right')

    # Clean up the merged DataFrame
    # Remove redundant columns from the merged DataFrame
    columns_to_drop = ['gRNA_right', 'CRISPRScan score_right', 'strand_right', 'location_right', 'context_right']
    # Only drop dynamic_cassette_right if it exists (not present in intron mode)
    if 'dynamic_cassette_right' in merged_df.columns:
        columns_to_drop.append('dynamic_cassette_right')
    merged_df.drop(columns=columns_to_drop, inplace=True)

    # Rename the columns back to their original names where necessary
    rename_dict = {
        'gRNA_left': 'gRNA',
        'CRISPRScan score_left': 'CRISPRScan score',
        'strand_left': 'strand',
        'location_left': 'location',
        'context_right': 'right',
    }
    # Only rename dynamic_cassette_left if it exists (not present in intron mode)
    if 'dynamic_cassette_left' in merged_df.columns:
        rename_dict['dynamic_cassette_left'] = 'dynamic_cassette'
    merged_df.rename(columns=rename_dict, inplace=True)

    # Display the resulting DataFrame

    merged_df.drop(columns=['side_left', 'side_right'], inplace=True)
    merged_df['integration_score'] = (merged_df['Predicted frequency_left'] * merged_df['Predicted frequency_right']) / 100

    sorted_df = merged_df

    # Find the index of the maximum integration_score for each gRNA
    max_indices = sorted_df.groupby('gRNA')['integration_score'].idxmax()

    # Select the rows corresponding to the maximum integration_score for each gRNA
    max_scores_df = sorted_df.loc[max_indices]

    # Set the lower threshold as the integration_score of the maximum scores minus 1
    lower_thresholds = max_scores_df[['gRNA', 'integration_score']]
    lower_thresholds['integration_score'] -= 1

    # Merge the lower_thresholds DataFrame with the sorted_df to get the maximum integration_score for each gRNA
    merged_df = pd.merge(sorted_df, lower_thresholds, on='gRNA', suffixes=('', '_max'))

    # Ensure the 'integration_score_max' column is correctly assigned from the merge
    merged_df['integration_score_max'] = merged_df['integration_score_max'].astype(float)

    merged_df['integration_score_float'] = merged_df['integration_score'].astype(float)

    # Filter the DataFrame to keep only the rows between the lower threshold and maximum integration_score for each gRNA
    filtered_df2 = merged_df[merged_df['integration_score_float'] >= merged_df['integration_score_max']]

    # Drop the integration_score_max column
    filtered_df2 = filtered_df2.drop('integration_score_max', axis=1)
    filtered_df2 = filtered_df2.drop('integration_score_float', axis=1)

    # Compute the product of Amount of trimologies_right and Homol_length_right
    product_right = filtered_df2['Amount of trimologies_right'] * filtered_df2['Homol_length_right']

    # Compute the product of Amount of trimologies_left and Homol_length_left
    product_left = filtered_df2['Amount of trimologies_left'] * filtered_df2['Homol_length_left']

    # Add the two products together to get the solution complexity
    filtered_df2['solution_complexity'] = product_right + product_left

    max_score_idx = filtered_df2.groupby('gRNA')['solution_complexity'].idxmin()

    # Retrieve the rows with the maximum 'integration_score' for each gRNA
    max_integration_scores = merged_df.loc[max_score_idx]

    max_integration_scores = max_integration_scores.sort_values(by='integration_score', ascending=False)

    #code block for primer finding

    # Function to adjust primer length to match Tms

    from Bio.SeqUtils import MeltingTemp as mt

    def adjust_primer_length(seq, target_tm, max_diff=1, max_length=30):
        for length in range(18, max_length):
            primer_seq = Seq(seq[:length])
            tm = mt.Tm_NN(primer_seq)
            if abs(tm - target_tm) <= max_diff:
                return primer_seq, tm
        return Seq(seq[:18]), mt.Tm_NN(Seq(seq[:18]))  # Return at least 18 bases if no closer Tm is found

    for index, row in max_integration_scores.iterrows(): 
        
        dna_sequence = Casette
        
        # Initial primer length assumption
        primer_length = 18

        # Left primer (at the start of the sequence)
        left_primer_seq = Seq(dna_sequence[:primer_length])
        left_tm = mt.Tm_NN(left_primer_seq)

        # Right primer (reverse complement of the end of the sequence)
        right_primer_seq = Seq(dna_sequence[-primer_length:]).reverse_complement()
        right_tm = mt.Tm_NN(right_primer_seq)

        # Adjust the length of the primers to balance their Tms
        if left_tm > right_tm:
            right_primer_seq, right_tm = adjust_primer_length(str(Seq(dna_sequence).reverse_complement()), left_tm)
        else:
            left_primer_seq, left_tm = adjust_primer_length(dna_sequence, right_tm)
            
        max_integration_scores.loc[index, "Forward_Primer"] = str(left_primer_seq)
        max_integration_scores.loc[index, "Forward_Primer_Tm"] = left_tm
        max_integration_scores.loc[index, "Reverse_Primer"] = str(right_primer_seq)  
        max_integration_scores.loc[index, "Reverse_Primer_Tm"] = right_tm

    #end code block for primer finding 

    #add repair arms to the primers

    # Function to extract left repair arm based on specified criteria
    def extract_left_repair_arm(row):
        homol_length_left = row["Homol_length_left"]
        context_left = row["context_left"]
        
        middle_position = len(context_left) // 2
        
        start_index = max(0, middle_position - homol_length_left)
        start_index = int(start_index)  # Convert start_index to an integer
        
        left_repair_arm = context_left[start_index:middle_position] * int(row["Amount of trimologies_left"])
        
        return left_repair_arm

    # Apply the function to create the new column
    max_integration_scores["left_repair_arm"] = max_integration_scores.apply(extract_left_repair_arm, axis=1)

    def extract_right_repair_arm(row):
        homol_length_right = row["Homol_length_right"]
        context_left = row["context_left"]
        
        middle_position = len(context_left) // 2
        
        end_index = min(len(context_left), middle_position + homol_length_right)
        end_index = int(end_index)  # Convert end_index to an integer
        
        right_repair_arm = context_left[middle_position:end_index] * int(row["Amount of trimologies_right"])
        
        return right_repair_arm

    # Apply the function to create the new column
    max_integration_scores["right_repair_arm"] = max_integration_scores.apply(extract_right_repair_arm, axis=1)

    max_integration_scores["Revcomp_right_repair_arm"] = max_integration_scores["right_repair_arm"].apply(reverse_complement)

    # Construct the complete Repair_Template for each gRNA
    # The structure depends on whether this is integration (intron), first_exon (5'), or last_exon (3') tagging
    # and the strand orientation

    for index, row in max_integration_scores.iterrows():
        if integration_dropdown_value == 'integration':
            # Intron mode: left_repair_arm + Cassette + right_repair_arm
            # For minus strand, reverse complement the cassette to match gene orientation
            if row["strand"] == "plus":
                repair_template = row["left_repair_arm"] + Casette + row["right_repair_arm"]
            else:
                # Minus strand: reverse complement the cassette
                casette_revcomp = reverse_complement(Casette)
                repair_template = row["left_repair_arm"] + casette_revcomp + row["right_repair_arm"]
        elif integration_dropdown_value == 'first_exon':
            # 5' (N-terminal) tagging: include the 25 bp of upstream 5' UTR (Kozak context)
            # immediately after the left homology arm.
            # input_box_context_value = [50bp upstream 5'UTR] + [first_exon] + [50bp downstream]
            # so bases [25:50] are the last 25 bp of the upstream region, right before the ATG.
            kozak_25bp = input_box_context_value[25:50]

            if row["strand"] == "plus":
                repair_template = row["left_repair_arm"] + kozak_25bp + Casette + row["dynamic_cassette"] + row["right_repair_arm"]
            else:
                # Minus strand: the repair template is in plus-strand coords, so the Kozak
                # (provided in gene/plus orientation) must be reverse complemented.
                dynamic_cassette_revcomp = reverse_complement(row["dynamic_cassette"])
                kozak_25bp_revcomp = reverse_complement(kozak_25bp)
                repair_template = row["left_repair_arm"] + kozak_25bp_revcomp + dynamic_cassette_revcomp + Casette + row["right_repair_arm"]
        else:  # last_exon (3' tagging)
            # 3' tagging: left_repair_arm + dynamic_cassette + Cassette + right_repair_arm
            if row["strand"] == "plus":
                repair_template = row["left_repair_arm"] + row["dynamic_cassette"] + Casette + row["right_repair_arm"]
            else:
                # For minus strand, dynamic_cassette needs to be reverse complemented
                dynamic_cassette_revcomp = reverse_complement(row["dynamic_cassette"])
                repair_template = row["left_repair_arm"] + Casette + dynamic_cassette_revcomp + row["right_repair_arm"]

        max_integration_scores.at[index, "Full repair cassette sequence"] = repair_template

    #generate the final primers

    for index, row in max_integration_scores.iterrows():
        if row["strand"] == "plus":
            max_integration_scores.at[index, "forward_primer_with_overhang"] = row["left_repair_arm"] + row["Forward_Primer"]
            max_integration_scores.at[index, "reverse_primer_with_overhang"] = row["Revcomp_right_repair_arm"] + row["Reverse_Primer"]
        else:
            max_integration_scores.at[index, "forward_primer_with_overhang"] = row["Revcomp_right_repair_arm"] + row["Forward_Primer"]
            max_integration_scores.at[index, "reverse_primer_with_overhang"] = row["left_repair_arm"] + row["Reverse_Primer"]

    logger.info("[%s] Complete — %d gRNAs passed to frontend", label, len(max_integration_scores))
    return max_integration_scores
    


# In[ ]:




