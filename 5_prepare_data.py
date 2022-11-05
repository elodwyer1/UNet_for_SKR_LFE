
root="C:/Users/eliza/Desktop/Python_Scripts/"

## Imports
import shutil
import os
import random
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from os import listdir
from os.path import isfile, join

## Seeding 
seed = 42
random.seed = seed
np.random.seed = seed


#Function to read image and convert to numpy array.
def img_to_arr(infilename) :
    img=plt.imread(infilename)
    
    imgr=img[:,:,0]
    imgg=img[:,:,1]
    imgb=img[:,:,2]
    imgalpha=img[:,:,3]

    img_inds=(imgalpha==0)
    imgr=np.ma.masked_array(imgr, mask=img_inds).filled(0).reshape((imgr.shape[0], imgr.shape[1],1))
    imgg=np.ma.masked_array(imgg, mask=img_inds,fill_value=0).filled(0).reshape((imgr.shape[0], imgr.shape[1],1))
    imgb=np.ma.masked_array(imgb, mask=img_inds,fill_value=0).filled(0).reshape((imgr.shape[0], imgr.shape[1],1))
    imgcom=np.concatenate([imgr, imgg, imgb],axis=2)
    img_gray =cv2.cvtColor(imgcom,cv2.COLOR_RGB2GRAY)
    return img_gray

#Function to combine flux and polarization data.
def combine_channels(flux_file, pol_file):
    flx = img_to_arr(flux_file)
    flx=np.reshape(flx, (flx.shape[0], flx.shape[1], 1))
    pol=img_to_arr(pol_file)
    pol=np.reshape(pol, (pol.shape[0], pol.shape[1], 1))
    ttl = np.concatenate([flx, pol], axis=2)
    return ttl 
def read_mask(file1):
    img=plt.imread(file1)
    img_gray =cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    return img_gray

def save_files(flux_file, pol_file,mask_file1,num,path_):
    ttl = combine_channels(flux_file, pol_file)
    mask = read_mask(mask_file1)
    
    ttlpath = path_+str(num).zfill(3)+'/images'
    if os.path.exists(ttlpath):
        shutil.rmtree(ttlpath)
    os.makedirs(ttlpath)
    maskpath = path_+str(num).zfill(3)+'/masks'
    if os.path.exists(maskpath):
        shutil.rmtree(maskpath)
    os.makedirs(maskpath)
    np.save(ttlpath + '/' + str(num).zfill(3)+'.npy',ttl)
    np.save(maskpath + '/' + str(num).zfill(3)+'.npy',mask)
    return ttl,mask

def save_label(label,num,path_):
    ttlpath=path_+str(num).zfill(3)+'/label'
    if os.path.exists(ttlpath):
        shutil.rmtree(ttlpath)
    os.makedirs(ttlpath)
    label_path = ttlpath + '/' + str(num).zfill(3)+'.npy'
    np.save(label_path,label)
    return None
def save_traj(lat_st, lat_m, lt_std, lt_med,num,path_):
    ttlpath=path_+str(num).zfill(3)+'/traj'
    
    if os.path.exists(ttlpath):

      shutil.rmtree(ttlpath)
    os.makedirs(ttlpath)

    label_arr = [lat_st, lat_m, lt_std, lt_med]
    
    np.save(ttlpath + '/' + str(num).zfill(3)+'.npy',label_arr)

    return None


'''________Flux and Pol_________'''
count=3000
#Read in directories for each Flux/Polarization Spectrogram showing an LFE image.
flxpath=root+'ML_Dataset/flux_images/'
flx_labels=[f for f in listdir(flxpath) if isfile(join(flxpath, f))]
flxfiles = [root+'ML_Dataset/flux_images/'+f for f in flx_labels]
polpath=root+'ML_Dataset/pol_images/'
pol_labels=[f for f in listdir(polpath) if isfile(join(polpath, f))]
polfiles = [root+'ML_Dataset/pol_images/'+f for f in pol_labels]


