# %%
import numpy as np

data_sources_1d = ['Iceland_data.npz', 'Irish_data.npz', 'Balearic_data.npz']

data_sources_2d = ['Iceland_data_new_2d_model.npz',
                   'Irish_data_new_2d_model.npz',
                   'Balearic_data_new_2d_model.npz']

filenames = ['Iceland', 'Ireland', 'Balearic']

def sort_data(data_1d_loc, data_2d_loc, filename):

    data_1d = np.load(data_1d_loc)
    data_2d = np.load(data_2d_loc)


    d = {'freq_orig': 'freq_origin',
         'freq_simple_model': 'freq_model1',
         'freq_old_model': 'freq_model2',
         'freq_new_1d_model': 'freq_model3',
         'freq_new_2d_model': 'freq_model4',
         'incr_orig': 'incr_origin',
         'incr_simple_model': 'incr_model1',
         'incr_old_model': 'incr_model2',
         'Incr_new_1d_model': 'incr_model3',
         'Incr_new_2d_model': 'incr_model4',
         'autocor_orig_90min': 'auto_origin',
         'autocorr_simple_90min': 'auto_model1',
         'autocor_old_model_90min': 'auto_model2',
         'autocor_new_1d_model_90min': 'auto_model3',
         'autocor_new_2d_model_90min': 'auto_model4'}

    data = {}

    for key, val in d.items():
        if key in data_1d.keys():
            data[val] = data_1d[key]
        if key in data_2d.keys():
            data[val] = data_2d[key]


    np.savez_compressed(filename, **data)

    return

# %%

## Iceland data:
sort_data(data_sources_1d[0], data_sources_2d[0], filenames[0])

## Iceland data:
sort_data(data_sources_1d[1], data_sources_2d[1], filenames[1])

## Balearic data:
sort_data(data_sources_1d[2], data_sources_2d[2], filenames[2])


# %% data soruting for Fig2
data = np.load('Irish_KM_coefficients_new_1d_model.npz')
data2 = np.load('Irish_KM_coefficients_new_2d_model.npz')

edges_1d = data['edges_1d'],
drift_1d = data['kmc_1d_drift'],
diffusion_1d = data['kmc_1s_diffusion'],
edges_2d = data2['edges_2d'],
kmc_2d = data2['kmc_2d'],

c_1_model1 = data['c_1_simple_model'],
c_1_model2 = data['c_1_drift_old_model'],

p_3_model3 = data['p_3_drift_new_1d_model'],
p_1_model3 = data['p_1_drift_new_1d_model'],

epsilon_model2 = data['epsilon_old_model'],
epsilon_model1 = data['epsilon_simple_model'],
d_2_model3 = data['d_2_new_1d_model'],
d_0_model3 = data['d_0_new_1d_model'],

# %%
np.savez_compressed('fig2_Ireland',
    edges_1d = edges_1d[0],
    drift_1d = drift_1d,
    diffusion_1d = diffusion_1d,
    c_1_model1 = c_1_model1,
    c_1_model2 = c_1_model2,
    p_1_model3 = p_1_model3,
    p_3_model3 = p_3_model3,
    epsilon_model1 = epsilon_model1,
    epsilon_model2 = epsilon_model2,
    d_0_model3 = d_0_model3,
    d_2_model3 = d_2_model3,
    edges_2d = edges_2d[0],
    kmc_2d = kmc_2d[0])