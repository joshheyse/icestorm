#!/usr/bin/env python3
#
#  Copyright (C) 2015  Clifford Wolf <clifford@clifford.at>
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import icebox
from icebox import re_match_cached, re_sub_cached
import getopt, sys, os, re

chipname = "iCE40 HX1K"
chipdbfile = "chipdb-1k.txt"
outdir = None
mode8k = False
mode384 = False
tx, ty = 0, 0

def usage():
    print("Usage: %s [options]" % sys.argv[0])
    print("  -x tile_x_coordinate")
    print("  -y tile_y_coordinate")
    print("  -d outdir")
    print("  -8")
    print("  -3")
    sys.exit(0)

try:
    opts, args = getopt.getopt(sys.argv[1:], "x:y:d:83")
except:
    usage()

for o, a in opts:
    if o == "-x":
        tx = int(a)
    elif o == "-y":
        ty = int(a)
    elif o == "-d":
        outdir = a
    elif o == "-8":
        mode8k = True
        chipname = "iCE40 HX8K"
        chipdbfile = "chipdb-8k.txt"
    elif o == "-3":
        mode384 = True
        chipname = "iCE40 LP384"
        chipdbfile = "chipdb-384.txt"
    else:
        usage()

if len(args) != 0:
    usage()

ic = icebox.iceconfig()

mktiles = set()

if mode384:
    ic.setup_empty_384()

    for x in range(1, 7): # IO top/bottom
        mktiles.add((x, 0))
        mktiles.add((x, 9))

    for x in list(range(1, 3)) + list(range(5, 7)): # corners
        mktiles.add((x, 1))
        mktiles.add((x, 8))

    for x in [1,6]:
        mktiles.add((x, 2))
        mktiles.add((x, 7))

    for y in range(1, 9): # left/right IO
        mktiles.add((0, y))
        mktiles.add((7, y))

    for x in range(3, 5): # middle square
        for y in range(4, 6):
            mktiles.add((x, y))

elif mode8k:
    ic.setup_empty_8k()

    for x in list(range(1, 3)) + list(range(8-2, 8+3)) + list(range(15, 19)) + list(range(25-2, 25+3)) + list(range(33-2, 33)):
        mktiles.add((x, 0))
        mktiles.add((x, 33))

    for x in list(range(0, 3)) + list(range(8-1, 8+2)) + list(range(25-1, 25+2)) + list(range(33-2, 34)):
        mktiles.add((x, 1))
        mktiles.add((x, 32))

    for x in list(range(0, 2)) + list(range(8-1, 8+2)) + list(range(25-1, 25+2)) + list(range(34-2, 34)):
        mktiles.add((x, 2))
        mktiles.add((x, 31))

    for x in [0, 33]:
        mktiles.add((x, 15))
        mktiles.add((x, 16))
        mktiles.add((x, 17))
        mktiles.add((x, 18))

    for x in [16, 17]:
        mktiles.add((x, 16))
        mktiles.add((x, 17))

else:
    ic.setup_empty_1k()

    for x in range(1, 13):
        mktiles.add((x, 0))
        mktiles.add((x, 17))

    for x in list(range(0, 6)) + list(range(8, 14)):
        mktiles.add((x, 1))
        mktiles.add((x, 16))

    for x in list(range(0, 5)) + list(range(9, 14)):
        mktiles.add((x, 2))
        mktiles.add((x, 15))

    for y in range(7, 11):
        mktiles.add((0, y))
        mktiles.add((13, y))

    for x in range(6, 8):
        for y in range(8, 10):
            mktiles.add((x, y))

expand_count=[0]

def print_expand_div(title):
    print('<a id="exph%d" href="#" onclick="document.getElementById(\'exph%d\').style.display=\'none\'; document.getElementById(\'exp%d\').style.display=\'block\'; return false">[+] Show %s</a><div id="exp%d" style="display:none">' % (expand_count[0], expand_count[0], expand_count[0], title, expand_count[0]))
    expand_count[0] += 1