#LFE filepaths
flux_lfe_files = [root+'ML_Dataset/flux_images/fl_img'+str(i).zfill(4)+'.png' for i in range(count)]
#Final List
flux_lfe_files = [i for i in flux_lfe_files if i in flxfiles]
###############################################################
pol_lfe_files=[root+'ML_Dataset/pol_images/pl_img'+str(i).zfill(4)+'.png' for i in range(count)]
#Final List
pol_lfe_files=[i for i in pol_lfe_files if i in polfiles]


'''______Mask_________'''
maskpath1=root+'ML_Dataset/mask_images/'
mask_image_label1=[f for f in listdir(maskpath1) if isfile(join(maskpath1, f))]
mask_fp1 = [maskpath1+i for i in mask_image_label1]
mask_files1 = [root+'ML_Dataset/mask_images/mask_img'+str(i).zfill(4)+'.png' for i in range(count)]
mask_file1=[i for i in mask_files1 if i in mask_fp1]

'''________labels and trajectory________'''
lfe_info = pd.read_csv(root+"ML_Dataset/ML_total_catalogue_withaug.csv")
ttl_labels=np.array(lfe_info['label'])
lat_std = np.array(lfe_info['lat_stdev'])
lat_med = np.array(lfe_info['lat_median'])
lt_std = np.array(lfe_info['lt_stdev'])
lt_med = np.array(lfe_info['lt_median'])

'''________Separate out augmented data so that it goes into training set only'''
frac_train=(0.75*(2091)-100)/(1991)

label=ttl_labels[0:1991]
pol = pol_lfe_files[0:1991]
flux=flux_lfe_files[0:1991]
mask=mask_file1[0:1991]
lat_s =lat_std[0:1991]
lt_s=lt_std[0:1991]
lat_m=lat_med[0:1991]
lt_m=lt_med[0:1991]

label_augment=ttl_labels[1991:]
flux_augment=flux_lfe_files[1991:]
pol_augment=pol_lfe_files[1991:]
mask_augment=mask_file1[1991:]
lat_s_augment =lat_std[1991:]
lt_s_augment=lt_std[1991:]
lat_m_augment=lat_med[1991:]
lt_m_augment=lt_med[1991:]

train_flux ,test_flux, train_pol, test_pol, train_m1, test_m1, train_label, test_label, lat_m_train, lat_m_test, lat_s_train, lat_s_test,lt_m_train, lt_m_test, lt_s_train, lt_s_test=train_test_split(flux,pol, mask,label,lat_m, lat_s, lt_m, lt_s, train_size=frac_train, random_state=42, shuffle=True, stratify=label)
train_flux=np.concatenate([train_flux, flux_augment],axis=0)
train_pol=np.concatenate([train_pol, pol_augment],axis=0)
train_m1=np.concatenate([train_m1, mask_augment],axis=0)
train_label=np.concatenate([train_label, label_augment],axis=0)
lat_m_train = np.concatenate([lat_m_train, lat_m_augment],axis=0)
lt_m_train = np.concatenate([lt_m_train, lt_m_augment],axis=0)
lat_s_train = np.concatenate([lat_s_train, lat_s_augment],axis=0)
lt_s_train = np.concatenate([lt_s_train, lt_s_augment],axis=0)


    
'''__________Train__________________'''
path_ = root+"ML_Dataset/train/"
[save_label(train_label[i], i,path_) for i in range(len(train_label))]
[save_traj(lat_s_train[i], lat_m_train[i], lt_s_train[i], lt_m_train[i],i,path_) for i in range(len(lat_m_train))]
[save_files(train_flux[i], train_pol[i], train_m1[i], i,path_) for i in range(len(train_flux))]


  

'''________________Test________________'''
path_ = root+ "ML_Dataset/test/"
[save_label(test_label[i], i,path_) for i in range(len(test_label))]
[save_traj(lat_s_test[i], lat_m_test[i], lt_s_test[i], lt_m_test[i],i,path_) for i in range(len(lat_m_test))]
[save_files(test_flux[i], test_pol[i], test_m1[i], i,path_) for i in range(len(test_flux))]


