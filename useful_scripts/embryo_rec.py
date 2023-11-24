'''
 # @ Author: Giovanni Dalmasso
 # @ Create Time: 12-09-2023 15:52:04
 # @ Modified by: Giovanni Dalmasso
 # @ Modified time: 12-09-2023 15:52:16
 # @ Description:
 '''

from vedo import load, show

data_path = '/Users/gio/Library/Mobile Documents/com~apple~CloudDocs/iEMBL/CODE/4d-gene-reconstruction/data_tmp/OPT_ISH_pesao/'
folder = 'OPT_023_ISH_hoxa13 IS_antiGFP_181113/E11.5_ISH_hoxa13_antigen_retrieval_95C_IS_goat_antiGFP_12.7um/C1_WH_IR/'

OPT = load(data_path + folder + 'E11_5 hoxa13 IS goat antiGFP0*.tif')
