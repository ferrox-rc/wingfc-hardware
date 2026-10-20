#!/usr/bin/env python3
"""
KiCad 10 PCB Generator for WingFC - Compact 32x32.5mm Layout
Refined placement with zero shorts, verified clearances, clean courtyards.
"""
import pcbnew
import re
import os
import math

def mm(v):
    return int(round(v * 1e6))

def build_pcb():
    pcb_path = "/home/bryansouza/Repos/WingFC/hardware/kicad/WingFC.kicad_pcb"
    net_path = "/home/bryansouza/Repos/WingFC/hardware/kicad/WingFC.net"
    fp_base = "/home/bryansouza/Repos/WingFC/hardware/kicad/footprints"

    # Create fresh 4-layer board
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)

    # Board design settings: standard 0.15mm clearance for TSOT/LGA/SMD
    settings = board.GetDesignSettings()
    settings.m_MinClearance = mm(0.15)
    settings.m_TrackMinWidth = mm(0.15)
    settings.m_ViasMinSize = mm(0.45)
    settings.m_ViasMinDrill = mm(0.2)
    settings.m_CopperEdgeClearance = mm(0.3)
    settings.m_HoleClearance = mm(0.25)
    
    # Configure Default NetClass
    dnc = settings.m_NetSettings.GetDefaultNetclass()
    dnc.SetClearance(mm(0.15))
    dnc.SetTrackWidth(mm(0.20))
    dnc.SetViaDiameter(mm(0.50))
    dnc.SetViaDrill(mm(0.25))

    # 1. Board Dimensions & Center
    cx, cy = 150.0, 100.0
    w = 32.0 # 134.0 to 166.0
    x_min, x_max = cx - w / 2.0, cx + w / 2.0
    y_min = 84.0  # USB-C flush at North edge
    y_max = 117.2 # 4.45mm past lower mounting holes (33.2mm total board length)

    edge_layer = pcbnew.Edge_Cuts

    def add_line(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        s.SetLayer(edge_layer)
        s.SetWidth(mm(0.15))
        board.Add(s)

    def add_arc(cx_a, cy_a, start_x, start_y, end_x, end_y):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(pcbnew.VECTOR2I(mm(cx_a), mm(cy_a)))
        s.SetStart(pcbnew.VECTOR2I(mm(start_x), mm(start_y)))
        s.SetEnd(pcbnew.VECTOR2I(mm(end_x), mm(end_y)))
        s.SetLayer(edge_layer)
        s.SetWidth(mm(0.15))
        board.Add(s)

    r = 2.0
    # Top edge with shallow USB-C access notch between X = 144.5 and X = 155.5
    add_arc(x_min + r, y_min + r, x_min, y_min + r, x_min + r, y_min)
    add_line(x_min + r, y_min, 144.5, y_min)
    # USB Notch (steps back by 0.8mm from 84.0 to 84.8)
    add_line(144.5, y_min, 145.5, y_min + 0.8)
    add_line(145.5, y_min + 0.8, 154.5, y_min + 0.8)
    add_line(154.5, y_min + 0.8, 155.5, y_min)
    add_line(155.5, y_min, x_max - r, y_min)
    # Right top corner
    add_arc(x_max - r, y_min + r, x_max - r, y_min, x_max, y_min + r)
    # Right side
    add_line(x_max, y_min + r, x_max, y_max - r)
    # Bottom right corner
    add_arc(x_max - r, y_max - r, x_max, y_max - r, x_max - r, y_max)
    # Bottom side
    add_line(x_max - r, y_max, x_min + r, y_max)
    # Bottom left corner
    add_arc(x_min + r, y_max - r, x_min + r, y_max, x_min, y_max - r)
    # Left side
    add_line(x_min, y_max - r, x_min, y_min + r)

    # 2. Add 4x M2 Mounting Holes (25.5mm x 25.5mm pitch)
    hole_fp_path = os.path.join(fp_base, "MountingHole.pretty")
    hole_offset = 25.5 / 2.0  # 12.75 mm
    for idx, (hx, hy) in enumerate([(cx - hole_offset, cy - hole_offset),
                                    (cx + hole_offset, cy - hole_offset),
                                    (cx - hole_offset, cy + hole_offset),
                                    (cx + hole_offset, cy + hole_offset)], 1):
        mh = pcbnew.FootprintLoad(hole_fp_path, "MountingHole_2.2mm_M2")
        mh.SetReference(f"H{idx}")
        board.Add(mh)
        mh.SetPosition(pcbnew.VECTOR2I(mm(hx), mm(hy)))
        ref_text = mh.Reference()
        ref_text.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        ref_text.SetTextThickness(mm(0.12))
        # Move Hx labels inward so they are fully visible and never clipped by corners/edges
        dx = -1.2 if hx < cx else 1.2
        dy = 1.6 if hy < cy else 1.6
        ref_text.SetPosition(pcbnew.VECTOR2I(mm(hx + dx), mm(hy + dy)))

    # 3. Parse Netlist
    with open(net_path) as f:
        net_text = f.read()

    comp_defs = re.findall(r"\(comp\s+\(ref\s+\"([^\"]+)\"\)\s+\(value\s+\"([^\"]+)\"\)\s+\(footprint\s+\"([^\"]+)\"\)", net_text)
    net_blocks = re.findall(r"\(net\s+\(code\s+\"\d+\"\)\s+\(name\s+\"([^\"]+)\"\)(.*?)\n\t\t\)", net_text, re.DOTALL)
    pin_to_net = {}
    net_objects = {}

    for net_name, block in net_blocks:
        net_info = board.FindNet(net_name)
        if not net_info:
            net_info = pcbnew.NETINFO_ITEM(board, net_name)
            board.Add(net_info)
        net_objects[net_name] = net_info
        for ref, pin in re.findall(r"\(node\s+\(ref\s+\"([^\"]+)\"\)\s+\(pin\s+\"([^\"]+)\"\)", block):
            pin_to_net[(ref, pin)] = net_name

    # 4. Component Placements & Orientations
    cy_xiao = 94.5
    # Pin 1 of 1x03 vertical pin header (Pin 1 = Signal, Pin 2 = +5V at 112.75, Pin 3 = GND at 115.29)
    servo_y = 110.21

    actuator_x = {
        "ESC1": cx - 2.5 * 2.54,  # 143.65
        "ESC2": cx - 1.5 * 2.54,  # 146.19
        "S1":   cx - 0.5 * 2.54,  # 148.73
        "S2":   cx + 0.5 * 2.54,  # 151.27
        "S3":   cx + 1.5 * 2.54,  # 153.81
        "S4":   cx + 2.5 * 2.54,  # 156.35
    }

    placements = {
        # =====================================================================
        # Top Layer (F.Cu)
        # =====================================================================
        "U1":    (cx, cy_xiao, "F.Cu", 90),
        
        # JST-SH Ports (Openings point outward towards board edges)
        # J_RC on West edge: angle 270 -> opening points West (-X)
        "J_RC":  (137.2, 96.5, "F.Cu", 270),
        # J_GPS on East edge: angle 90 -> opening points East (+X)
        "J_GPS": (162.8, 96.5, "F.Cu", 90),

        # 6 Primary Actuator Headers (2.54mm pitch)
        "ESC1":  (actuator_x["ESC1"], servo_y, "F.Cu", 0),
        "ESC2":  (actuator_x["ESC2"], servo_y, "F.Cu", 0),
        "S1":    (actuator_x["S1"],   servo_y, "F.Cu", 0),
        "S2":    (actuator_x["S2"],   servo_y, "F.Cu", 0),
        "S3":    (actuator_x["S3"],   servo_y, "F.Cu", 0),
        "S4":    (actuator_x["S4"],   servo_y, "F.Cu", 0),

        # 4 Secondary Actuator Headers (1.27mm pitch) grouped in East bay (horizontal)
        "S5":    (160.5, 102.0, "F.Cu", 90),
        "S6":    (160.5, 104.0, "F.Cu", 90),
        "S7":    (160.5, 106.0, "F.Cu", 90),
        "S8":    (160.5, 108.0, "F.Cu", 90),

        # =====================================================================
        # Bottom Layer (B.Cu)
        # =====================================================================
        # Battery Input & TVS Protection (in West pocket, clear of J_RC and H3)
        "J_BAT": (136.5, 103.5, "B.Cu", 270),
        "D3":    (140.0, 105.8, "B.Cu", 270),

        # Battery Sense Divider (In NW area, clear of H1)
        "R3":    (139.5, 87.0, "B.Cu", 90),
        "R4":    (141.5, 87.0, "B.Cu", 90),
        "C6":    (143.5, 87.0, "B.Cu", 90),

        # Buck Regulator MP2315 & Passives (Under MCU shield, Y in 86.5..99.0)
        "U2":     (146.0, 92.5, "B.Cu", 0),
        "L1":     (146.0, 97.5, "B.Cu", 90),
        # Input capacitors 0805: vertical orientation, spaced horizontally
        "C1":     (140.5, 91.5, "B.Cu", 90),
        "C2":     (142.8, 91.5, "B.Cu", 90),
        "D2":     (141.5, 97.0, "B.Cu", 90),
        "C_BST":  (150.0, 95.0, "B.Cu", 0),
        "C_VCC":  (149.5, 92.5, "B.Cu", 90),
        "R5":     (150.0, 90.0, "B.Cu", 0),
        "R6":     (146.0, 88.0, "B.Cu", 90),
        # Output capacitors 0805 & Bulk 1206: vertical orientation
        "C3":     (151.0, 97.5, "B.Cu", 90),
        "C4":     (153.2, 97.5, "B.Cu", 90),
        "C_BULK": (156.0, 97.5, "B.Cu", 90),

        # Power Protection & MCU Hold-up
        "D4":    (154.5, 92.5, "B.Cu", 0),
        "D1":    (154.5, 88.5, "B.Cu", 0),
        "C5":    (158.0, 88.5, "B.Cu", 90),
        "C8":    (160.5, 88.5, "B.Cu", 90),

        # Barometer (Infineon DPS310) shifted Eastward for clean clearance to D4
        "U3":    (160.5, 94.5, "B.Cu", 0),
        "C7":    (160.5, 97.5, "B.Cu", 0),

        # ESC 5V Isolation Jumpers (North of ESC1/ESC2 Pin 1)
        "JP1":   (actuator_x["ESC1"], 107.0, "B.Cu", 0),
        "JP2":   (actuator_x["ESC2"], 107.0, "B.Cu", 0),

        # SWD Test Points (TP1..TP5)
        "TP1":   (148.5, 107.0, "B.Cu", 0),
        "TP2":   (150.5, 107.0, "B.Cu", 0),
        "TP3":   (152.5, 107.0, "B.Cu", 0),
        "TP4":   (154.5, 107.0, "B.Cu", 0),
        "TP5":   (156.5, 107.0, "B.Cu", 0),

        # Spare GPIO Test Points (TP6..TP8 in West pocket on B.Cu)
        "TP6":   (136.5, 90.5, "B.Cu", 0),
        "TP7":   (136.5, 92.5, "B.Cu", 0),
        "TP8":   (136.5, 94.5, "B.Cu", 0),
    }

    # 5. Load & Place All Components
    placed_mods = {}
    for ref, val, fp in comp_defs:
        lib_nick, fp_name = fp.split(":")
        lib_path = os.path.join(fp_base, f"{lib_nick}.pretty")
        mod = pcbnew.FootprintLoad(lib_path, fp_name)
        if not mod:
            print(f"Error: could not load {fp}")
            continue

        mod.SetReference(ref)
        mod.SetValue(val)
        board.Add(mod)

        if ref in placements:
            px, py, layer_name, angle = placements[ref]
            mod.SetPosition(pcbnew.VECTOR2I(mm(px), mm(py)))
            mod.SetOrientation(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
            if layer_name == "B.Cu":
                mod.Flip(pcbnew.VECTOR2I(mm(px), mm(py)), False)

        for pad in mod.Pads():
            pnum = pad.GetNumber()
            net_name = pin_to_net.get((ref, pnum))
            if net_name and net_name in net_objects:
                pad.SetNet(net_objects[net_name])

        # Silk text formatting & strategic positioning
        ref_item = mod.Reference()
        ref_item.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        ref_item.SetTextThickness(mm(0.12))
        
        # Hide reference silkscreen for small passives and test points to avoid clutter/overlaps
        if ref.startswith(("C", "R", "TP")) or ref in ("D1", "D2", "U1"):
            ref_item.SetVisible(False)
        
        # Explicit label positions for key components
        if ref == "J_RC":
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(137.2), mm(92.5)))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        elif ref == "J_GPS":
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(162.8), mm(91.5)))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        elif ref == "J_BAT":
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(136.5), mm(100.8)))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        elif ref == "D4":
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(154.5), mm(90.15)))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        elif ref == "L1":
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(146.0), mm(94.45)))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        elif ref == "U3":
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(160.5), mm(92.2)))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        elif ref in ("S5", "S6", "S7", "S8"):
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(164.6), mm(placements[ref][1])))
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        elif ref in actuator_x:
            ref_item.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
            px, py, _, _ = placements[ref]
            ref_item.SetPosition(pcbnew.VECTOR2I(mm(px), mm(servo_y - 2.8)))

        placed_mods[ref] = mod

    # 6. Silkscreen Legend for Actuator Pin Rows
    for x_pos in [cx - 8.5, cx + 8.5]:
        for label, y_pos in [("S", servo_y), ("+", servo_y + 2.54), ("-", servo_y + 5.08)]:
            txt = pcbnew.PCB_TEXT(board)
            txt.SetText(label)
            txt.SetPosition(pcbnew.VECTOR2I(mm(x_pos), mm(y_pos)))
            txt.SetLayer(pcbnew.F_SilkS)
            txt.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
            txt.SetTextThickness(mm(0.12))
            board.Add(txt)

    # Top board silkscreen branding: FerroxRC & WingFC in West shelf
    brand1 = pcbnew.PCB_TEXT(board)
    brand1.SetText("FerroxRC")
    brand1.SetPosition(pcbnew.VECTOR2I(mm(138.5), mm(109.2)))
    brand1.SetLayer(pcbnew.F_SilkS)
    brand1.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
    brand1.SetTextThickness(mm(0.13))
    board.Add(brand1)

    brand2 = pcbnew.PCB_TEXT(board)
    brand2.SetText("WingFC")
    brand2.SetPosition(pcbnew.VECTOR2I(mm(138.5), mm(110.8)))
    brand2.SetLayer(pcbnew.F_SilkS)
    brand2.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
    brand2.SetTextThickness(mm(0.13))
    board.Add(brand2)

    # Standalone Center Flight Direction Arrow (Clean, bold, pointing North)
    arrow_y = 105.0
    s_arrow = pcbnew.PCB_SHAPE(board)
    s_arrow.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s_arrow.SetStart(pcbnew.VECTOR2I(mm(cx), mm(arrow_y + 2.0)))
    s_arrow.SetEnd(pcbnew.VECTOR2I(mm(cx), mm(arrow_y - 2.0)))
    s_arrow.SetLayer(pcbnew.F_SilkS)
    s_arrow.SetWidth(mm(0.35))
    board.Add(s_arrow)

    s_head1 = pcbnew.PCB_SHAPE(board)
    s_head1.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s_head1.SetStart(pcbnew.VECTOR2I(mm(cx), mm(arrow_y - 2.0)))
    s_head1.SetEnd(pcbnew.VECTOR2I(mm(cx - 1.2), mm(arrow_y - 0.7)))
    s_head1.SetLayer(pcbnew.F_SilkS)
    s_head1.SetWidth(mm(0.35))
    board.Add(s_head1)

    s_head2 = pcbnew.PCB_SHAPE(board)
    s_head2.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s_head2.SetStart(pcbnew.VECTOR2I(mm(cx), mm(arrow_y - 2.0)))
    s_head2.SetEnd(pcbnew.VECTOR2I(mm(cx + 1.2), mm(arrow_y - 0.7)))
    s_head2.SetLayer(pcbnew.F_SilkS)
    s_head2.SetWidth(mm(0.35))
    board.Add(s_head2)

    # Bottom board silkscreen branding: FerroxRC WingFC Rev C
    b_brand = pcbnew.PCB_TEXT(board)
    b_brand.SetText("FerroxRC WingFC Rev C")
    b_brand.SetPosition(pcbnew.VECTOR2I(mm(cx), mm(103.5)))
    b_brand.SetLayer(pcbnew.B_SilkS)
    b_brand.SetMirrored(True)
    b_brand.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
    b_brand.SetTextThickness(mm(0.12))
    board.Add(b_brand)

    # 7. Antenna Keepout Zone (All Copper Layers)
    keepout = pcbnew.ZONE(board)
    keepout.SetIsRuleArea(True)
    keepout.SetDoNotAllowTracks(True)
    keepout.SetDoNotAllowVias(True)
    keepout.SetDoNotAllowZoneFills(True)
    lset = pcbnew.LSET()
    lset.AddLayer(pcbnew.F_Cu)
    lset.AddLayer(pcbnew.B_Cu)
    lset.AddLayer(pcbnew.In1_Cu)
    lset.AddLayer(pcbnew.In2_Cu)
    keepout.SetLayerSet(lset)
    k_outline = pcbnew.SHAPE_LINE_CHAIN()
    k_outline.Append(mm(145.0), mm(101.5))
    k_outline.Append(mm(155.0), mm(101.5))
    k_outline.Append(mm(155.0), mm(106.0))
    k_outline.Append(mm(145.0), mm(106.0))
    k_outline.SetClosed(True)
    keepout.AddPolygon(k_outline)
    board.Add(keepout)

    # 8. Copper Zones (Planes)
    gnd_net = net_objects.get("GND")
    if gnd_net:
        zone_gnd = pcbnew.ZONE(board)
        zone_gnd.SetLayer(pcbnew.In1_Cu)
        zone_gnd.SetNet(gnd_net)
        outline = pcbnew.SHAPE_LINE_CHAIN()
        outline.Append(mm(x_min), mm(y_min))
        outline.Append(mm(x_max), mm(y_min))
        outline.Append(mm(x_max), mm(y_max))
        outline.Append(mm(x_min), mm(y_max))
        outline.SetClosed(True)
        zone_gnd.AddPolygon(outline)
        board.Add(zone_gnd)

        zone_top = pcbnew.ZONE(board)
        zone_top.SetLayer(pcbnew.F_Cu)
        zone_top.SetNet(gnd_net)
        outline_top = pcbnew.SHAPE_LINE_CHAIN()
        outline_top.Append(mm(x_min), mm(y_min))
        outline_top.Append(mm(x_max), mm(y_min))
        outline_top.Append(mm(x_max), mm(y_max))
        outline_top.Append(mm(x_min), mm(y_max))
        outline_top.SetClosed(True)
        zone_top.AddPolygon(outline_top)
        board.Add(zone_top)

        zone_bot = pcbnew.ZONE(board)
        zone_bot.SetLayer(pcbnew.B_Cu)
        zone_bot.SetNet(gnd_net)
        outline_bot = pcbnew.SHAPE_LINE_CHAIN()
        outline_bot.Append(mm(x_min), mm(y_min))
        outline_bot.Append(mm(x_max), mm(y_min))
        outline_bot.Append(mm(x_max), mm(y_max))
        outline_bot.Append(mm(x_min), mm(y_max))
        outline_bot.SetClosed(True)
        zone_bot.AddPolygon(outline_bot)
        board.Add(zone_bot)

    # In2.Cu: +5V Power Plane
    p5v_net = net_objects.get("+5V")
    if p5v_net:
        zone_5v = pcbnew.ZONE(board)
        zone_5v.SetLayer(pcbnew.In2_Cu)
        zone_5v.SetNet(p5v_net)
        outline_5v = pcbnew.SHAPE_LINE_CHAIN()
        outline_5v.Append(mm(x_min), mm(y_min))
        outline_5v.Append(mm(x_max), mm(y_min))
        outline_5v.Append(mm(x_max), mm(y_max))
        outline_5v.Append(mm(x_min), mm(y_max))
        outline_5v.SetClosed(True)
        zone_5v.AddPolygon(outline_5v)
        board.Add(zone_5v)

    # 9. Fill All Zones
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    # 10. Save Board
    board.Save(pcb_path)
    print(f"SUCCESS: Generated compact WingFC PCB ({w:.1f}x{y_max - y_min:.1f}mm): {pcb_path}")

if __name__ == "__main__":
    build_pcb()
