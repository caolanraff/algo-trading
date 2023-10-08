import sys
sys.path.append('/Users/caolanraff/Documents/Development/projects/algo-trading/')

from utils.data import load_financial_data
import h5py

data_dir = '/Users/caolanraff/Development/projects/algo-trading/data/'

data = load_financial_data('GOOG', '2001-01-01', '2018-01-01', 'GOOG_data_large.pkl')

# save as hdf file
data.to_hdf(data_dir + 'GOOG_data.h5', 'goog_data', mode='w', format='table', data_columns=True)

# load from hdf file
data_from_h5 = h5py.File(data_dir + 'GOOG_data.h5')
h5_table = data_from_h5['goog_data']['table']

print(h5_table)
print(h5_table[:])
for attributes in h5_table.attrs.items():
    print(attributes)