# Code modified from Jakob's neural volumes github
import argparse
from cloudvolume import CloudVolume
import numpy as np
import os
from tqdm import tqdm
from skimage.restoration import denoise_tv_chambolle
import torch


def main(args):

    # load cloudvolume
    cv = CloudVolume(
        args.path,
        cache=True,
        parallel=True,
    )
    mip = 0

    try:
        volume_size = cv.info["scales"][mip]["size"]
        resolution = cv.info["scales"][mip]["resolution"]
        print("Volume size: ", volume_size)
        print("Resolution: ", resolution)
    except KeyError:
        print("Double check if the neuroglancer precomputed info file contains necessary metadata.")

    output_path = "./data/{}/".format(args.name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if args.train:
        output_path = os.path.join(output_path, "train")
    else:
        output_path = os.path.join(output_path, "test")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # load dataset
    for i in tqdm(range(args.n_images)):
        download_size = [args.image_size, args.image_size, args.image_size]

        x = np.random.randint(15_000, 21_000) # assuming x,y is the high resolution axis
        y = np.random.randint(15_000, 21_000)
        z = np.random.randint(15_000, 21_000)
            
        point = [x, y, z]

        # get image
        vol = cv.download_point(tuple(point), size=tuple(download_size), mip=mip)

        if args.denoise:
            vol_denoised = denoise_tv_chambolle(vol, weight=0.1, channel_axis=-1)
            vol_denoised = np.squeeze(vol_denoised * 255.0).astype(np.uint8)
             # save numpy array to disk
            np.save(os.path.join(output_path, "{}_{}_{}_denoised.npy".format(x, y, z)), vol_denoised)
        else:
            # save numpy array to disk   
            vol = np.squeeze(vol) 
            np.save(os.path.join(output_path, "{}_{}_{}.npy".format(x, y, z)), vol)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example Script")
    parser.add_argument('--name', type=str, help='Name of dataset', required=True)
    parser.add_argument('--path', type=str, help='Path to ng precomputed file', required=True)
    parser.add_argument('--train', action="store_true", help='Whether to download training or test images')
    parser.add_argument('--anistropic_dim', type=int, help='Which dimension is anisotropic. 0-->x, 1-->y, 2-->z', default=2, required=True)
    parser.add_argument('--image_size', type=int, help='Pixel size of dataset images', default=128, required=True)
    parser.add_argument('--n_images', type=int, help='Number of images being downloaded', default=1000, required=True)
    parser.add_argument('--denoise', action="store_true", help='Whether to apply variation denoising (TV)')

    args = parser.parse_args()
    main(args)