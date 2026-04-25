import logging
import warnings
warnings.filterwarnings('ignore')
warnings.filterwarnings("ignore", category=DeprecationWarning)
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
from datetime import datetime

logger = logging.getLogger('pythia.editing')

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

def reload_inDelphi_if_needed(dropdown_value):
    global last_celltype, inDelphi
    if dropdown_value != last_celltype:
        inDelphi = importlib.reload(inDelphi)
        inDelphi.init_model(celltype=dropdown_value)
        last_celltype = dropdown_value

def process_pythia_editing_withgRNAfinder(dropdown_value, geneticsequence, geneticsequencemut, min_length, max_length, max_distance):
    logger.info("Editing (gRNA finder) started — cell type: %s", dropdown_value)

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

    # Reload and reinitialize inDelphi module if dropdown_value changes
    reload_inDelphi_if_needed(dropdown_value)
   
    #inputs

    seq = geneticsequence


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

    df_all_unique = pd.concat([output_plus, output_min], ignore_index=True)
    df_all_unique['CRISPR_Scan_Score'] = df_all_unique['CRISPR_Scan_Score'].astype(str).str.strip('[]')
    logger.info("Found %d candidate gRNAs in target sequence", len(df_all_unique))

    def reverse_complement(seq):
        complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return ''.join(complement[base] for base in reversed(seq))

    rev_comp_sequence = reverse_complement(seq)

    geneticsequencemut_rev = reverse_complement(geneticsequencemut)

    contexts = []

    for index, row in df_all_unique.iterrows():
        
        if row['strand'] == "plus":
                
            context = seq[row['location'] - 40:row['location'] + 40]
            
        else:
            
            pos_rev = len(seq) - row['location'] #takethis
                                            
            context = rev_comp_sequence[pos_rev - 40:pos_rev + 40]
                    
        contexts.append(context)
        
    df_all_unique['contexts'] = contexts
    df_all_unique = df_all_unique[df_all_unique['contexts'].str.len() == 80]


    contextsmut = []

    seqmut = geneticsequencemut

    #find the location of the point mutations, left and right

    def find_mismatches(seq, seqmut):
        # Initialize indices for the leftmost and rightmost mismatches
        left_mismatch = None
        right_mismatch = None

        # Loop over the length of the shorter DNA sequence to avoid index errors
        for i in range(min(len(seq), len(seqmut))):
            # Check if characters at the current position are different
            if seq[i] != seqmut[i]:
                # If no left mismatch has been recorded, set this as the first one
                if left_mismatch is None:
                    left_mismatch = i
                # Always update the right mismatch to the current index
                right_mismatch = i

        # Ensure to return the results
        return left_mismatch, right_mismatch

    # Example usage:
    left, right = find_mismatches(seq, seqmut)

    len_seqmut = len(seq)
    mismatch_central = (min(df_all_unique['location']) + max(df_all_unique['location'])) // 2  # Example calculation

    # Function to calculate the distance based on the strand
    def calculate_distance(row):
        if row['strand'] == 'plus':
            return abs(row['location'] - mismatch_central)
        else:
            return abs(len_seqmut - row['location'] - mismatch_central)

    # Apply the function to calculate distances
    df_all_unique['distance_to_central'] = df_all_unique.apply(calculate_distance, axis=1)

    # Filter the DataFrame based on the distance criteria
    df_filtered = df_all_unique[df_all_unique['distance_to_central'] <= max_distance]

    # Assign the filtered DataFrame back to df_all_unique
    df_all_unique = df_filtered
    logger.info("%d gRNAs within range of mutation site — starting per-gRNA scoring", len(df_all_unique))

    #getgeneticsequence

    for index, row in df_all_unique.iterrows():
        
        if row['strand'] == "plus":
                
            context = seqmut[row['location'] - 40:row['location'] + 40]
            
        else:
            
            pos_rev = len(seqmut) - row['location']
        
            rev_comp_sequence_mut = reverse_complement(seqmut)
                                            
            context = rev_comp_sequence_mut[pos_rev - 40:pos_rev + 40]
                    
        contextsmut.append(context)
        
    df_all_unique['contextsmut'] = contextsmut
    df_all_unique = df_all_unique[df_all_unique['contextsmut'].str.len() == 80]
    
    #df_all_unique.to_csv("test2.csv")

#!!!!!!!!!!! here simply change the inputs instead of doing input box values, just needs to be a slice of the input string, at the location of the found gRNA


    total_grnas = len(df_all_unique)
    for grna_idx, (index, row) in enumerate(df_all_unique.iterrows(), 1):

        gRNA_seq = row['gRNA_seq']  # Store the gRNA_seq from df_all_unique
        gRNA_score = row['CRISPR_Scan_Score']
        logger.info("Processing gRNA %s (%d/%d)", gRNA_seq, grna_idx, total_grnas)

        Left = row['contexts'][:40]
        Right = row['contexts'][40:]

        Left_point = row['contextsmut'][:40]

        Right_point = row['contextsmut'][40:]

        for i in range(min_length, max_length, 1):
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
                        results_df_right = results_df_right.append({'Loop index_right': p, 'Predicted frequency_right': frequency, 'Loop index':Loop_left_counter, 'Predicted frequency':Predicted_Freq_left, "primer_to_order":Primer_to_Order, "gRNA": gRNA_seq, 'CRISPRSCan Score':gRNA_score}, ignore_index=True)

    for index, row in results_df_right.iterrows():
        if row['primer_to_order'] not in geneticsequencemut and row['primer_to_order'] not in geneticsequencemut_rev:
            results_df_right.at[index, 'Joint probability'] = 0
            results_df_right.at[index, 'Predicted frequency_right'] = 0
            results_df_right.at[index, 'Predicted frequency'] = 0

    if results_df_right.shape == (0, 0):
        result_editing = "no_solution"
        logger.info("Editing (gRNA finder) complete — no solution found")
    else:
        results_df_right['Predicted frequency'] = results_df_right['Predicted frequency'].replace('', 0)
        results_df_right['Joint probability'] = (results_df_right['Predicted frequency']/100) * (results_df_right['Predicted frequency_right']/100) * 100
        results_df_right = results_df_right[results_df_right['Joint probability'] != 0]
        result_editing = results_df_right
        logger.info("Editing (gRNA finder) complete — %d results passed to frontend", len(results_df_right))

    return result_editing