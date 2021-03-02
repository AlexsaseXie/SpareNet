# Copyright (c) Microsoft Corporation.   
# Licensed under the MIT License.

import os
import cv2
import sys
import yaml
import torch
import open3d
import argparse
import pprint
from utils.misc import set_logger
from configs.base_config import cfg, cfg_from_file, cfg_update


def get_args_from_command_line():
    """
    config the parameter
    """
    parser = argparse.ArgumentParser(description="The argument parser of R2Net runner")

    # choose model
    parser.add_argument("--model", type=str, default="sparenet", help="sparenet, atlasnet, msn, grnet")

    # choose test mode
    parser.add_argument("--test_mode", dest="default", help="default vis render kitti", type=str)

    # choose load model
    parser.add_argument("--weights", dest="weights", help="Initialize network from the weights file", default=None)

    # setup gpu
    parser.add_argument("--gpu", dest="gpu_id", help="GPU device to use", default="0", type=str)

    # setup workdir
    parser.add_argument("--workdir", dest="workdir", help="where to save files", default="./output", type=str)
    return parser.parse_args()


def main():
    # update config
    args = get_args_from_command_line()
    if args.gan:
        cfg_from_file("configs/" + args.model + "_gan.yaml")
    else:
        cfg_from_file("configs/" + args.model + ".yaml")
    if args.test_mode is not None:
        cfg.TEST.mode = args.test_mode
    output_dir = cfg_update(args)

    # Set up folders for logs and checkpoints
    if not os.path.exists(cfg.DIR.logs):
        os.makedirs(cfg.DIR.logs)
    logger = set_logger(os.path.join(cfg.DIR.logs, "log.txt"))
    logger.info("save into dir: %s" % output_dir)

    # Set GPU to use
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = cfg.CONST.device

    if "WEIGHTS" not in cfg.CONST or not os.path.exists(cfg.CONST.weights):
        logger.error("Please specify the file path of checkpoint.")
        sys.exit(2)

    # Start inference process
    if args.gan:
        runners = __import__("runners."+ args.model + "_gan_runner")
        module = getattr(runners, args.model + "_gan_runner")
        model = getattr(module, args.model + "GANRunner")(cfg,logger)

    else:
        runners = __import__("runners."+ args.model + "_runner")
        module = getattr(runners, args.model + "_runner")
        model = getattr(module, args.model + "Runner")(cfg,logger)
    
    model.test()

if __name__ == "__main__":
    main()