def print_expand_end():
    print('</div>')

def print_expand_all():
    print('<a id="exph%d" href="#" onclick="for (i = 0; i < 100; i++) { document.getElementById(\'exph\'+i).style.display=\'none\'; document.getElementById(\'exp\'+i).style.display=\'block\'; }; return false">[+] Expand All</a><span id="exp%d" style="display:none"></span>' % (expand_count[0], expand_count[0]))
    expand_count[0] += 1

def print_index():
    print("<title>Project IceStorm &ndash; %s Overview</title>" % chipname)
    print("<h1>Project IceStorm &ndash; %s Overview</h1>" % chipname)

    print("""<i><a href="http://www.clifford.at/icestorm/">Project IceStorm</a> aims at documenting the bitstream format of Lattice iCE40 FPGAs
and providing simple tools for analyzing and creating bitstream files. This is work in progress.</i>""")

    print("""<p>This documentation is auto-generated by <tt>icebox_html.py</tt> from IceBox.<br/>
A machine-readable form of the database can be downloaded <a href="%s">here</a>.</p>""" % chipdbfile)

    print("""<p>The iCE40 FPGA fabric is organized into tiles. The configuration bits
themselves have the same meaning in all tiles of the same type. But the way the tiles
are connected to each other depends on the types of neighbouring cells. Furthermore,
some wire names are different for e.g. an IO tile on the left border and an IO tile on
the top border.</p>""")

    print("""<p>Click on a highlighted tile below to view the bitstream details for the
tile. The highlighted tiles cover all combinations of neighbouring cells that can be found
in iCE40 FPGAs.</p>""")

    print('<p><table border="1">')
    for y in range(ic.max_y, -1, -1):
        print("<tr>")
        for x in range(ic.max_x + 1):
            if mode8k:
                fontsize="8px"
                print('<td style="width:25px; height:20px;" align="center" valign="center"', end="")
            else:
                fontsize="10px"
                print('<td style="width:40px; height:40px;" align="center" valign="center"', end="")
            if ic.tile_pos(x, y) == None:
                print('>&nbsp;</td>')
            elif (x, y) in mktiles:
                if ic.tile_type(x, y) == "IO": color = "#aee"
                if ic.tile_type(x, y) == "LOGIC": color = "#eae"
                if ic.tile_type(x, y) == "RAMB": color = "#eea"
                if ic.tile_type(x, y) == "RAMT": color = "#eea"
                print('bgcolor="%s"><span style="font-size:%s"><a style="color:#000; text-decoration:none" href="tile_%d_%d.html"><b>%s<br/>(%d %d)</b></a></span></td>' % (color, fontsize, x, y, ic.tile_type(x, y), x, y))
            else:
                if ic.tile_type(x, y) == "IO": color = "#8aa"
                if ic.tile_type(x, y) == "LOGIC": color = "#a8a"
                if ic.tile_type(x, y) == "RAMB": color = "#aa8"
                if ic.tile_type(x, y) == "RAMT": color = "#aa8"
                print('bgcolor="%s"><span style="font-size:%s">%s<br/>(%d %d)</span></td>' % (color, fontsize, ic.tile_type(x, y), x, y))
        print("</tr>")
    print("</table></p>")

