import json
from dash import html


def darken(hex_color, factor=0.65):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"rgb({r},{g},{b})"

def build_arrow(rank_idx, row, pos_pct, is_selected=False, dim_nonselected=True):
    """
    Build a single arrow marker with tooltip.

    dim_nonselected:
        - False: all arrows bright
        - True: only selected bright, others dimmed
    """
    loc = row["location"]
    strand = row["strand"]
    rank = rank_idx + 1

    arrow_char = "▼" if strand == "plus" else "▲"

    # Rank-based color (kept from your working version)
    # Rank-based bright colors
    if rank <= 5:
        bright = "#22C55E"      # green
    elif rank <= 10:
        bright = "#F97316"      # orange
    elif rank <= 20:
        bright = "#EF4444"      # red
    else:
        # ranks > 20 → baseline grey
        bright = "#BBBDC2"      # Tailwind Gray-500 (medium grey)

    dim = darken(bright, 0.70)

    # === Darker + semi-opaque dim for ranks > 20 ===
    if rank > 20:
        # darker, but still clear + opaque enough to see shape
        color = darken(bright, 0.85)   # dark grey, clean + readable
        opacity = "0.50"               # MUCH better than 0.20
    else:
        # normal dimming behavior for the top 20
        if dim_nonselected:
            color = bright if is_selected else dim
            opacity = "1" if is_selected else "0.35 "
        else:
            color = bright
            opacity = "1"



    arrow_style = {
        "position": "absolute",
        "left": f"{pos_pct}%",
        "top": "-24px" if strand == "plus" else None,
        "bottom": "-24px" if strand != "plus" else None,
        "transform": "translateX(-50%)",
        "fontSize": "1em",
        "opacity": opacity,
        "color": color,
        "cursor": "pointer",
        "pointerEvents": "auto",
        "userSelect": "none",
        "zIndex": str(200 - rank),
        # This is what makes arrows SLIDE:
        "transition": (
            "left 0.45s ease-out, "
            "opacity 0.45s ease-out, "
            "color 0.45s ease-out, "
            "top 0.45s ease-out, "
            "bottom 0.45s ease-out"
        ),
    }

    tooltip_text = (
        f"#{rank} | Cut: {loc} | Integ: {row['integration_score']:.1f} | "
        f"gRNA: {row['CRISPRScan_score']:.0f}"
    )

    tooltip_class = "arrow-tooltip-top" if strand == "plus" else "arrow-tooltip-bottom"

    # Use hover-lift class merged with your tagging-arrow classes
    strand_class = "plus" if strand == "plus" else "minus"
    base_classes = ["tagging-arrow", strand_class]
    if is_selected:
        base_classes.append("active-arrow")

    class_name = " ".join(base_classes)

    return [
        html.Div(
            [
                arrow_char,
                html.Div(tooltip_text, className=f"arrow-tooltip {tooltip_class}"),
            ],
            id={"type": "grna-arrow", "index": rank_idx},
            className=class_name,
            style=arrow_style,
        )
    ]

