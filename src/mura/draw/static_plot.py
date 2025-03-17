import os
import ffmpeg
import numpy as np
from tqdm import tqdm
import matplotlib.colors as mcolors
from einops import rearrange

import jpcm
from mura.draw.color import to_div

ndiv = np.array([jpcm.maps.rurikon,jpcm.maps.aoi,jpcm.maps.sora_iro,jpcm.maps.rgb(255,255,255)]) # pretty good right now
cmap = to_div(ndiv,rot=1/3,net_rot=0.0,sat_factor=100)
# cmap = to_div(ndiv,rot=1/3+0.025/3,net_rot=-0.025,sat_factor=100)

def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

def mp4(filename, d, fps=2, triplet=True, mn = None, cmap=cmap):
    """Saves a NumPy array of frames as an MP4 video."""
 
    if d.shape[0] > 4000:
        d = d[1000:3000,...]
 
 
    if triplet:
        frames = np.stack([ d[:,0,...], d[:,0,...] + d[:,1,...],d[:,1,...]], axis=1).astype(np.float32) # x_err, xhat, x
        print(frames.shape)
        r = np.maximum(np.max(frames[:,-1], axis=(0,2,3)),-np.min(frames[:,-1],axis=(0,2,3)))[None,None,:,None,None] # B, Y, C, H, W
        nframes = frames / (2*r) + 0.5
        nframes = rearrange(nframes,'b y c h w -> b (c h) (y w)')
        print(np.max(nframes), np.min(nframes))
    else:
        assert mn is not None
        assert d.shape[1] == mn[0] * mn[1]
        frames = d
        r = np.maximum(np.max(frames, axis=(0,2,3)),-np.min(frames,axis=(0,2,3)))[None,:,None,None] # B, C, H, W
        nframes = frames / (2*r) + 0.5
        nframes = rearrange(nframes,'b (c d) h w -> b c d h w', c=mn[0], d=mn[1])
        nframes = rearrange(nframes,'b c d h w -> b (d h) (c w)')
        print(np.max(nframes), np.min(nframes))
        
    print(cmap)
    frames = cmap(nframes)[...,:3]
    frames *= 255 / np.max(frames)
    n, height, width, channels = frames.shape
    print(frames.shape)
    process = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}')
        .output(filename, pix_fmt='yuv420p', vcodec='libx264', r=fps)
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )
    for frame in frames:
        process.stdin.write(frame.astype(np.uint8).tobytes())
    process.stdin.close()
    process.wait()


if __name__ == '__main__':    

    names = ['valid','infer']
    directory = 'run/'
    remake = True #False

    print('scan directory')
    gen = fast_scandir(directory)
    for path in tqdm(gen):
        fname = os.path.join(path,'valid.mp4')
        qname = os.path.join(path,'infer.npz')
        if (not os.path.exists(fname) and os.path.exists(qname)) \
              or (os.path.exists(qname) and remake):
            print(path)
            try:
                data = [np.load(os.path.join(path,f"{x}.npz"))['arr_0'] for x in names]    
                for name, d in zip(names, data):
                    fname = os.path.join(path,f'{name}.mp4')
                    mp4(fname, d)
            except Exception as e:
                print(e)

# run this script with 
# conda activate ./sw
# source .venv/bin/activate
# python3 src/ml/runners/basic_plot.pyWW