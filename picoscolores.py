#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

# Standard LCARS colours
# LCARS CLASSIC THEME, 24# NEMESIS BLUE THEME, 39#LOWER DECKS THEME 42#LOWER DECKS PADD THEME
lcars_colores = [
{"ID":0, "NAME": "space-white", "value": '#f5f6fa' },
{"ID":1, "NAME": "violet-creme", "value": '#ddbbff'},
{"ID":2, "NAME": "green", "value": '#33cc99'},
{"ID":3, "NAME": "magenta", "value": '#cc4499'},
{"ID":4, "NAME": "blue", "value": '#4455ff'},
{"ID":5, "NAME": "yellow", "value": '#ffcc33'},
{"ID":6, "NAME": "violet", "value": '#9944ff'},
{"ID":7, "NAME": "orange", "value": '#ff7700'},
{"ID":8, "NAME": "african-violet", "value": '#cc88ff'},
{"ID":9, "NAME": "text", "value": '#cc77ff'},
{"ID":10, "NAME": "red", "value": '#dd4444'},
{"ID":11, "NAME": "almond", "value": '#ffaa90'},
{"ID":12, "NAME": "almond-creme", "value": '#ffbbaa'},
{"ID":13, "NAME": "sunflower", "value": '#ffcc66'},
{"ID":14, "NAME": "bluey", "value": '#7788ff'},
{"ID":15, "NAME": "gray", "value": '#666688'},
{"ID":16, "NAME": "sky", "value": '#aaaaff'},
{"ID":17, "NAME": "ice", "value": '#88ccff'},
{"ID":18, "NAME": "gold", "value": '#ffaa00'},
{"ID":19, "NAME": "mars", "value": '#ff2200'},
{"ID":20, "NAME": "peach", "value": '#ff8866'},
{"ID":21, "NAME": "butterscotch", "value": '#ff9966'},
{"ID":22, "NAME": "tomato", "value": '#ff5555'},
{"ID":23, "NAME": "lilac", "value": '#cc33ff'},
{"ID":24, "NAME": "evening", "value": '#2255ff'},
{"ID":25, "NAME": "midnight", "value": '#1111ee'},
{"ID":26, "NAME": "ghost", "value": '#88bbff'},
{"ID":27, "NAME": "wheat", "value": '#ccaa88'},
{"ID":28, "NAME": "roseblush", "value": '#cc6666'},
{"ID":29, "NAME": "honey", "value": '#ffcc99'},
{"ID":30, "NAME": "cardinal", "value": '#cc2233'},
{"ID":31, "NAME": "pumpkinshade", "value": '#ff7744'},
{"ID":32, "NAME": "tangerine", "value": '#ff8833'},
{"ID":33, "NAME": "martian", "value": '#99dd66'},
{"ID":34, "NAME": "text2", "value": '#2266ff'},
{"ID":35, "NAME": "moonbeam", "value": '#ccdeff'},
{"ID":36, "NAME": "cool", "value": '#5588ff'},
{"ID":37, "NAME": "galaxy", "value": '#444a77'},
{"ID":38, "NAME": "moonshine", "value": '#ddeeff'},
{"ID":39, "NAME": "october-sunset", "value": '#ff4400'},
{"ID":40, "NAME": "harvestgold", "value": '#ffaa44'},
{"ID":41, "NAME": "butter", "value": '#ddeeff'},
{"ID":42, "NAME": "c43", "value": '#5588ee'},
{"ID":43, "NAME": "c44", "value": '#88ffff'},
{"ID":44, "NAME": "c45", "value": '#344470'},
{"ID":45, "NAME": "c46", "value": '#455580'},
{"ID":46, "NAME": "c47", "value": '#7799dd'},
{"ID":47, "NAME": "c48", "value": '#66ccff'},
{"ID":48, "NAME": "c49", "value": '#99ccff'},
{"ID":49, "NAME": "c50", "value": '#ff3500'},
{"ID":50, "NAME": "c51", "value": '#552255'},
{"ID":51, "NAME": "c52", "value": '#663366'},
{"ID":52, "NAME": "c53", "value": '#774477'},
{"ID":53, "NAME": "c54", "value": '#885588'},
{"ID":54, "NAME": "c55", "value": '#996699'},
{"ID":55, "NAME": "c56", "value": '#ff8800'},
{"ID":56, "NAME": "c57", "value": '#d0b0a0'},
{"ID":57, "NAME": "c58", "value": '#bbbbff'},
{"ID":58, "NAME": "c59", "value": '#99aa66'},
{"ID":59, "NAME": "c60", "value": '#00bb00'},
{"ID":60, "NAME": "c61", "value": '#33ff33'},
{"ID":61, "NAME": "c62", "value": '#ddffdd'},
{"ID":62, "NAME": "c63", "value": '#ffebde'},
{"ID":63, "NAME": "c64", "value": '#cc99cc'},
{"ID":64, "NAME": "c65", "value": '#f6eef6'},
{"ID":65, "NAME": "c66", "value": '#aa66aa'},
{"ID":66, "NAME": "c67", "value": '#dd88dd'},
{"ID":67, "NAME": "c68", "value": '#ff0000'},
{"ID":68, "NAME": "c69", "value": '#cc0000'},
{"ID":69, "NAME": "c70", "value": '#ee0000'},
{"ID":70, "NAME": "c71", "value": '#dfdfdf'},
{"ID":71, "NAME": "c72", "value": '#f7f7f7'},
{"ID":72, "NAME": "42", "value": '#ffeecc'}
]

lcars_theme = [
{"ID": 0 ,"NAME": "LOWER DECKS PADD THEME", "colore0": lcars_colores[42]['value'], "colore1": lcars_colores[43]['value'], "colore2": lcars_colores[44]['value'] , "colore3": lcars_colores[45]['value'], "colore4": lcars_colores[46]['value'], "colore5":lcars_colores[47]['value'], "colore6": lcars_colores[48]['value'], "colore7": lcars_colores[49]['value'], "font0": lcars_colores[43]['value'] },
{"ID": 1 ,"NAME": "LOWER DECKS THEME", "colore0": lcars_colores[39]['value'], "colore1": lcars_colores[40]['value'], "colore2": lcars_colores[7]['value'] , "colore3": lcars_colores[29]['value'], "colore4": lcars_colores[72]['value'], "colore5":lcars_colores[41]['value'], "colore6": lcars_colores[41]['value'], "colore7": lcars_colores[49]['value'], "font0":lcars_colores[43]['value'] },
{"ID": 2 ,"NAME": "Red Alert ?", "colore0": lcars_colores[39]['value'], "colore1": lcars_colores[40]['value'], "colore2": lcars_colores[7]['value'] , "colore3": lcars_colores[29]['value'], "colore4": lcars_colores[41]['value'], "colore5":lcars_colores[41]['value'], "colore6": lcars_colores[41]['value'], "colore7": lcars_colores[49]['value'], "font0": lcars_colores[34]['value'] },
]