def build_gene_bar(df, sequence_length, gene, selected_idx=None, tag_length='3bp',
                   prev_width_data=None, custom_insert_length=None, linker_color=None, tag_color=None,
                   linker_name=None, tag_name=None, linker_len=None, tag_len=None, mode='Exon',
                   last_exon_length=None, extra_components=None):
    """
    Full corrected version with:
    - left-exon shrink animation synced with insert
    - teleport when growing, smooth when shrinking
    - correct segment order
    - correct gap hugging
    - linker_color: hex color for linker segment (default: #8B4513 brown)
    - tag_color: hex color for tag segment (default: #10B981 green)
    - linker_name: name to display in linker hover popup
    - tag_name: name to display in tag hover popup
    - mode: 'Exon' or 'Intron' - controls colors and labels
    - last_exon_length: length of last_exon_sequence for Intron mode (used for blue block in repair template)
    """

    # Import build_allele_panel here to avoid circular imports
    from .panels import build_allele_panel

    # small segment helper
    def segclass(pct):
        return "tagging-seg small-seg" if pct < 6 else "tagging-seg"

    is_zoomed = selected_idx is not None

    # ============================================================
    # ZOOM MODE GEOMETRY
    # ============================================================
    if is_zoomed:
        row = df.iloc[selected_idx]
        cut = int(row["location"])
        strand = row["strand"]
        dynamic_len = len(row["dynamic_cassette"]) if isinstance(row.get("dynamic_cassette"), str) else None

        LEFT_BP = max(1, int(sequence_length * 0.05))
        RIGHT_BP = max(1, int(sequence_length * 0.05))

        # Use custom insert length only when we don't have preset linker/tag info.
        # When preset info is present, fall back to the split linker/tag view and
        # size the segments using the actual preset lengths when provided.
        use_preset_segments = any([linker_color, tag_color, linker_name, tag_name, linker_len, tag_len])
        if custom_insert_length is not None and not use_preset_segments:
            BROWN_BP = 0  # No brown when custom
            GREEN_BP = custom_insert_length
            is_custom_insert = True
        else:
            BROWN_BP = linker_len if linker_len is not None else 18
            GREEN_BP = tag_len if tag_len is not None else 705
            is_custom_insert = False

        EXTRA_BP = sum(c['length'] for c in extra_components) if extra_components else 0
        INSERT_BP = BROWN_BP + GREEN_BP + EXTRA_BP

        cut_frac = max(0, min(1, cut / float(sequence_length)))
        blue_left_bp = int(cut_frac * sequence_length)
        blue_right_bp = sequence_length - blue_left_bp

        TOTAL = (
            LEFT_BP + blue_left_bp + blue_right_bp +
            INSERT_BP + blue_right_bp + RIGHT_BP
        )

        # percentages
        left_pct = LEFT_BP / TOTAL * 100
        blue_left_pct = blue_left_bp / TOTAL * 100
        blue_right_pct = blue_right_bp / TOTAL * 100
        brown_pct = BROWN_BP / TOTAL * 100
        green_pct = GREEN_BP / TOTAL * 100
        right_pct = RIGHT_BP / TOTAL * 100

        blue_right_left = left_pct + blue_left_pct
        brown_left = left_pct + blue_left_pct + blue_right_pct
        green_left = brown_left + brown_pct
        right_blue_left = green_left + green_pct
        right_grey_left = right_blue_left + blue_right_pct

        # By default, the right cut (insert gap) ends after the green tag.
        insert_right_edge_pct = green_left + green_pct

        blue_pct = (blue_left_bp + blue_right_bp) / TOTAL * 100
        arrow_pos = left_pct + cut_frac * blue_pct
        visual_blue_left_pct = blue_left_pct  # default

        # ============================================================
        # Determine SHRINK vs GROW for left-exon
        # ============================================================
        if isinstance(prev_width_data, (int, float)):
            previous_width = prev_width_data
        else:
            previous_width = blue_left_pct

        is_growing = (blue_left_pct >= previous_width)

        if is_growing:
            start_width = "100%"           # teleport mode
        else:
            start_width = f"{previous_width}%"  # animate from old width

    # ============================================================
    # OVERVIEW MODE GEOMETRY
    # ============================================================
    else:
        LEFT = 5
        RIGHT = 5
        INNER = 90
        TOTAL = sequence_length

    border_style = '1px solid rgba(15,23,42,0.45)'

    # ============================================================
    # ZOOM MODE SEGMENTS
    # ============================================================
    if is_zoomed:
        # Mode-based configuration
        is_intron_mode = (mode == 'Intron')

        # ============================================================
        # BASE BACKGROUND - different color for Intron mode
        # ============================================================
        if is_intron_mode:
            base_bg_color = 'rgba(29, 78, 216, 0.8)'  # Blue background for intron mode (80% opaque)
        else:
            base_bg_color = '#E5E7EB'  # Grey background for exon mode

        base_bg = html.Div(
            style={
                'position': 'absolute',
                'left': 0,
                'top': 0,
                'width': '100%',
                'height': '100%',
                'backgroundColor': base_bg_color,
                'borderRadius': '10px',
                'zIndex': 1
            }
        )

        # Configure left and main segments based on mode
        if is_intron_mode:
            left_bg_color = 'rgba(29, 78, 216, 0)'  # Transparent blue for intron mode
            left_label = ""
            left_popup = "Exon"
            left_text_color = 'white'  # White text on blue
            left_zindex = '4'  # Blue behind

            main_bg_color = 'rgb(229,231,235)'  # Grey for intron mode (fully opaque)
            main_label = f"Last intron {gene}"
            main_popup = "Last intron"
            main_text_color = '#4B5563'  # Dark grey text
            main_zindex = '5'  # Grey on top
        else:
            left_bg_color = 'rgba(229,231,235,0.15)'  # Grey for exon mode
            left_label = ""
            left_popup = "Last intron"
            left_text_color = '#4B5563'  # Dark grey text
            left_zindex = '4'  # Grey behind

            main_bg_color = '#1D4ED8'  # Blue for exon mode
            main_label = "EXON"
            main_popup = "EXON"
            main_text_color = 'white'  # White text on blue
            main_zindex = '5'  # Blue on top in exon mode

        # ---------- Get Repair_Cassette length for both modes ----------
        # Get the actual Repair_Cassette length from the database row
        if 'Repair_Cassette' in row:
            repair_cassette_length = len(row['Repair_Cassette'])
        else:
            # Fallback if column doesn't exist
            repair_cassette_length = INSERT_BP

        # ---------- INTRON MODE: Recalculate percentages BEFORE creating segments ----------
        if is_intron_mode and last_exon_length:
            # For Intron mode: Get the actual Repair_Cassette length from the database row
            # Repair_Cassette = Grey (splice acceptor) + Blue (last exon) + Brown (linker) + Green (tag)
            #
            # LAST_EXON_BP = last_exon_length (from transcript_sequences.db)
            # BROWN_BP = 18 (linker)
            # GREEN_BP = 705 (tag)
            # SPLICE_ACCEPTOR_BP = Repair_Cassette_length - LAST_EXON_BP - BROWN_BP - GREEN_BP

            LAST_EXON_BP = last_exon_length

            # When using a custom insert in intron mode, only the linker/tag portion changes.
            # Keep splice acceptor + last exon lengths, and size the insert from the custom length.
            if is_custom_insert and dynamic_len is not None:
                # dynamic_len already includes splice acceptor + last exon
                SPLICE_ACCEPTOR_BP = max(0, dynamic_len - LAST_EXON_BP)
                repair_cassette_length = dynamic_len + BROWN_BP + GREEN_BP  # brown is 0 for custom
            else:
                SPLICE_ACCEPTOR_BP = repair_cassette_length - LAST_EXON_BP - BROWN_BP - GREEN_BP - EXTRA_BP

            # Ensure non-negative values
            if SPLICE_ACCEPTOR_BP < 0:
                SPLICE_ACCEPTOR_BP = 0
            if LAST_EXON_BP < 0:
                LAST_EXON_BP = 0

            # RECALCULATE TOTAL for Intron mode
            # In Intron mode, INSERT_BP should be repair_cassette_length instead of BROWN_BP + GREEN_BP
            # TOTAL = LEFT_BP + blue_left_bp + blue_right_bp + repair_cassette_length + blue_right_bp + RIGHT_BP
            TOTAL = LEFT_BP + blue_left_bp + blue_right_bp + repair_cassette_length + blue_right_bp + RIGHT_BP

            # Recalculate all percentages with the new TOTAL
            left_pct = LEFT_BP / TOTAL * 100
            blue_left_pct = blue_left_bp / TOTAL * 100
            blue_right_pct = blue_right_bp / TOTAL * 100
            right_pct = RIGHT_BP / TOTAL * 100

            # Calculate percentages for the 4 repair template blocks
            splice_acceptor_pct = SPLICE_ACCEPTOR_BP / TOTAL * 100
            last_exon_pct = LAST_EXON_BP / TOTAL * 100
            brown_pct = BROWN_BP / TOTAL * 100
            green_pct = GREEN_BP / TOTAL * 100

            # Recalculate positions
            blue_right_left = left_pct + blue_left_pct
            brown_left = left_pct + blue_left_pct + blue_right_pct
            green_left = brown_left + brown_pct
            right_blue_left = green_left + green_pct
            right_grey_left = right_blue_left + blue_right_pct

            # Recalculate arrow position
            blue_pct = (blue_left_bp + blue_right_bp) / TOTAL * 100
            arrow_pos = left_pct + cut_frac * blue_pct

            # Total insert uses the actual repair cassette components
            insert_total = splice_acceptor_pct + last_exon_pct + brown_pct + green_pct

            # The right cut should land at the end of the full repair cassette, not just the green tag.
            insert_right_edge_pct = blue_right_left + insert_total

            # Shift the post-insert segments so they start after the full cassette.
            right_blue_left = insert_right_edge_pct
            right_grey_left = right_blue_left + blue_right_pct

            # --- Recompute overall percentages using the ACTUAL cassette length ---
            # In intron mode use a total composed of flanks + full cassette (no default insert swap).
            total_adjusted = LEFT_BP + RIGHT_BP + blue_left_bp + blue_right_bp + repair_cassette_length

            left_pct = LEFT_BP / total_adjusted * 100
            blue_left_pct = blue_left_bp / total_adjusted * 100
            blue_right_pct = blue_right_bp / total_adjusted * 100
            brown_pct = BROWN_BP / total_adjusted * 100
            green_pct = GREEN_BP / total_adjusted * 100
            right_pct = RIGHT_BP / total_adjusted * 100

            blue_right_left = left_pct + blue_left_pct
            brown_left = left_pct + blue_left_pct + blue_right_pct
            green_left = brown_left + brown_pct
            right_blue_left = green_left + green_pct
            right_grey_left = right_blue_left + blue_right_pct

            splice_acceptor_pct = SPLICE_ACCEPTOR_BP / total_adjusted * 100
            last_exon_pct = LAST_EXON_BP / total_adjusted * 100
            brown_pct = BROWN_BP / total_adjusted * 100
            green_pct = GREEN_BP / total_adjusted * 100
            extra_pcts = [c['length'] / total_adjusted * 100 for c in extra_components] if extra_components else []
            insert_total = splice_acceptor_pct + last_exon_pct + brown_pct + green_pct + sum(extra_pcts)
            insert_right_edge_pct = blue_right_left + insert_total
            right_blue_left = insert_right_edge_pct
            right_grey_left = right_blue_left + blue_right_pct

            blue_pct = (blue_left_bp + blue_right_bp) / total_adjusted * 100
            arrow_pos = left_pct + cut_frac * blue_pct

            # Anchor the visible left segment to end exactly at the cut
            visual_blue_left_pct = max(0, arrow_pos - left_pct)

            # DEBUG: Print comprehensive block size calculations for ALL bar segments
            print("=" * 80)
            print("INTRON MODE - REPAIR TEMPLATE DEBUG:")
            print("\nRAW VALUES (base pairs):")
            print(f"  SPLICE_ACCEPTOR_BP (grey): {SPLICE_ACCEPTOR_BP}")
            print(f"  LAST_EXON_BP (blue): {LAST_EXON_BP}")
            print(f"  BROWN_BP (linker): {BROWN_BP}")
            print(f"  GREEN_BP (tag): {GREEN_BP}")
            print(f"  repair_cassette_length (from DB): {repair_cassette_length}")
            print(f"  last_exon_length (from DB): {last_exon_length}")
            print(f"  LEFT_BP: {LEFT_BP} | RIGHT_BP: {RIGHT_BP}")
            print(f"  blue_left_bp (to cut): {blue_left_bp} | blue_right_bp (after cut): {blue_right_bp}")
            print(f"  total_adjusted (bp): {total_adjusted}")

            print("\nREPAIR TEMPLATE PERCENTAGES:")
            print(f"  splice_acceptor_pct (grey): {splice_acceptor_pct:.4f}%")
            print(f"  last_exon_pct (blue): {last_exon_pct:.4f}%")
            print(f"  brown_pct: {brown_pct:.4f}%")
            print(f"  green_pct: {green_pct:.4f}%")
            print(f"  insert_total: {insert_total:.4f}%")

            print("\nREPAIR CASSETTE VERIFICATION:")
            cassette_bp_sum = SPLICE_ACCEPTOR_BP + LAST_EXON_BP + BROWN_BP + GREEN_BP
            print(f"  grey+blue+brown+green = {cassette_bp_sum} bp")
            print(f"  Should equal Repair_Cassette = {repair_cassette_length} bp")
            print(f"  Match: {cassette_bp_sum == repair_cassette_length}")

            print("\nSEGMENT POSITIONS (percent of bar):")
            print(f"  left_pct: {left_pct:.4f}%")
            print(f"  blue_left_pct (computed): {blue_left_pct:.4f}% | visual_blue_left_pct (anchored to cut): {visual_blue_left_pct:.4f}%")
            print(f"  start_of_last_intron_pct: {left_pct:.4f}%")
            print(f"  arrow_pos (cut marker): {arrow_pos:.4f}%  (should equal left_pct + visual_blue_left_pct)")
            print(f"  insert starts at blue_right_left: {blue_right_left:.4f}% and ends at insert_right_edge_pct: {insert_right_edge_pct:.4f}%")
            print(f"  right_blue_left (post-insert exon/intron start): {right_blue_left:.4f}%")
            print(f"  right_grey_left (far right segment start): {right_grey_left:.4f}%")
            print("=" * 80)
        else:
            extra_pcts = [c['length'] / TOTAL * 100 for c in extra_components] if extra_components else []
            insert_total = blue_right_pct + brown_pct + green_pct + sum(extra_pcts)
            if extra_pcts:
                insert_right_edge_pct = green_left + green_pct + sum(extra_pcts)
                right_blue_left = insert_right_edge_pct
                right_grey_left = right_blue_left + blue_right_pct

        # ---------- Left segment (INTRON/EXON depending on mode) ----------
        intron_left = html.Div(
            [
                html.Div(left_label, className='tagging-inline-label', style={'color': left_text_color}),
                html.Div(left_popup, className='tagging-seg-popup')
            ],
            id={'type': 'blue-seg-back', 'index': 'intron-left'},
            className='tagging-seg tagging-grey-appear',
            style={
                'left': '0',
                'width': f'{left_pct}%',
                '--final-width': f'{left_pct}%',
                'backgroundColor': left_bg_color,
                'borderRadius': '10px 0 0 10px',
                'zIndex': left_zindex,
                'cursor': 'pointer',
                'pointerEvents': 'auto'
            }
        )

        # ---------- Main Left segment (EXON/INTRON depending on mode) ----------
        # Add border radius to prevent overflow when left grey is small
        blue_left_border_radius = '10px 0 0 10px' if left_pct < 3 else '0'
        # Render the main left segment from the end of the left buffer up to the cut
        left_block_left = left_pct
        left_width_for_render = blue_left_pct

        blue_left_seg = html.Div(
            [
                html.Div(main_label, className="tagging-inline-label", style={'color': main_text_color}),
                html.Div(main_popup, className="tagging-seg-popup")
            ],
            id={'type': 'blue-seg-back', 'index': 'exon-left'},
            className=segclass(left_width_for_render) + " tagging-blue-left",
            style={
                'left': f'{left_block_left}%',
                'width': f'{left_width_for_render}%',
                '--final-left': f'{left_block_left}%',
                '--final-width': f'{left_width_for_render}%',
                '--start-width': start_width,
                'backgroundColor': main_bg_color,
                'borderLeft': border_style,
                'borderRadius': blue_left_border_radius,
                'overflow': 'visible',
                'zIndex': main_zindex
            }
        )

        # ---------- INSERT (structure depends on mode) ----------
        # Build insert layers based on mode and whether it's custom or default
        if is_custom_insert:
            # Custom insert: orange background with "Custom Insert" label
            if is_intron_mode and last_exon_length:
                # Intron mode with custom insert: grey + blue + orange
                insert_layers = [
                    # Grey splice acceptor
                    html.Div(
                        [html.Div("Endogenous splice acceptor", className="insert-layer-popup")],
                        className="insert-layer insert-layer-grey",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': '0%',
                            'width': f'{(splice_acceptor_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': 'rgb(229,231,235)',
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Blue last_exon
                html.Div(
                        [html.Div("Last exon", className="insert-layer-popup")],
                        className="insert-layer insert-layer-blue",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{(splice_acceptor_pct/insert_total)*100}%',
                            'width': f'{(last_exon_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': '#1D4ED8',
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Orange custom insert (replaces brown + green)
                html.Div(
                        [html.Div("Custom Insert", className="insert-layer-popup")],
                        className="insert-layer insert-layer-custom",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{((splice_acceptor_pct + last_exon_pct)/insert_total)*100}%',
                            'width': f'{(green_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': '#F97316',  # Orange
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                    html.Div("CUSTOM REPAIR TEMPLATE", className="tagging-inline-label repair-template-label",
                             style={'zIndex': 2, 'position': 'relative'})
                ]
            else:
                # Exon mode with custom insert
                insert_layers = [
                    # Blue-right sliver
                    html.Div(
                        [html.Div("Remaining Exon without stopcodon", className="insert-layer-popup")],
                        className="insert-layer insert-layer-blue",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': '0%',
                            'width': f'{(blue_right_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': '#1D4ED8',
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Orange custom insert (replaces brown + green)
                html.Div(
                        [html.Div("Custom Insert", className="insert-layer-popup")],
                        className="insert-layer insert-layer-custom",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{(blue_right_pct/insert_total)*100}%',
                            'width': f'{(green_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': '#F97316',  # Orange
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                    html.Div("CUSTOM REPAIR TEMPLATE", className="tagging-inline-label repair-template-label",
                             style={'zIndex': 2, 'position': 'relative'})
                ]
        else:
            # Default insert: brown + green with standard labels (or custom colors from preset)
            # Use provided colors or defaults
            actual_linker_color = linker_color if linker_color else '#B45309'
            actual_tag_color = tag_color if tag_color else '#22C55E'
            actual_linker_name = linker_name if linker_name else "GS-Linker"
            actual_tag_name = tag_name if tag_name else "mBaoJin"

            if is_intron_mode and last_exon_length:
                # Intron mode: 4 blocks (grey + blue + brown + green)
                insert_layers = [
                    # Grey splice acceptor
                    html.Div(
                        [html.Div("Endogenous splice acceptor", className="insert-layer-popup")],
                        className="insert-layer insert-layer-grey",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': '0%',
                            'width': f'{(splice_acceptor_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': 'rgb(229,231,235)',
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Blue last_exon
                html.Div(
                        [html.Div("Last exon", className="insert-layer-popup")],
                        className="insert-layer insert-layer-blue",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{(splice_acceptor_pct/insert_total)*100}%',
                            'width': f'{(last_exon_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': '#1D4ED8',
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Brown/Linker
                html.Div(
                        [html.Div(actual_linker_name, className="insert-layer-popup")],
                        className="insert-layer insert-layer-brown",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{((splice_acceptor_pct + last_exon_pct)/insert_total)*100}%',
                            'width': f'{(brown_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': actual_linker_color,
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Green/Tag
                html.Div(
                        [html.Div(actual_tag_name, className="insert-layer-popup")],
                        className="insert-layer insert-layer-green",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{((splice_acceptor_pct + last_exon_pct + brown_pct)/insert_total)*100}%',
                            'width': f'{(green_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': actual_tag_color,
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                ] + [
                # Extra components (beyond primary linker + tag)
                html.Div(
                    [html.Div(comp['name'], className="insert-layer-popup")],
                    className="insert-layer",
                    **{
                        'style': {
                            'position': 'absolute',
                            'left': f'{((splice_acceptor_pct + last_exon_pct + brown_pct + green_pct + sum(extra_pcts[:i]))/insert_total)*100}%',
                            'width': f'{(extra_pcts[i]/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': comp['color'],
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                )
                for i, comp in enumerate(extra_components or [])
                ] + [
                    html.Div("REPAIR TEMPLATE", className="tagging-inline-label repair-template-label",
                             style={'zIndex': 2, 'position': 'relative'})
                ]
            else:
                # Exon mode: 3 blocks (blue + brown + green)
                insert_layers = [
                    # Blue-right sliver
                    html.Div(
                        [html.Div("Remaining Exon without stopcodon", className="insert-layer-popup")],
                        className="insert-layer insert-layer-blue",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': '0%',
                            'width': f'{(blue_right_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': '#1D4ED8',
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Brown/Linker
                html.Div(
                        [html.Div(actual_linker_name, className="insert-layer-popup")],
                        className="insert-layer insert-layer-brown",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{(blue_right_pct/insert_total)*100}%',
                            'width': f'{(brown_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': actual_linker_color,
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                # Green/Tag
                html.Div(
                        [html.Div(actual_tag_name, className="insert-layer-popup")],
                        className="insert-layer insert-layer-green",
                        **{
                            'style': {
                            'position': 'absolute',
                            'left': f'{((blue_right_pct+brown_pct)/insert_total)*100}%',
                            'width': f'{(green_pct/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': actual_tag_color,
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                ),
                ] + [
                # Extra components (beyond primary linker + tag)
                html.Div(
                    [html.Div(comp['name'], className="insert-layer-popup")],
                    className="insert-layer",
                    **{
                        'style': {
                            'position': 'absolute',
                            'left': f'{((blue_right_pct + brown_pct + green_pct + sum(extra_pcts[:i]))/insert_total)*100}%',
                            'width': f'{(extra_pcts[i]/insert_total)*100}%',
                            'height': '100%',
                            'backgroundColor': comp['color'],
                            'zIndex': 1,
                            'overflow': 'visible'
                        }
                    }
                )
                for i, comp in enumerate(extra_components or [])
                ] + [
                    html.Div("REPAIR TEMPLATE", className="tagging-inline-label repair-template-label",
                             style={'zIndex': 2, 'position': 'relative'})
                ]

        # Create a diagonal pattern overlay using CSS class
        pattern_overlay = html.Div(className="insert-pattern")

        insert_block = html.Div(
            insert_layers + [pattern_overlay],
            id={'type': 'blue-seg-back', 'index': 'insert'},
            className=segclass(insert_total) + " tagging-insert-appear",
            style={
                'left': f'{blue_right_left}%',
                'width': '0%',
                '--final-width': f'{insert_total}%',
                '--final-left': f'{blue_right_left}%',
                '--initial-left': f'{arrow_pos}%',
                'borderLeft': border_style,
                'borderRight': border_style,
                'overflow': 'visible',
                'position': 'absolute',
                'top': 0,
                'height': '100%',
                'zIndex': 5
            }
        )

        # ---------- Exon Right (Non-coding exon) ----------
        # Add border radius to prevent overflow when right grey is small
        right_blue_border_radius = '0 10px 10px 0' if right_pct < 3 else '0'

        # Configure right segment based on mode
        if is_intron_mode:
            right_seg_label = "Intron"
            right_seg_popup = "Intron"
            right_seg_bg = 'rgb(229,231,235)'  # Grey for intron mode (fully opaque)
            right_seg_text_color = '#4B5563'  # Dark grey text on light grey
        else:
            right_seg_label = "Non-coding exon"
            right_seg_popup = "Non-coding exon"
            right_seg_bg = 'rgba(29, 78, 216, 0.5)'  # Darker faded blue for exon mode
            right_seg_text_color = 'white'  # White text on blue

        right_blue_seg = html.Div(
            [
                html.Div(right_seg_label, className="tagging-inline-label", style={'color': right_seg_text_color}),
                html.Div(right_seg_popup, className="tagging-seg-popup")
            ],
            id={'type': 'blue-seg-back', 'index': 'exon-right'},
            className=segclass(blue_right_pct),
            style={
                'left': f'{right_blue_left}%',
                'width': f'{blue_right_pct}%',
                'backgroundColor': right_seg_bg,
                'borderRight': border_style,
                'borderRadius': right_blue_border_radius,
                'overflow': 'visible',
                'zIndex': 7,
                'cursor': 'pointer',
                'pointerEvents': 'auto'
            }
        )

        # ---------- Non-CDS / CDS ----------
        # Configure rightmost segment based on mode
        if is_intron_mode:
            rightmost_popup = "Last exon"
            rightmost_bg_color = 'rgba(29, 78, 216, 0)'  # Transparent blue for intron mode
        else:
            rightmost_popup = "CDS"
            rightmost_bg_color = 'rgba(229,231,235,0.15)'  # Grey for exon mode

        right_seg = html.Div(
            [
                html.Div("", className="tagging-inline-label"),
                html.Div(rightmost_popup, className="tagging-seg-popup")
            ],
            id={'type': 'blue-seg-back', 'index': 'noncds-right'},
            className=segclass(right_pct) + " tagging-grey-appear",
            style={
                'left': f'{right_grey_left}%',
                'width': '0%',
                '--final-width': f'{right_pct}%',
                'backgroundColor': rightmost_bg_color,
                'borderRadius': '0 10px 10px 0',
                'overflow': 'visible',
                'zIndex': 6,
                'cursor': 'pointer',
                'pointerEvents': 'auto'
            }
        )

        # ---------- Cut lines ----------
        cutgap = html.Div(
            className="tagging-cutgap",
            style={'left': 'calc(var(--cut-left) - 3px)'}
        )
        insertgap = html.Div(
            className="tagging-cutgap",
            style={'left': f'calc({insert_right_edge_pct}% - 3px)'}
        )
        glow = html.Div(
            className="tagging-cutglow",
            style={'left': f'{arrow_pos}%'}
        )

        cut_label = html.Div(
            str(cut),
            className="cut-label",
            style={
                'position': 'absolute',
                'top': '50%',
                'left': 'var(--cut-left)',
                'transform': 'translate(-50%, -50%)'
            }
        )
        insert_label = html.Div(
            "*",
            className="cut-label secondary-cut-label",
            style={
                'position': 'absolute',
                'top': '50%',
                'left': 'var(--insert-left)',
                'transform': 'translate(-50%, -50%)'
            }
        )

        # Build arrows after all geometry is finalized
        arrow_blocks = []
        for rank_idx, (_, r) in enumerate(df.iterrows()):
            loc = r["location"]
            frac = max(0, min(1, loc / float(sequence_length)))

            if frac <= cut_frac:
                local = frac / cut_frac if cut_frac > 0 else 0
                pos_pct = left_pct + local * blue_left_pct
            else:
                local = (frac - cut_frac) / (1 - cut_frac) if (1 - cut_frac) > 0 else 0
                pos_pct = right_blue_left + local * blue_right_pct

            arrow_blocks.extend(
                build_arrow(
                    rank_idx,
                    r,
                    pos_pct,
                    is_selected=(rank_idx == selected_idx),
                    dim_nonselected=is_zoomed
                )
            )

        segments = [
            base_bg,
            intron_left,
            blue_left_seg,
            insert_block,
            right_blue_seg,
            right_seg,
            glow,
            cutgap,
            insertgap,
            insert_label,
            *arrow_blocks,
            cut_label,
            html.Div("0", style={'position': 'absolute','bottom': '-28px','left': '0'}),
            html.Div(str(sequence_length + repair_cassette_length),
                     style={'position': 'absolute','bottom': '-28px','right': '0'})
        ]

    # ============================================================
    # OVERVIEW MODE SEGMENTS
    # ============================================================
    else:
        # Mode-based configuration for overview
        is_intron_mode = (mode == 'Intron')

        # ============================================================
        # BASE BACKGROUND - always grey for overview mode
        # ============================================================
        base_bg = html.Div(
            style={
                'position': 'absolute',
                'left': 0,
                'top': 0,
                'width': '100%',
                'height': '100%',
                'backgroundColor': '#E5E7EB',
                'borderRadius': '10px',
                'zIndex': 1
            }
        )

        if is_intron_mode:
            # Intron mode: left is blue "Exon", right is blue "Last exon", center is grey "Last intron gene"
            left_bg = 'rgba(29,78,216,0.8)'  # Blue
            left_popup = "Exon"
            right_bg = 'rgba(29,78,216,0.8)'  # Blue
            right_popup = "Last exon"
            center_bg = 'rgba(229,231,235,0.05)'  # Grey
            center_text = f"{gene} LAST INTRON"
        else:
            # Exon mode: left is grey "Last intron", right is grey "CDS", center is blue "Last exon gene"
            left_bg = 'rgba(229,231,235,0.05)'  # Grey
            left_popup = "Last intron"
            right_bg = 'rgba(229,231,235,0.05)'  # Grey
            right_popup = "CDS"
            center_bg = 'rgba(29,78,216,0.8)'  # Blue
            center_text = f"{gene} LAST EXON"

        left_seg = html.Div(
            [
                html.Div("", className="tagging-inline-label"),
                html.Div(left_popup, className="tagging-seg-popup")
            ],
            className="tagging-seg",
            style={
                'left': '0%',
                'width': f'{LEFT}%',
                'backgroundColor': left_bg,
                'borderRadius': '10px 0 0 10px',
                'cursor': 'pointer',
                'pointerEvents': 'auto',
                'zIndex': '4'
            }
        )

        right_seg = html.Div(
            [
                html.Div("", className="tagging-inline-label"),
                html.Div(right_popup, className="tagging-seg-popup")
            ],
            className="tagging-seg",
            style={
                'right': '0%',
                'width': f'{RIGHT}%',
                'backgroundColor': right_bg,
                'borderRadius': '0 10px 10px 0',
                'cursor': 'pointer',
                'pointerEvents': 'auto',
                'zIndex': '4'
            }
        )

        # Text color: dark grey on light grey backgrounds (intron mode), white on colored backgrounds (exon mode)
        center_text_color = '#4B5563' if is_intron_mode else 'white'  # Dark grey for intron (grey bg), white for exon (blue bg)

        blue_seg = html.Div(
            [
                html.Div(
                    center_text,
                    style={
                        'position': 'absolute',
                        'top': '50%',
                        'left': '50%',
                        'transform': 'translate(-50%, -50%)',
                        'color': center_text_color,
                        'fontWeight': 'bold',
                        'fontSize': '1.05em',
                        'pointerEvents': 'none'
                    }
                )
            ],
            style={
                'position': 'absolute',
                'top': '0',
                'height': '100%',
                'left': f'{LEFT}%',
                'width': f'{INNER}%',
                'backgroundColor': center_bg,
                'borderLeft': border_style,
                'borderRight': border_style,
                'overflow': 'visible',
                'pointerEvents': 'none',
                'zIndex': '3'
            }
        )

        arrow_blocks = []
        for rank_idx, (_, r) in enumerate(df.iterrows()):
            loc = r["location"]
            pos_pct = LEFT + (loc / sequence_length) * INNER
            arrow_blocks.extend(
                build_arrow(
                    rank_idx,
                    r,
                    pos_pct,
                    is_selected=False,
                    dim_nonselected=False
                )
            )

        segments = [
            base_bg,
            left_seg,
            right_seg,
            blue_seg,
            *arrow_blocks,
            html.Div("0", style={'position': 'absolute','bottom': '-28px','left': f'{LEFT}%'}),
            html.Div(str(sequence_length),
                     style={'position': 'absolute','bottom': '-28px','right': f'{RIGHT}%'})
        ]

    bar_style = {
        'position': 'relative',
        'width': '100%',
        'height': '40px',
        'border': border_style,
        'borderRadius': '10px',
        'overflow': 'visible'
    }
    if is_zoomed:
        bar_style['--cut-left'] = f'{arrow_pos}%'
        bar_style['--insert-left'] = f'{insert_right_edge_pct}%'

    bar = html.Div(
        segments,
        className='tagging-bar',
        style=bar_style
    )

    allele_panel = build_allele_panel(row, gene, tag_length, mode=mode) if is_zoomed else None

    # IMPORTANT: return the new width too!
    return bar, allele_panel