def print_tile(tx, ty):
    tile = ic.tile(tx, ty)
    tile_type = ic.tile_type(tx, ty)

    print("<title>Project IceStorm &ndash; %s %s Tile (%d %d)</title>" % (chipname, tile_type, tx, ty))
    print("<h1>Project IceStorm &ndash; %s %s Tile (%d %d)</h1>" % (chipname, tile_type, tx, ty))

    print("""<i><a href="http://www.clifford.at/icestorm/">Project IceStorm</a> aims at documenting the bitstream format of Lattice iCE40 FPGAs
and providing simple tools for analyzing and creating bitstream files. This is work in progress.</i>""")

    print("""<p>This page describes the %s Tile (%d %d), what nets and
configuration bits it has and how it is connected to its neighbourhood.</p>""" % (tile_type, tx, ty))

    visible_tiles = set()

    print('<p><table border="1">')
    for y in range(ty+2, ty-3, -1):
        print("<tr>")
        for x in range(tx-2, tx+3):
            print('<td style="width:100px; height:70px;" align="center" valign="center"', end="")
            if ic.tile_pos(x, y) == None:
                print('>&nbsp;</td>')
            else:
                if (x, y) in mktiles:
                    if ic.tile_type(x, y) == "IO": color = "#aee"
                    if ic.tile_type(x, y) == "LOGIC": color = "#eae"
                    if ic.tile_type(x, y) == "RAMB": color = "#eea"
                    if ic.tile_type(x, y) == "RAMT": color = "#eea"
                    print('bgcolor="%s"><a style="color:#000; text-decoration:none" href="tile_%d_%d.html"><b>%s Tile<br/>(%d %d)</b></a></td>' % (color, x, y, ic.tile_type(x, y), x, y))
                else:
                    if ic.tile_type(x, y) == "IO": color = "#8aa"
                    if ic.tile_type(x, y) == "LOGIC": color = "#a8a"
                    if ic.tile_type(x, y) == "RAMB": color = "#aa8"
                    if ic.tile_type(x, y) == "RAMT": color = "#aa8"
                    print('bgcolor="%s">%s Tile<br/>(%d %d)</td>' % (color, ic.tile_type(x, y), x, y))
                visible_tiles.add((x, y))
        print("</tr>")
    print("</table></p>")

    # print_expand_all()

    print("<h2>Configuration Bitmap</h2>")

    print("<p>A %s Tile has %d config bits in %d groups of %d bits each:<br/>" % (tile_type, len(tile)*len(tile[0]), len(tile), len(tile[0])))
    print(("<tt>%s</tt></p>" % (", ".join(['%sB%d[%d:0]' % ("&nbsp;" if i < 10 else "", i, len(tile[i])-1) for i in range(len(tile))]))).replace("&nbsp;B8", "<br/>&nbsp;B8"))

    bitmap_cells = list()
    for line_nr in range(len(tile)):
        line = list()
        bitmap_cells.append(line)
        for bit_nr in range(len(tile[line_nr])):
            line.append({"bgcolor": "#aaa", "label": "?"})

    for entry in ic.tile_db(tx, ty):
        if not ic.tile_has_entry(tx, ty, entry):
            continue
        for bit in [bit.replace("!", "") for bit in entry[0]]:
            match = re_match_cached(r"B(\d+)\[(\d+)\]$", bit)
            idx1 = int(match.group(1))
            idx2 = int(match.group(2))
            if entry[1] == "routing":
                bitmap_cells[idx1][idx2]["bgcolor"] = "#faa"
                bitmap_cells[idx1][idx2]["label"] = "R"
                bitmap_cells[idx1][idx2]["is_routing"] = True
            elif entry[1] == "buffer":
                bitmap_cells[idx1][idx2]["bgcolor"] = "#afa"
                bitmap_cells[idx1][idx2]["label"] = "B"
                bitmap_cells[idx1][idx2]["is_routing"] = True
            else:
                bitmap_cells[idx1][idx2]["bgcolor"] = "#aaf"
                if entry[1] == "ColBufCtrl":
                    bitmap_cells[idx1][idx2]["label"] = "O"
                elif entry[1].startswith("LC_"):
                    bitmap_cells[idx1][idx2]["label"] = "L"
                elif entry[1].startswith("NegClk"):
                    bitmap_cells[idx1][idx2]["label"] = "N"
                elif entry[1].startswith("CarryInSet"):
                    bitmap_cells[idx1][idx2]["label"] = "C"
                elif entry[1].startswith("IOB_"):
                    bitmap_cells[idx1][idx2]["label"] = "I"
                elif entry[1].startswith("IoCtrl"):
                    bitmap_cells[idx1][idx2]["label"] = "T"
                elif entry[1] == "Icegate":
                    bitmap_cells[idx1][idx2]["label"] = "G"
                elif entry[1].startswith("Cascade"):
                    bitmap_cells[idx1][idx2]["label"] = "A"
                elif entry[1].startswith("RamConfig"):
                    bitmap_cells[idx1][idx2]["label"] = "M"
                elif entry[1].startswith("RamCascade"):
                    bitmap_cells[idx1][idx2]["label"] = "M"
                elif entry[1].startswith("PLL"):
                    bitmap_cells[idx1][idx2]["label"] = "P"
                else:
                    assert False
            bitmap_cells[idx1][idx2]["label"] = '<a style="color:#666; text-decoration:none" href="#B.%d.%d">%s</a>' % (idx1, idx2, bitmap_cells[idx1][idx2]["label"])

    print('<table style="font-size:small">')
    print("<tr><td></td>")
    for cell_nr in range(len(line)):
        print('<td align="center" width="15">%d</td>' % cell_nr)
    print("<td></td></tr>")
    for line_nr, line in enumerate(bitmap_cells):
        print("<tr>")
        print('<td>B%d</td>' % line_nr)
        for cell in line:
            print('<td align="center" bgcolor="%s" style="color:#666;">%s</td>' % (cell["bgcolor"], cell["label"]))
        print('<td>B%d</td>' % line_nr)
        print("</tr>")
    print("<tr><td></td>")
    for cell_nr in range(len(line)):
        print('<td align="center">%d</td>' % cell_nr)
    print("<td></td></tr>")
    print("</table>")

    print("<h2>Nets and Connectivity</h2>")

    print("""<p>This section lists all nets in the tile and how this
nets are connected with nets from cells in its neighbourhood.</p>""")

    grouped_segs = ic.group_segments(set([(tx, ty)]))
    groups_indexed = dict()
    this_tile_nets = dict()

    for segs in sorted(grouped_segs):
        this_segs = list()
        neighbour_segs = dict()
        for s in segs:
            if s[0] == tx and s[1] == ty:
                this_segs.append(s[2])
                match = re_match_cached(r"(.*?_)(\d+)(.*)", s[2])
                if match:
                    this_tile_nets.setdefault(match.group(1) + "*" + match.group(3), set()).add(int(match.group(2)))
                else:
                    this_tile_nets.setdefault(s[2], set()).add(-1)
            if (s[0], s[1]) in visible_tiles:
                neighbour_segs.setdefault((s[0], s[1]), list()).append(s[2])
        if this_segs:
            this_name = ", ".join(sorted(this_segs))
            assert this_name not in groups_indexed
            groups_indexed[this_name] = neighbour_segs

    print("<h3>List of nets in %s Tile (%d %d)</h3>" % (tile_type, tx, ty))

    def net2cat(netname):
        cat = (99, "Unsorted")
        if netname.startswith("glb_netwk_"): cat = (10, "Global Networks")
        if netname.startswith("glb2local_"): cat = (10, "Global Networks")
        if netname.startswith("fabout"): cat = (10, "Global Networks")
        if netname.startswith("local_"): cat = (20, "Local Tracks")
        if netname.startswith("carry_in"): cat = (25, "Logic Block")
        if netname.startswith("io_"): cat = (25, "IO Block")
        if netname.startswith("ram"): cat = (25, "RAM Block")
        if netname.startswith("lutff_"): cat = (25, "Logic Block")
        if netname.startswith("lutff_0"): cat = (30, "Logic Unit 0")
        if netname.startswith("lutff_1"): cat = (30, "Logic Unit 1")
        if netname.startswith("lutff_2"): cat = (30, "Logic Unit 2")
        if netname.startswith("lutff_3"): cat = (30, "Logic Unit 3")
        if netname.startswith("lutff_4"): cat = (30, "Logic Unit 4")
        if netname.startswith("lutff_5"): cat = (30, "Logic Unit 5")
        if netname.startswith("lutff_6"): cat = (30, "Logic Unit 6")
        if netname.startswith("lutff_7"): cat = (30, "Logic Unit 7")
        if netname.startswith("neigh_op_"): cat = (40, "Neighbourhood")
        if netname.startswith("logic_op_"): cat = (40, "Neighbourhood")
        if netname.startswith("sp4_v_"): cat = (50, "Span-4 Vertical")
        if netname.startswith("span4_vert_"): cat = (50, "Span-4 Vertical")
        if netname.startswith("sp4_r_v_"): cat = (55, "Span-4 Right Vertical")
        if netname.startswith("sp4_h_"): cat = (60, "Span-4 Horizontal")
        if netname.startswith("span4_horz_"): cat = (60, "Span-4 Horizontal")
        if netname.startswith("sp12_v_"): cat = (70, "Span-12 Vertical")
        if netname.startswith("span12_vert_"): cat = (70, "Span-12 Vertical")
        if netname.startswith("sp12_h_"): cat = (80, "Span-12 Horizontal")
        if netname.startswith("span12_horz_"): cat = (80, "Span-12 Horizontal")
        return cat

    nets_in_cats = dict()

    for this_name in sorted(this_tile_nets):
        nets_in_cats.setdefault(net2cat(this_name), list()).append(this_name)

    for cat in sorted(nets_in_cats):
        print('<h4>%s</h4>' % cat[1])
        print('<p><ul style="margin:0">')
        for this_name in sorted(nets_in_cats[cat]):
            indices = [i for i in this_tile_nets[this_name] if i >= 0]
            if -1 in this_tile_nets[this_name]:
                print("<li><tt>%s</tt></li>" % this_name)
            if len(indices) == 1:
                print("<li><tt>%s</tt></li>" % this_name.replace("*", "%d" % indices[0]))
            elif len(indices) > 0:
                print("<li><tt>%s</tt></li>" % this_name.replace("*", "{" + ",".join(["%d" % i for i in sorted(indices)]) + "}"))
        print("</ul></p>")

    print("<h3>Nets and their permanent connections to nets in neighbour tiles</h3>")

    # print_expand_div("connection details")

    all_cats = set()
    for this_name in sorted(groups_indexed):
        all_cats.add(net2cat(this_name))

    for cat in sorted(all_cats):
        print('<h4>%s</h4>' % cat[1])
        print('<p><div style="-webkit-column-count: 3; -moz-column-count: 3; column-count: 3;"><ul style="margin:0">')
        for this_name in sorted(groups_indexed):
                if net2cat(this_name) == cat:
                    neighbour_segs = groups_indexed[this_name]
                    print("<li><tt><b>%s</b></tt>" % this_name)
                    if neighbour_segs:
                        print("<ul>")
                        for nidx in sorted(neighbour_segs):
                            if nidx == (tx, ty):
                                print("<li><tt><b>(%d %d)</b> %s</tt></li>" % (nidx[0], nidx[1], ", ".join(sorted(neighbour_segs[nidx]))))
                            else:
                                print("<li><tt>(%d %d) %s</tt></li>" % (nidx[0], nidx[1], ", ".join(sorted(neighbour_segs[nidx]))))
                        print("</ul>")
                    print("</li>")
        print("</ul></div></p>")

    # print_expand_end()

    print("<h2>Routing Configuration</h2>")

    print("""<p>This section lists the routing configuration bits in the tile.
All routing resources are directional tristate buffers that are in tristate mode
in the all-zeros configuration.</p>""")

    grpgrp = dict()
    config_groups = dict()
    other_config_groups = dict()

    for entry in ic.tile_db(tx, ty):
        if not ic.tile_has_entry(tx, ty, entry):
            continue
        if entry[1] in ("routing", "buffer"):
            cfggrp = entry[1] + " " + entry[3] + "," + ",".join(sorted([bit.replace("!", "") for bit in entry[0]]))
            config_groups.setdefault(cfggrp, list()).append(entry)
            grpgrp.setdefault(net2cat(entry[3]), set()).add(cfggrp)
        else:
            grp = other_config_groups.setdefault("&nbsp;".join(entry[1:]), set())
            for bit in entry[0]: grp.add(bit)

    for cat in sorted(grpgrp):
        print('<h4>%s</h4>' % cat[1])

        bits_in_cat = set()

        for cfggrp in sorted(grpgrp[cat]):
            grp = config_groups[cfggrp]
            for bit in cfggrp.split(",")[1:]:
                match = re_match_cached(r"B(\d+)\[(\d+)\]", bit)
                bits_in_cat.add((int(match.group(1)), int(match.group(2))))

        print('<table style="font-size:x-small">')
        print("<tr><td></td>")
        for cell_nr in range(len(bitmap_cells[0])):
            print('<td align="center" width="15">%d</td>' % cell_nr)
        print("<td></td></tr>")
        for line_nr, line in enumerate(bitmap_cells):
            print("<tr>")
            print('<td>B%d</td>' % line_nr)
            for cell_nr, cell in enumerate(line):
                color = cell["bgcolor"]
                if (line_nr, cell_nr) not in bits_in_cat: color="#aaa"
                print('<td align="center" bgcolor="%s" style="color:#666;">%s</td>' % (color, cell["label"]))
            print('<td>B%d</td>' % line_nr)
            print("</tr>")
        print("<tr><td></td>")
        for cell_nr in range(len(line)):
            print('<td align="center">%d</td>' % cell_nr)
        print("<td></td></tr>")
        print("</table>")

        # print_expand_div("details")

        src_nets = set()
        dst_nets = set()
        links = dict()

        for cfggrp in sorted(grpgrp[cat]):
            grp = config_groups[cfggrp]
            for entry in grp:
                src_nets.add(entry[2])
                dst_nets.add(entry[3])
                if entry[1] == "buffer":
                    assert (entry[2], entry[3]) not in links
                    links[(entry[2], entry[3])] = '<td align="center" bgcolor="#afa" style="color:#666;">B</td>'
                else:
                    assert (entry[2], entry[3]) not in links
                    links[(entry[2], entry[3])] = '<td align="center" bgcolor="#faa" style="color:#666;">R</td>'

        print('<h5>Connectivity Matrix</h5>')
        print('<table style="font-size:x-small">')
        dst_net_prefix = ""
        dst_net_list = sorted(dst_nets, key=icebox.key_netname)
        if len(dst_net_list) > 1:
            while len(set([n[0] for n in dst_net_list])) == 1:
                dst_net_prefix += dst_net_list[0][0]
                for i in range(len(dst_net_list)):
                    dst_net_list[i] = dst_net_list[i][1:]
        while dst_net_prefix != "" and dst_net_prefix[-1] != "_":
            for i in range(len(dst_net_list)):
                dst_net_list[i] = dst_net_prefix[-1] + dst_net_list[i]
            dst_net_prefix = dst_net_prefix[0:-1]
        print('<tr><td></td><td colspan="%d" align="center">%s</td></tr>' % (len(dst_net_list), dst_net_prefix))
        print('<tr><td></td>')
        for dn in dst_net_list:
            print('<td>%s</td>' % dn)
        print("</tr>")
        for sn in sorted(src_nets, key=icebox.key_netname):
            print("<tr>")
            print('<td>%s</td>' % sn)
            for dn in sorted(dst_nets, key=icebox.key_netname):
                if (sn, dn) in links:
                    print(links[(sn, dn)])
                else:
                    print('<td align="center" bgcolor="#aaa" style="color:#666;">&nbsp;</td>')
            print("</tr>")
        print("</table>")

        print('<h5>Configuration Stamps</h5>')
        for cfggrp in sorted(grpgrp[cat]):
            grp = config_groups[cfggrp]
            bits = cfggrp.split(",")[1:]
            print('<p><table style="font-size:small" border><tr>')
            for bit in bits:
                print('<th style="width:5em"><a name="%s">%s</a></th>' % (re_sub_cached(r"B(\d+)\[(\d+)\]", r"B.\1.\2", bit), bit))
            group_lines = list()
            is_buffer = True
            for entry in grp:
                line = '<tr>'
                for bit in bits:
                    if bit in entry[0]:
                        line += '<td align="center">1</td>'
                    else:
                        line += '<td align="center">0</td>'
                is_buffer = entry[1] == "buffer"
                line += '<td align="center">%s</td><td><tt>%s</tt></td><td><tt>%s</tt></td></tr>' % (entry[1], entry[2], entry[3])
                group_lines.append(line)
            if is_buffer:
                print('<th style="width:5em">Function</th><th style="width:15em">Source-Net</th><th style="width:15em">Destination-Net</th></tr>')
            else:
                print('<th style="width:5em">Function</th><th style="width:15em">Net</th><th style="width:15em">Net</th></tr>')
            for line in sorted(group_lines):
                print(line)
            print('</table></p>')

        # print_expand_end()

    print("<h2>Non-routing Configuration</h2>")

    print("<p>This section lists the non-routing configuration bits in the tile.</p>")

    print('<table style="font-size:x-small">')
    print("<tr><td></td>")
    for cell_nr in range(len(bitmap_cells[0])):
        print('<td align="center" width="15">%d</td>' % cell_nr)
    print("<td></td></tr>")
    for line_nr, line in enumerate(bitmap_cells):
        print("<tr>")
        print('<td>B%d</td>' % line_nr)
        for cell_nr, cell in enumerate(line):
            color = cell["bgcolor"]
            if "is_routing" in cell: color="#aaa"
            print('<td align="center" bgcolor="%s" style="color:#666;">%s</td>' % (color, cell["label"]))
        print('<td>B%d</td>' % line_nr)
        print("</tr>")
    print("<tr><td></td>")
    for cell_nr in range(len(line)):
        print('<td align="center">%d</td>' % cell_nr)
    print("<td></td></tr>")
    print("</table>")

    print('<p><table style="font-size:small" border><tr><th>Function</th><th>Bits</th></tr>')
    for cfggrp in sorted(other_config_groups):
        bits = " ".join(['<a name="%s">%s</a>' % (re_sub_cached(r"B(\d+)\[(\d+)\]", r"B.\1.\2", bit), bit) for bit in sorted(other_config_groups[cfggrp])])
        cfggrp = cfggrp.replace("&nbsp;" + list(other_config_groups[cfggrp])[0], "")
        print('<tr><td>%s</td><td>%s</td></tr>' % (cfggrp, bits))
    print('</table></p>')


if outdir is not None:
    stdout = sys.stdout

    if not os.path.exists(outdir):
        print("Creating %s/" % outdir, file=stdout)
        os.makedirs(outdir)

    print("Writing %s/index.html.." % outdir, file=stdout)
    sys.stdout = open("%s/index.html" % outdir, "w")
    print_index()

    for x in range(ic.max_x+1):
        for y in range(ic.max_y+1):
            if (x, y) in mktiles:
                print("Writing %s/tile_%d_%d.html.." % (outdir, x, y), file=stdout)
                sys.stdout = open("%s/tile_%d_%d.html" % (outdir, x, y), "w")
                print_tile(x, y)

    print("Writing %s/%s..." % (outdir, chipdbfile), file=stdout)
    if os.access("icebox_chipdb.py", os.R_OK):
        os.system("python3 icebox_chipdb.py %s > %s/%s" % ("-8" if mode8k else "", outdir, chipdbfile))
    else:
        os.system("icebox_chipdb %s > %s/%s" % ("-8" if mode8k else "", outdir, chipdbfile))

    sys.stdout = stdout

elif (tx, ty) == (0, 0):
    print_index()

else:
    print_tile(tx, ty)
