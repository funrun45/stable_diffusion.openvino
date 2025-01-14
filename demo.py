# -- coding: utf-8 --
import argparse
import os
import json
import random
import time
from datetime import datetime
# engine
from stable_diffusion_engine import StableDiffusionEngine
# scheduler
from diffusers import LMSDiscreteScheduler, PNDMScheduler
# utils
import cv2
import numpy as np
from openvino.runtime import Core

def main(args):
    if args.seed is None:
        args.seed = random.randint(0, 2**30)
    np.random.seed(args.seed)
    if args.init_image is None:
        scheduler = LMSDiscreteScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            tensor_format="np"
        )
    else:
        scheduler = PNDMScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            skip_prk_steps=True,
            tensor_format="np"
        )
    engine = StableDiffusionEngine(
        model=args.model,
        scheduler=scheduler,
        tokenizer=args.tokenizer,
        device=args.device
    )
    today = datetime.today().strftime('%Y%m%d')
    output_folder = os.path.join('Output', today)
    os.makedirs(output_folder, exist_ok=True)
    for i in range(args.num_images):
        image = engine(
            prompt=args.prompt,
            init_image=None if args.init_image is None else cv2.imread(args.init_image),
            mask=None if args.mask is None else cv2.imread(args.mask, 0),
            strength=args.strength,
            num_inference_steps=args.num_inference_steps,
            guidance_scale=args.guidance_scale,
            eta=args.eta
        )
        
        output_name = f"{os.path.join(output_folder, os.path.splitext(args.output)[0])}_{int(time.time())}_{i+1}.png"
        cv2.imwrite(output_name, image)
        print(f"Saved {output_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="bes-dev/stable-diffusion-v1-4-openvino", help="model name")
    parser.add_argument("--device", type=str, default="CPU", help=f"inference device [{', '.join(Core().available_devices)}]")
    parser.add_argument("--seed", type=int, default=None, help="random seed for generating consistent images per prompt")
    parser.add_argument("--beta-start", type=float, default=0.00085, help="LMSDiscreteScheduler::beta_start")
    parser.add_argument("--beta-end", type=float, default=0.012, help="LMSDiscreteScheduler::beta_end")
    parser.add_argument("--beta-schedule", type=str, default="scaled_linear", help="LMSDiscreteScheduler::beta_schedule")
    parser.add_argument("--num-inference-steps", type=int, default=32, help="num inference steps")
    parser.add_argument("--guidance-scale", type=float, default=7.5, help="guidance scale")
    parser.add_argument("--eta", type=float, default=0.0, help="eta")
    parser.add_argument("--tokenizer", type=str, default="openai/clip-vit-large-patch14", help="tokenizer")
    parser.add_argument("--prompt", type=str, default="Street-art painting of Emilia Clarke in style of Banksy, photorealism", help="prompt")
    parser.add_argument("--init-image", type=str, default=None, help="path to initial image")
    parser.add_argument("--strength", type=float, default=0.5, help="how strong the initial image should be noised [0.0, 1.0]")
    parser.add_argument("--mask", type=str, default=None, help="mask of the region to inpaint on the initial image")
    parser.add_argument("--output", type=str, default="output.png", help="output image base name (will have timestamp and index added)")
    parser.add_argument("--num-images", type=int, default=1, help="Number of images to generate")

    args = parser.parse_args()
    main(args)
